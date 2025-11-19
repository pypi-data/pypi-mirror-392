from fastapi.testclient import TestClient
from ontologia_api.services.linked_objects_service import LinkedObjectsService


class FakeGraphLinkedRepo:
    def is_available(self) -> bool:
        return True

    def list_edges(
        self,
        link_type_api_name: str,
        from_label: str,
        to_label: str,
        from_pk_field: str,
        to_pk_field: str,
        *,
        limit: int = 100,
        offset: int = 0,
        property_names: list[str] | None = None,
    ):
        return [
            {"fromPk": "e1", "toPk": "c1"},
            {"fromPk": "e2", "toPk": "c1"},
        ]


class FakeGraphLinkedRepoWithGetter(FakeGraphLinkedRepo):
    def get_linked_objects(
        self,
        from_label,
        from_pk_field,
        from_pk_value,
        link_label,
        to_label,
        direction,
        limit,
        offset,
    ):
        return [
            {
                "fromObjectType": "employee",
                "toObjectType": "company",
                "fromPk": "e1",
                "toPk": "c1",
                "linkProperties": {"since": "2024-01-01"},
                "linkRid": "edge-1",
            }
        ]


def _setup_types_and_link(client: TestClient):
    # Create OTs
    for ot_name in ("employee", "company"):
        resp = client.put(
            f"/v2/ontologies/default/objectTypes/{ot_name}",
            json={
                "displayName": ot_name.title(),
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        assert resp.status_code == 200, resp.text

    # Create LinkType MANY_TO_ONE: employee -> company
    resp_link = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert resp_link.status_code == 200, resp_link.text


def test_graph_reads_list_links(client: TestClient, session, monkeypatch):
    # Enable graph reads
    monkeypatch.setenv("USE_GRAPH_READS", "1")

    _setup_types_and_link(client)

    svc = LinkedObjectsService(
        session,
        service="ontology",
        instance="default",
        graph_repo=FakeGraphLinkedRepo(),
    )

    # list_links via graph (no data in SQLModel needed)
    lst = svc.list_links("works_for")
    assert len(lst.data) == 2
    pairs = {(it.fromPk, it.toPk) for it in lst.data}  # type: ignore[attr-defined]
    assert pairs == {("e1", "c1"), ("e2", "c1")}


def test_graph_reads_respects_from_pk_filter(client: TestClient, session, monkeypatch):
    monkeypatch.setenv("USE_GRAPH_READS", "1")

    _setup_types_and_link(client)

    svc = LinkedObjectsService(
        session,
        service="ontology",
        instance="default",
        graph_repo=FakeGraphLinkedRepoWithGetter(),
    )

    lst = svc.list_links("works_for", from_pk="e1")
    assert len(lst.data) == 1
    item = lst.data[0]
    assert item.fromPk == "e1"
    assert item.toPk == "c1"
    assert item.linkProperties["since"] == "2024-01-01"  # type: ignore[index]
