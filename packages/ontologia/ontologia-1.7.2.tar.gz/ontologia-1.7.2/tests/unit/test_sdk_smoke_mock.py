from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def test_smoke_sdk_with_mock_client():
    client = MockOntologyClient()

    # Seed objects
    client.upsert_object("employee", "e1", {"name": "Alice", "dept": "Eng"})
    client.upsert_object("company", "c1", {"name": "ACME"})

    # Load generated class instance
    emp = Employee.get(client, "e1")  # type: ignore[arg-type]
    assert emp.name == "Alice"

    # Create link and verify typed props
    emp.works_for.create("c1", {"role": "Engineer"})
    typed = emp.works_for.get_typed("c1")
    assert typed.role == "Engineer"  # type: ignore[attr-defined]

    typed_page = emp.works_for.all_typed()
    assert typed_page.data[0].link_properties.role == "Engineer"  # type: ignore[attr-defined]

    # List links
    lst = emp.works_for.list()
    assert isinstance(lst, dict)
    assert any(item.get("toPk") == "c1" for item in lst.get("data", []))  # type: ignore[index]

    # Legacy helpers still work
    emp.delete_works_for("c1")
    emp.create_works_for("c1", {"role": "Engineer"})

    emp.works_for.delete("c1")
    lst2 = emp.works_for.list()
    assert all(item.get("toPk") != "c1" for item in lst2.get("data", []))

    # Pagination helpers
    emp.works_for.create("c1", {"role": "Engineer"})
    pages = list(emp.works_for.iter_pages(page_size=1))  # type: ignore[index]
    assert len(pages) >= 1
    assert any(item.get("toPk") == "c1" for page in pages for item in page.get("data", []))  # type: ignore[index]
    typed_pages = list(emp.works_for.iter_pages_typed(page_size=1))
    assert typed_pages
    assert typed_pages[0].data[0].link_properties.role == "Engineer"  # type: ignore[attr-defined]

    # Typed search helpers
    search_results = Employee.search_typed(
        client,  # type: ignore[arg-type]
        where=[{"property": "dept", "op": "eq", "value": "Eng"}],
        limit=5,
    )
    assert any(item.pk == "e1" for item in search_results.data)  # type: ignore[attr-defined]

    typed_iter = list(  # type: ignore[index,arg-type]
        Employee.search_typed(
            client,  # type: ignore[arg-type]
            where=[{"property": "dept", "op": "eq", "value": "Eng"}],
            limit=5,
        ).data  # type: ignore[attr-defined]
    )
    assert any(item.pk == "e1" for item in typed_iter)  # type: ignore[attr-defined]
