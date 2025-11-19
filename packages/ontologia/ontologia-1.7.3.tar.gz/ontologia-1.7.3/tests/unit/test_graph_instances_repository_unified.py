import asyncio
from unittest.mock import MagicMock

from ontologia_api.repositories.graph_instances_repository import GraphInstancesRepository


class _Row:
    def __init__(self, d):
        self._d = d

    def __getitem__(self, k):
        return self._d[k]

    def get(self, k, default=None):
        return self._d.get(k, default)


class _DF:
    def __init__(self, rows):
        self._rows = [_Row(r) for r in rows]
        self.columns = list(rows[0].keys()) if rows else []
        # mimic pandas' .iloc indexer
        self.iloc = self

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, idx):
        return self._rows[idx]


class _Result:
    def __init__(self, df):
        self._df = df

    def get_as_df(self):  # noqa: D401
        return self._df


def test_list_by_interface_unified_uses_object_and_labels(monkeypatch):
    # enable unified graph
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")

    # mock kuzu repo
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    rows = [
        {
            "objectTypeApiName": "employee",
            "pkValue": "e1",
            "properties": '{"id":"e1","name":"Alice"}',
        },
        {
            "objectTypeApiName": "employee",
            "pkValue": "e2",
            "properties": '{"id":"e2","name":"Bob"}',
        },
    ]
    df = _DF(rows)
    mock_kuzu.execute.return_value = _Result(df)

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    out = repo.list_by_interface("person", limit=10, offset=0)

    # verify mapping
    assert len(out) == 2
    assert out[0]["objectTypeApiName"] == "employee"
    assert out[0]["pkValue"] == "e1"
    assert out[0]["properties"]["name"] == "Alice"

    # verify query shape
    executed = "\n".join(str(call.args[0]) for call in mock_kuzu.execute.call_args_list)
    assert "MATCH (o:Object)" in executed
    assert "IN o.labels" in executed
    assert (
        "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties"
        in executed
    )


def test_get_by_pk_prefers_unified_query(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    df = _DF(
        [
            {
                "objectTypeApiName": "employee",
                "pkValue": "e1",
                "properties": '{"id":"e1","name":"Alice"}',
            }
        ]
    )
    mock_kuzu.execute.return_value = _Result(df)

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    result = asyncio.run(repo.get_by_pk("employee", "id", "e1"))

    assert result is not None
    assert result["pkValue"] == "e1"
    assert result["properties"]["name"] == "Alice"
    executed = mock_kuzu.execute.call_args[0][0]
    assert "objectTypeApiName = $objectType" in executed
    assert mock_kuzu.execute.call_count == 1


def test_get_by_pk_falls_back_to_label_query(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.side_effect = [
        _Result(_DF([])),
        _Result(
            _DF(
                [
                    {
                        "pkValue": None,
                        "properties": '{"id":"e1","name":"Bob"}',
                    }
                ]
            )
        ),
    ]

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    result = asyncio.run(repo.get_by_pk("employee", "id", "e1"))

    assert result is not None
    assert result["properties"]["name"] == "Bob"
    assert mock_kuzu.execute.call_count == 2
    fallback_query = mock_kuzu.execute.call_args_list[1][0][0]
    assert "MATCH (o:employee)" in fallback_query
    assert "o.id = $pkValue" in fallback_query


def test_list_by_type_returns_payload(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "objectTypeApiName": "employee",
                    "pkValue": "e1",
                    "properties": '{"id":"e1"}',
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    rows = repo.list_by_type("employee", limit=5, offset=0)

    assert len(rows) == 1
    assert rows[0]["objectTypeApiName"] == "employee"
    assert rows[0]["pkValue"] == "e1"


def test_get_linked_objects_inverse_uses_incoming_pattern(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "anchorType": "company",
                    "anchorPk": "c1",
                    "neighborType": "employee",
                    "neighborPk": "e2",
                    "neighborProperties": '{"id":"e2","name":"Eve"}',
                    "edgeProperties": '{"since":"2020"}',
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    rows = repo.get_linked_objects(
        from_label="company",
        from_pk_field="id",
        from_pk_value="c1",
        link_label="works_for",
        to_label="employee",
        direction="inverse",
        limit=10,
        offset=0,
    )

    assert len(rows) == 1
    assert rows[0]["pkValue"] == "e2"
    assert rows[0]["linkProperties"]["since"] == "2020"
    query = mock_kuzu.execute.call_args[0][0]
    assert "MATCH (anchor:Object)<-[r:works_for]-(neighbor:Object)" in query


def test_get_linked_objects_forward_includes_link_metadata(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "anchorType": "employee",
                    "anchorPk": "e1",
                    "neighborType": "company",
                    "neighborPk": "c1",
                    "neighborProperties": '{"id":"c1","name":"ACME"}',
                    "edgeProperties": '{"since":"2021"}',
                    "edgeRid": "edge-123",
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    rows = repo.get_linked_objects(
        from_label="employee",
        from_pk_field="id",
        from_pk_value="e1",
        link_label="works_for",
        to_label="company",
        direction="forward",
        limit=10,
        offset=0,
    )

    assert len(rows) == 1
    payload = rows[0]
    assert payload["objectTypeApiName"] == "company"
    assert payload["pkValue"] == "c1"
    assert payload["fromPk"] == "e1"
    assert payload["toPk"] == "c1"
    assert payload["linkProperties"]["since"] == "2021"
    assert payload["linkRid"] == "edge-123"


def test_get_linked_objects_inverse_swaps_from_to(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "anchorType": "company",
                    "anchorPk": "c1",
                    "neighborType": "employee",
                    "neighborPk": "e2",
                    "neighborProperties": '{"id":"e2"}',
                    "edgeProperties": '{"role":"dev"}',
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    rows = repo.get_linked_objects(
        from_label="company",
        from_pk_field="id",
        from_pk_value="c1",
        link_label="works_for",
        to_label="employee",
        direction="inverse",
        limit=10,
        offset=0,
    )

    payload = rows[0]
    assert payload["fromPk"] == "e2"
    assert payload["toPk"] == "c1"
    assert payload["objectTypeApiName"] == "employee"


def test_list_edges_unified(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "fromObjectType": "employee",
                    "fromPk": "e1",
                    "toObjectType": "company",
                    "toPk": "c1",
                    "properties": '{"valid_from":"2024-01-01"}',
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    edges = repo.list_edges(
        "works_for",
        "employee",
        "company",
        "id",
        "id",
        limit=5,
        offset=0,
    )

    assert len(edges) == 1
    assert edges[0]["fromPk"] == "e1"
    assert edges[0]["toPk"] == "c1"
    assert edges[0]["properties"]["valid_from"] == "2024-01-01"
    query = mock_kuzu.execute.call_args[0][0]
    assert "MATCH (source:Object)-[rel:works_for]->(target:Object)" in query


def test_list_edges_fallback(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.side_effect = [
        _Result(_DF([])),
        _Result(
            _DF(
                [
                    {
                        "fromPk": "e1",
                        "toPk": "c1",
                        "properties": '{"valid_from":"2024-01-01"}',
                    }
                ]
            )
        ),
    ]

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    edges = repo.list_edges(
        "works_for",
        "employee",
        "company",
        "id",
        "id",
        limit=5,
        offset=0,
    )

    assert len(edges) == 1
    assert mock_kuzu.execute.call_count == 2
    fallback_query = mock_kuzu.execute.call_args_list[1][0][0]
    assert "MATCH (source:employee)-[rel:works_for]->(target:company)" in fallback_query


def test_list_edges_property_filter(monkeypatch):
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    mock_kuzu.execute.return_value = _Result(
        _DF(
            [
                {
                    "fromObjectType": "employee",
                    "fromPk": "e1",
                    "toObjectType": "company",
                    "toPk": "c1",
                    "properties": '{"score":0.9,"meta":"x"}',
                }
            ]
        )
    )

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    edges = repo.list_edges(
        "works_for",
        "employee",
        "company",
        "id",
        "id",
        limit=5,
        offset=0,
        property_names=("score",),
    )

    assert edges[0]["properties"] == {"score": 0.9}
