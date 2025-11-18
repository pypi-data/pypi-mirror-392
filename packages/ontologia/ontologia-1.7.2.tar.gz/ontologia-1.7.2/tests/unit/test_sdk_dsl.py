from ontologia_sdk.link_proxy import LinkDescriptor
from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.query import QueryBuilder
from ontologia_sdk.testing import MockOntologyClient
from ontologia_sdk.types import Page


def test_field_descriptor_expressions():
    eq_expr = Employee.dept == "Engineering"
    filters = eq_expr.to_filters()  # type: ignore[attr-defined]
    assert filters == [
        {"property": "dept", "op": "eq", "value": "Engineering"},
    ]

    combo = (Employee.dept == "Engineering") & (Employee.name != "Bob")
    combo_filters = combo.to_filters()  # type: ignore[attr-defined]
    assert {(f["property"], f["op"], f["value"]) for f in combo_filters} == {
        ("dept", "eq", "Engineering"),
        ("name", "ne", "Bob"),
    }

    union = (Employee.dept == "Engineering") | (Employee.dept == "R&D")
    union_filters = union.to_filters()  # type: ignore[attr-defined]
    assert len(union_filters) == 1
    or_payload = union_filters[0]
    assert or_payload["op"] == "or"
    assert {f["value"] for f in or_payload["filters"]} == {"Engineering", "R&D"}


def test_query_builder_accepts_dsl():
    class StubClient:
        def __init__(self) -> None:
            self.last_payload: dict | None = None

        def search_objects(self, object_type, *, where, order_by, limit, offset):  # type: ignore[override]
            self.last_payload = {
                "object_type": object_type,
                "where": where,
                "order_by": order_by,
                "limit": limit,
                "offset": offset,
            }
            return {"data": []}

    stub = StubClient()
    qb = QueryBuilder(client=stub, object_type="employee")
    qb.where(Employee.dept == "Engineering").order_by(
        Employee.name.asc()  # type: ignore[attr-defined]
    ).limit(10).offset(5).all()

    payload = stub.last_payload  # type: ignore[attr-defined]
    assert payload is not None
    assert payload["object_type"] == "employee"  # type: ignore[index]
    assert payload["where"] == [  # type: ignore[index]
        {"property": "dept", "op": "eq", "value": "Engineering"},
    ]
    assert payload["order_by"] == [  # type: ignore[index]
        {"property": "name", "direction": "asc"},
    ]
    assert payload["limit"] == 10  # type: ignore[index]
    assert payload["offset"] == 5  # type: ignore[index]


def test_link_descriptor_binds_proxy():
    descriptor = Employee.works_for
    assert isinstance(descriptor, LinkDescriptor)
    assert descriptor.link_type == "works_for"

    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice"})
    client.upsert_object("company", "c1", {"name": "ACME"})
    emp = Employee.from_response(client, client.get_object("employee", "e1"))  # type: ignore[arg-type]

    emp.works_for.create("c1", {"role": "Engineer"})
    typed = emp.works_for.get_typed("c1")
    assert typed.role == "Engineer"  # type: ignore[attr-defined]


def test_query_builder_typed_results_and_pagination():
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice", "dept": "Eng"})
    client.upsert_object("employee", "e2", {"name": "Bob", "dept": "Eng"})
    client.upsert_object("employee", "e3", {"name": "Carol", "dept": "Sales"})

    builder = (
        Employee.search_builder(client)  # type: ignore[arg-type]
        .where(Employee.dept == "Eng")
        .order_by(Employee.name.asc())  # type: ignore[attr-defined,arg-type]
    )
    typed_page = builder.limit(1).all_typed()
    assert isinstance(typed_page, Page)
    assert len(typed_page.data) == 1
    assert isinstance(typed_page.data[0], Employee)
    assert typed_page.data[0].dept == "Eng"  # type: ignore[attr-defined]

    pages = list(builder.iter_pages_typed(page_size=1))
    assert len(pages) == 2
    for page in pages:  # type: ignore[index]
        assert isinstance(page, Page)
        for item in page.data:
            assert isinstance(item, Employee)
            assert item.dept == "Eng"
