"""
services/actions_service.py
---------------------------
Business service to orchestrate Action execution and discovery.

Responsibilities:
- Load ActionType definitions from metamodel (control plane)
- Fetch target object
- Evaluate submission criteria safely
- Validate parameters against ActionType.parameters
- Resolve and execute registered executor function
- Manage transaction commit/rollback
"""

from __future__ import annotations

import ast
import datetime as dt
import inspect
import logging
from collections.abc import Mapping
from typing import Any, cast
from uuid import uuid4

from fastapi import HTTPException, status
from sqlmodel import Session

logger = logging.getLogger(__name__)

from ontologia.actions.exceptions import ActionValidationError
from ontologia.actions.registry import ACTION_REGISTRY
from ontologia.application.settings import get_settings
from ontologia.domain.metamodels.instances.dtos import ObjectInstanceDTO
from ontologia.domain.metamodels.types.action_execution_log import ActionExecutionLog
from ontologia.domain.metamodels.types.action_type import ActionType
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)
from ontologia.ogm.connection import CoreServiceProvider

# Best-effort: import built-in actions so registry has defaults in tests/dev
for _module in (
    "ontologia.actions.test_actions",
    "ontologia.actions.system_actions",
):
    try:  # pragma: no cover - optional convenience
        __import__(_module)
    except Exception as exc:  # pragma: no cover - ignore if unavailable
        logger.debug("Failed to preload action module %s", _module, exc_info=exc)


class ActionsService:
    def __init__(
        self,
        session: Session,
        service: str = "api",
        instance: str = "default",
        *,
        temporal_client: Any | None = None,
        principal: Any | None = None,
    ):
        logger.debug(
            "ActionsService init session id=%s class=%s obj=%s",
            id(session),
            session.__class__,
            session,
        )
        self.session = session
        logger.debug("ActionsService stored session id=%s obj=%s", id(self.session), self.session)
        self.service = service
        self.instance = instance
        logger.debug("Before SQLMetamodelRepository, session id=%s", id(session))
        self.repo = SQLMetamodelRepository(session)
        logger.debug("After SQLMetamodelRepository, session id=%s", id(session))
        logger.debug("Before CoreServiceProvider, session id=%s", id(session))
        provider = CoreServiceProvider(session)
        logger.debug("After CoreServiceProvider, session id=%s", id(session))
        self.instances = provider.instances_service()
        # Optional injected Temporal client (lifespan-managed)
        self.temporal_client = temporal_client
        self.principal = principal

    # ---------- Public API ----------

    def list_available_actions(
        self, object_type_api_name: str, pk_value: str, *, context: dict[str, Any] | None = None
    ) -> list[ActionType]:
        target = self._get_target(object_type_api_name, pk_value)
        items = self.repo.list_action_types_for_object_type(
            self.service, self.instance, target.object_type_api_name
        )
        latest: dict[str, ActionType] = {}
        for act in items:
            if not getattr(act, "is_latest", True):
                continue
            name = getattr(act, "api_name", None)
            ver = getattr(act, "version", 1)
            if name is None:
                continue
            prev = latest.get(name)
            if prev is None or int(getattr(prev, "version", 1)) < int(ver):
                latest[name] = act
        out: list[ActionType] = []
        for act in latest.values():
            if self._passes_submission_criteria(act, target, None, context):
                out.append(act)
        return out

    def execute_action(
        self,
        object_type_api_name: str,
        pk_value: str,
        action_api_name: str,
        params: dict[str, Any],
        *,
        user: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # 1) Definition
        act = self.repo.get_action_type_by_api_name(self.service, self.instance, action_api_name)
        if not act:
            raise HTTPException(status_code=404, detail="ActionType not found")
        # target must match
        if act.target_object_type_api_name != object_type_api_name:
            raise HTTPException(
                status_code=400,
                detail=f"Action '{action_api_name}' does not apply to ObjectType '{object_type_api_name}'",
            )

        # 2) Target object
        target = self._get_target(object_type_api_name, pk_value)

        # 3) Submission criteria
        # Build execution context (user may be None)
        user_ctx = user if user is not None else {"id": "anonymous", "role": "user"}
        exec_context: dict[str, Any] = {"user": user_ctx}
        if not self._passes_submission_criteria(act, target, params, exec_context):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Action not available"
            )

        # 4) Parameter validation
        self._validate_params(act, params)
        self._run_validation_rules(act, target, params, exec_context)

        # 5) Resolve executor
        func = ACTION_REGISTRY.get(act.executor_key)
        if not func:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Action not implemented"
            )

        # 6) Execute with transaction
        context = {
            "target_object": target,
            "session": self.session,
            "user": user_ctx,
            # Future: "headers": ...
        }
        started_at = dt.datetime.now(dt.UTC)
        try:
            if self.session.in_transaction():
                # Ensure executor receives a clean transaction boundary
                try:
                    logger.debug("Committing session before executor")
                    self.session.commit()
                    logger.debug("Session committed before executor")
                except Exception:
                    logger.debug("Rolling back session before executor")
                    self.session.rollback()
                    logger.debug("Session rolled back before executor")
                    raise
            result = func(context, params)
            logger.debug("Committing session after executor")
            self.session.commit()
            logger.debug("Session committed after executor")
            # Audit success (best-effort)
            finished_at = dt.datetime.now(dt.UTC)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            try:
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="success",
                    error_message=None,
                    parameters=dict(params or {}),
                    result=result if isinstance(result, dict) else {"value": result},
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                # do not fail the action on audit error
                pass
            return result if isinstance(result, dict) else {"status": "success", "result": result}
        except ActionValidationError as e:
            self.session.rollback()
            # Audit failure (best-effort)
            try:
                finished_at = dt.datetime.now(dt.UTC)
                duration_ms = int((finished_at - started_at).total_seconds() * 1000)
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name if "act" in locals() and act else action_api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="error",
                    error_message=str(e),
                    parameters=dict(params or {}),
                    result=None,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                pass
            raise HTTPException(status_code=e.http_status, detail=e.to_http_detail()) from e
        except Exception as e:
            self.session.rollback()
            # Audit failure (best-effort)
            try:
                finished_at = dt.datetime.now(dt.UTC)
                duration_ms = int((finished_at - started_at).total_seconds() * 1000)
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name if "act" in locals() and act else action_api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="error",
                    error_message=str(e),
                    parameters=dict(params or {}),
                    result=None,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def execute_action_async(
        self,
        object_type_api_name: str,
        pk_value: str,
        action_api_name: str,
        params: dict[str, Any],
        *,
        user: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an Action via Temporal workflow. Mirrors validations from the sync path
        and awaits the result from the worker. Leaves the synchronous method untouched
        for default behavior when USE_TEMPORAL_ACTIONS=0.
        """
        # 1) Definition
        act = self.repo.get_action_type_by_api_name(self.service, self.instance, action_api_name)
        if not act:
            raise HTTPException(status_code=404, detail="ActionType not found")
        if act.target_object_type_api_name != object_type_api_name:
            raise HTTPException(
                status_code=400,
                detail=f"Action '{action_api_name}' does not apply to ObjectType '{object_type_api_name}'",
            )

        # 2) Target object
        target = self._get_target(object_type_api_name, pk_value)

        # 3) Submission criteria
        user_ctx = user if user is not None else {"id": "anonymous", "role": "user"}
        exec_context: dict[str, Any] = {"user": user_ctx}
        if not self._passes_submission_criteria(act, target, params, exec_context):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Action not available"
            )

        # 4) Parameter validation
        self._validate_params(act, params)
        self._run_validation_rules(act, target, params, exec_context)

        # 5) Temporal client and workflow execution
        # Prepare context for the Activity (no DB session over the wire)
        activity_context: dict[str, Any] = {
            "target_object": target,
            "user": user_ctx,
        }
        started_at = dt.datetime.now(dt.UTC)
        try:
            # Use injected client when available; fallback to connecting
            client = self.temporal_client
            settings = get_settings()
            task_queue = settings.temporal_task_queue
            if client is None:
                from temporalio.client import Client  # type: ignore[unresolved-import]

                client = await Client.connect(
                    settings.temporal_address, namespace=settings.temporal_namespace
                )
            # Provide a unique workflow id per request
            wf_id = f"action-{self.service}-{self.instance}-{act.api_name}-{uuid4().hex}"
            result = await client.execute_workflow(
                "ActionWorkflow",
                args=[act.executor_key, activity_context, dict(params or {})],
                id=wf_id,
                task_queue=task_queue,
            )

            # 6) Audit success (best-effort)
            finished_at = dt.datetime.now(dt.UTC)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            try:
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="success",
                    error_message=None,
                    parameters=dict(params or {}),
                    result=result if isinstance(result, dict) else {"value": result},
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                pass
            return result if isinstance(result, dict) else {"status": "success", "result": result}
        except ActionValidationError as e:  # pragma: no cover - symmetry with sync path
            self.session.rollback()
            try:
                finished_at = dt.datetime.now(dt.UTC)
                duration_ms = int((finished_at - started_at).total_seconds() * 1000)
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name if "act" in locals() and act else action_api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="error",
                    error_message=str(e),
                    parameters=dict(params or {}),
                    result=None,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                pass
            raise HTTPException(status_code=e.http_status, detail=e.to_http_detail()) from e
        except Exception as e:
            self.session.rollback()
            try:
                finished_at = dt.datetime.now(dt.UTC)
                duration_ms = int((finished_at - started_at).total_seconds() * 1000)
                audit = ActionExecutionLog(
                    service=self.service,
                    instance=self.instance,
                    action_api_name=act.api_name if "act" in locals() and act else action_api_name,
                    target_object_type_api_name=object_type_api_name,
                    target_pk=pk_value,
                    status="error",
                    error_message=str(e),
                    parameters=dict(params or {}),
                    result=None,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                self.session.add(audit)
                self.session.commit()
            except Exception:
                pass
            raise HTTPException(status_code=502, detail=f"Temporal error: {e}") from e

    async def start_action_async(
        self,
        object_type_api_name: str,
        pk_value: str,
        action_api_name: str,
        params: dict[str, Any],
        *,
        user: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Fire-and-forget start: validate, then start a Temporal workflow and return identifiers.
        Does not await the result. Intended for long-running actions and polling via workflow id.
        """
        # 1) Definition
        act = self.repo.get_action_type_by_api_name(self.service, self.instance, action_api_name)
        if not act:
            raise HTTPException(status_code=404, detail="ActionType not found")
        if act.target_object_type_api_name != object_type_api_name:
            raise HTTPException(
                status_code=400,
                detail=f"Action '{action_api_name}' does not apply to ObjectType '{object_type_api_name}'",
            )

        # 2) Target object
        target = self._get_target(object_type_api_name, pk_value)

        # 3) Submission criteria
        user_ctx = user if user is not None else {"id": "anonymous", "role": "user"}
        exec_context: dict[str, Any] = {"user": user_ctx}
        if not self._passes_submission_criteria(act, target, params, exec_context):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Action not available"
            )

        # 4) Parameter validation
        self._validate_params(act, params)
        self._run_validation_rules(act, target, params, exec_context)

        # 5) Start Workflow
        # Idempotency: check by key (if provided)
        if idempotency_key:
            from sqlmodel import select

            existing = self.session.exec(
                select(ActionExecutionLog)
                .where(ActionExecutionLog.service == self.service)
                .where(ActionExecutionLog.instance == self.instance)
                .where(ActionExecutionLog.action_api_name == act.api_name)
                .where(ActionExecutionLog.target_object_type_api_name == object_type_api_name)
                .where(ActionExecutionLog.target_pk == pk_value)
                .where(ActionExecutionLog.idempotency_key == idempotency_key)
            ).first()
            if existing and existing.result:
                # Return previously created identifiers
                out = dict(existing.result or {})
                if existing.workflow_id and "workflowId" not in out:
                    out["workflowId"] = existing.workflow_id
                if existing.run_id and "runId" not in out:
                    out["runId"] = existing.run_id
                return {"status": "started", **out}

        # Use injected client when available; fallback to connecting
        client = self.temporal_client
        settings = get_settings()
        task_queue = settings.temporal_task_queue
        if client is None:
            from temporalio.client import Client  # type: ignore[unresolved-import]

            client = await Client.connect(
                settings.temporal_address, namespace=settings.temporal_namespace
            )
        wf_id = f"action-{self.service}-{self.instance}-{act.api_name}-{uuid4().hex}"
        activity_context: dict[str, Any] = {
            "target_object": target,
            "user": user_ctx,
        }
        handle = await client.start_workflow(
            "ActionWorkflow",
            args=[act.executor_key, activity_context, dict(params or {})],
            id=wf_id,
            task_queue=task_queue,
        )
        # Return identifiers for client-side tracking
        run_id = getattr(handle, "run_id", None)

        # Best-effort audit row for initiation
        started_at = dt.datetime.now(dt.UTC)
        try:
            audit = ActionExecutionLog(
                service=self.service,
                instance=self.instance,
                action_api_name=act.api_name,
                target_object_type_api_name=object_type_api_name,
                target_pk=pk_value,
                status="started",
                error_message=None,
                parameters=dict(params or {}),
                result={"workflowId": wf_id, "runId": run_id},
                started_at=started_at,
                finished_at=started_at,
                duration_ms=0,
                idempotency_key=idempotency_key,
                workflow_id=wf_id,
                run_id=run_id,
            )
            self.session.add(audit)
            self.session.commit()
        except Exception:
            pass

        return {"workflowId": wf_id, "runId": run_id}

    async def get_action_status(
        self, workflow_id: str, run_id: str | None = None
    ) -> dict[str, Any]:
        """Retrieve Temporal workflow status by id/run id.

        Returns a dict with at least: workflowId, runId (if available), status.
        """
        settings = get_settings()
        client = self.temporal_client
        if client is None:
            from temporalio.client import Client  # type: ignore[unresolved-import]

            client = await Client.connect(
                settings.temporal_address, namespace=settings.temporal_namespace
            )
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)
        status: str = "unknown"
        current_run_id = getattr(handle, "run_id", run_id)
        try:
            if hasattr(handle, "describe"):
                desc = handle.describe
                if inspect.iscoroutinefunction(desc):
                    info = await desc()  # type: ignore[misc]
                else:
                    info = desc()  # type: ignore[misc]
                # info may be a dict-like object in tests; best-effort extraction
                if isinstance(info, Mapping):
                    info_mapping = cast(Mapping[str, Any], info)
                    run_candidate = info_mapping.get("run_id")
                    if run_candidate is not None:
                        current_run_id = cast(str | None, run_candidate)
                    status_value = info_mapping.get("status")
                    if status_value is not None:
                        status = str(status_value)
                else:
                    # Fallback to string repr
                    status = str(getattr(info, "status", status))
                    current_run_id = getattr(info, "run_id", current_run_id)
        except Exception:
            # Keep best-effort defaults on errors
            pass

        return {"workflowId": workflow_id, "runId": current_run_id, "status": status}

    async def cancel_action_run(
        self, workflow_id: str, run_id: str | None = None
    ) -> dict[str, Any]:
        """Cancel a Temporal workflow run by id/run id.

        Returns a dict with workflowId, runId and status 'canceled' on success.
        """
        from temporalio.client import Client  # type: ignore[unresolved-import]

        settings = get_settings()
        client = await Client.connect(
            settings.temporal_address, namespace=settings.temporal_namespace
        )
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)
        current_run_id = getattr(handle, "run_id", run_id)
        try:
            # Prefer cancel over terminate; cancel allows workflow cleanup
            if hasattr(handle, "cancel"):
                cancel = handle.cancel
                if inspect.iscoroutinefunction(cancel):
                    await cancel()  # type: ignore[misc]
                else:
                    cancel()  # type: ignore[misc]
            else:
                # Fallback: terminate when cancel is not available
                term = getattr(handle, "terminate", None)
                if term:
                    if inspect.iscoroutinefunction(term):
                        await term(reason="user-requested")  # type: ignore[misc]
                    else:
                        term(reason="user-requested")  # type: ignore[misc]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cancel failed: {e}") from e
        return {"workflowId": workflow_id, "runId": current_run_id, "status": "canceled"}

    # ---------- Internals ----------

    def _get_target(self, object_type_api_name: str, pk_value: str) -> ObjectInstanceDTO:
        getter = getattr(self.instances, "get_object_dto", None)
        if getter is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="InstancesService does not support get_object_dto",
            )
        try:
            # Pass valid_at as keyword argument to get the latest version
            target = getter(object_type_api_name, pk_value, valid_at=dt.datetime.now(dt.UTC))
        except TypeError:
            # Fallback if signature doesn't support valid_at
            target = getter(object_type_api_name, pk_value)
        if not target:
            raise HTTPException(status_code=404, detail="Target object not found")
        return target

    def _passes_submission_criteria(
        self,
        act: ActionType,
        target: ObjectInstanceDTO,
        params: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        if not act.submission_criteria:
            return True
        for rule in act.submission_criteria:
            rule_logic = None
            if isinstance(rule, dict):
                rule_logic = rule.get("rule_logic") or rule.get("ruleLogic")
            else:
                rule_logic = getattr(rule, "rule_logic", None) or getattr(rule, "ruleLogic", None)
            if not rule_logic:
                # empty or invalid rule defaults to False (not available)
                return False
            result = self._safe_rule_eval(str(rule_logic), target, params or {}, context)
            if not result:
                return False
        return True

    def _run_validation_rules(
        self,
        act: ActionType,
        target: ObjectInstanceDTO,
        params: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> None:
        for rule in act.validation_rules or []:
            rule_logic = None
            if isinstance(rule, dict):
                rule_logic = rule.get("rule_logic") or rule.get("ruleLogic")
            else:
                rule_logic = getattr(rule, "rule_logic", None) or getattr(rule, "ruleLogic", None)
            if not rule_logic:
                # skip invalid rules silently
                continue
            ok = self._safe_rule_eval(str(rule_logic), target, params, context)
            if not ok:
                desc = (rule or {}).get("description") if isinstance(rule, dict) else None
                raise HTTPException(status_code=400, detail=f"Validation failed: {desc or 'rule'}")

    def _validate_params(self, act: ActionType, params: dict[str, Any]) -> None:
        errors: list[dict[str, str]] = []
        # Required
        for name, spec in (act.parameters or {}).items():
            required = True
            if isinstance(spec, dict):
                required = bool(spec.get("required", True))
            if required and name not in params:
                errors.append(
                    {"field": name, "code": "required", "message": "Missing required parameter"}
                )
        # Types (best-effort)
        for name, value in list(params.items()):
            spec = (act.parameters or {}).get(name)
            if not spec:
                continue
            dt = spec.get("dataType") if isinstance(spec, dict) else None
            if dt == "string":
                if value is not None and not isinstance(value, str):
                    params[name] = str(value)
            elif dt == "integer":
                try:
                    params[name] = int(value)
                except Exception:
                    errors.append(
                        {"field": name, "code": "type_error.integer", "message": "Must be integer"}
                    )
            elif dt == "double":
                try:
                    params[name] = float(value)
                except Exception:
                    errors.append(
                        {"field": name, "code": "type_error.double", "message": "Must be double"}
                    )
            elif dt == "boolean":
                if isinstance(value, bool):
                    continue
                if isinstance(value, str) and value.lower() in ("true", "false", "1", "0"):
                    params[name] = value.lower() in ("true", "1")
                else:
                    errors.append(
                        {"field": name, "code": "type_error.boolean", "message": "Must be boolean"}
                    )
            elif dt in ("date", "timestamp"):
                # Keep as string; parsing is domain-specific and can be handled in executor
                if value is not None and not isinstance(value, str):
                    params[name] = str(value)
        if errors:
            raise HTTPException(
                status_code=400, detail={"message": "Invalid parameters", "errors": errors}
            )

    # ---- Safe rule evaluation (restricted AST) ----

    def _safe_rule_eval(
        self,
        expr: str,
        target: ObjectInstanceDTO,
        params: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Evaluate a boolean expression safely with a restricted AST.
        Allowed constructs:
          - names: params, context, target_object
          - dict subscripts: x['key']
          - attribute access on target_object.properties
          - bool ops: and/or/not
          - comparisons: ==, !=, <, <=, >, >=, in, not in
          - constants: str, int, float, bool, None
        """
        try:
            tree = ast.parse(expr, mode="eval")
        except Exception:
            return False

        def eval_node(node, env):
            if isinstance(node, ast.Expression):
                return eval_node(node.body, env)
            if isinstance(node, ast.BoolOp):
                vals = [eval_node(v, env) for v in node.values]
                if any(v is _unsafe for v in vals):
                    return _unsafe
                if isinstance(node.op, ast.And):
                    return all(bool(v) for v in vals)
                if isinstance(node.op, ast.Or):
                    return any(bool(v) for v in vals)
                return _unsafe
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                v = eval_node(node.operand, env)
                return not bool(v)
            if isinstance(node, ast.Compare):
                left = eval_node(node.left, env)
                if left is _unsafe:
                    return _unsafe
                for op, comparator in zip(node.ops, node.comparators, strict=False):
                    right = eval_node(comparator, env)
                    if right is _unsafe:
                        return _unsafe
                    if isinstance(op, ast.Eq):
                        ok = left == right
                    elif isinstance(op, ast.NotEq):
                        ok = left != right
                    elif isinstance(op, ast.Lt):
                        ok = left < right
                    elif isinstance(op, ast.LtE):
                        ok = left <= right
                    elif isinstance(op, ast.Gt):
                        ok = left > right
                    elif isinstance(op, ast.GtE):
                        ok = left >= right
                    elif isinstance(op, ast.In):
                        ok = left in right
                    elif isinstance(op, ast.NotIn):
                        ok = left not in right
                    else:
                        return _unsafe
                    if not ok:
                        return False
                    left = right
                return True
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Name):
                if node.id == "params":
                    return env["params"]
                if node.id == "target_object":
                    return env["target_object"]
                if node.id == "context":
                    return env["context"]
                return _unsafe
            if isinstance(node, ast.Subscript):
                base = eval_node(node.value, env)
                key = (
                    eval_node(node.slice, env) if not isinstance(node.slice, ast.Slice) else _unsafe
                )
                if base is _unsafe or key is _unsafe:
                    return _unsafe
                try:
                    return base[key]
                except Exception:
                    return _unsafe
            if isinstance(node, ast.Attribute):
                # allow target_object.properties
                obj = eval_node(node.value, env)
                if obj is _unsafe:
                    return _unsafe
                if obj is env.get("target_object") and node.attr == "properties":
                    return env["target_object"]["properties"]
                return _unsafe
            # Disallow calls, comprehensions, lambdas, etc.
            return _unsafe

        _unsafe = object()
        env = {
            "params": dict(params or {}),
            "context": dict(context or {}),
            "target_object": {
                "properties": dict(target.data or {}),
                "pkValue": target.pk_value,
                "objectType": target.object_type_api_name,
            },
        }
        try:
            val = eval_node(tree, env)
            return bool(val) if val is not _unsafe else False
        except Exception:
            return False
