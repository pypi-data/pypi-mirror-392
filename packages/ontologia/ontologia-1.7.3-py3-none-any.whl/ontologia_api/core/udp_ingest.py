from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class UDPConfig:
    host: str = "0.0.0.0"
    port: int = 19091
    enabled: bool = False


def load_udp_config() -> UDPConfig:
    enabled = os.getenv("EDGE_UDP_ENABLED", "0") in {"1", "true", "True"}
    host = os.getenv("EDGE_UDP_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("EDGE_UDP_PORT", "19091"))
    except ValueError:
        port = 19091
    return UDPConfig(host=host, port=port, enabled=enabled)


class _UDPHandler(asyncio.DatagramProtocol):
    def __init__(self) -> None:
        super().__init__()
        # Lazy imports to avoid circular deps on module import
        from sqlmodel import Session

        from ontologia.edge import EdgeCommand  # noqa: F401 - future use
        from ontologia_api.core.database import engine
        from ontologia_api.core.edge_canonical import canonicalize
        from ontologia_api.core.edge_dedup import get_dedup_backend
        from ontologia_api.core.edge_models import EdgeEvent, EdgeHello
        from ontologia_api.core.edge_ratelimit import rate_limit
        from ontologia_api.core.edge_security import SignatureVerifier
        from ontologia_api.dependencies.realtime import get_entity_manager
        from ontologia_api.repositories.edge_repository import upsert_edge_node

        self.EdgeEvent = EdgeEvent
        self.EdgeHello = EdgeHello
        self._verify = SignatureVerifier()
        self._dedup = get_dedup_backend()
        self._rate_limit = rate_limit
        self._canonicalize = canonicalize
        self._get_entity_manager = get_entity_manager
        self._Session = Session
        self._engine = engine
        self._upsert_edge_node = upsert_edge_node

    def datagram_received(self, data: bytes, addr) -> None:  # type: ignore[override]
        try:
            payload: dict[str, Any] | None = None
            # Try CBOR first
            try:
                import cbor2  # type: ignore

                payload = cbor2.loads(data)
            except Exception:
                try:
                    payload = json.loads(data.decode("utf-8"))
                except Exception:
                    payload = None
            if not isinstance(payload, dict):
                return
            asyncio.get_event_loop().create_task(self._process(payload))
        except Exception:  # pragma: no cover - defensive
            logger.exception("UDP ingest error from %s", addr)

    async def _process(self, payload: dict[str, Any]) -> None:
        # Token check (UDP payload must include token if configured)
        token_expected = os.getenv("EDGE_SHARED_TOKEN")
        if token_expected:
            got = str(payload.get("token") or "")
            if got != token_expected:
                return

        ptype = str(payload.get("type") or "").upper()
        node_id = str(payload.get("node_id") or "")
        msg_id = str(payload.get("msg_id") or "")
        ttl = payload.get("ttl")

        # Rate limit
        if ptype in {"EVENT", "HELLO"}:
            ok_rl = await self._rate_limit(
                f"udp:{ptype.lower()}:{node_id}",
                prefix="UDP",
                default_capacity=120,
                default_window=60,
            )
            if not ok_rl:
                return

        # Dedup
        try:
            if not await self._dedup.is_new(msg_id, node_id=node_id, ttl=ttl):
                return
        except Exception:
            pass

        if ptype == "HELLO":
            await self._handle_hello(payload)
        elif ptype == "EVENT":
            await self._handle_event(payload)
        else:
            return

    async def _handle_hello(self, payload: dict[str, Any]) -> None:
        # Minimal HELLO processing: upsert node + verify signature
        try:
            hello = self.EdgeHello(**payload)
        except Exception:
            return
        algo = None
        caps = hello.capabilities or {}
        crypto = caps.get("crypto") if isinstance(caps, dict) else None
        if isinstance(crypto, dict):
            algo = crypto.get("algo")
        canonical = None
        if isinstance(crypto, dict):
            canonical = crypto.get("canonical")
        ok = await self._verify.verify(
            hello.node_id,
            self._canonicalize(hello.model_dump(mode="json"), mode=(canonical or "json")),
            hello.signature,
            algo=algo,
        )
        if not ok:
            return
        try:
            with self._Session(self._engine) as session:
                self._upsert_edge_node(
                    session,
                    node_id=hello.node_id,
                    public_key=hello.public_key,
                    capabilities=hello.capabilities,
                    software=hello.software,
                    hw=hello.hw,
                )
        except Exception:
            logger.exception("UDP HELLO upsert failed")

    async def _handle_event(self, payload: dict[str, Any]) -> None:
        try:
            event = self.EdgeEvent(**payload)
        except Exception:
            return
        # Verify signature with node defaults if possible (algo may be missing; verifier falls back)
        ok = await self._verify.verify(
            event.node_id,
            self._canonicalize(event.model_dump(mode="json"), mode="json"),
            event.signature,
        )
        if not ok:
            return
        manager = self._get_entity_manager()
        components = event.to_components()
        try:
            await manager.upsert(
                event.subject or f"{event.node_id}:{event.ont_type}",
                object_type=event.ont_type,
                provenance=event.node_id,
                ttl=__import__("datetime").timedelta(seconds=(event.ttl or 30)),
                components=components,
                metadata={
                    **(event.metadata or {}),
                    "predicate": event.predicate,
                    "unit": event.unit,
                    "origin": event.node_id,
                    "msg_id": event.msg_id,
                },
            )
        except Exception:
            logger.exception("UDP EVENT upsert failed")


async def start_udp_server() -> asyncio.DatagramTransport | None:
    cfg = load_udp_config()
    if not cfg.enabled:
        return None
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(_UDPHandler, local_addr=(cfg.host, cfg.port))
    logger.info("UDP ingest listening on %s:%s", cfg.host, cfg.port)
    return transport
