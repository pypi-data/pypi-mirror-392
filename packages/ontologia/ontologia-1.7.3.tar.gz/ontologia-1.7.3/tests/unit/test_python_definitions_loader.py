from ontologia.ogm.python_definitions import load_python_definitions


def test_load_python_definitions_produces_expected_objects():
    definition_set = load_python_definitions("ontology_definitions.models")

    assert "employee" in definition_set.object_types
    employee = definition_set.object_types["employee"]
    assert employee["primaryKey"] == "employee_id"
    assert "properties" in employee
    assert "name" in employee["properties"]

    assert "works_for" in definition_set.link_types
    works_for = definition_set.link_types["works_for"]
    assert works_for["fromObjectType"] == "employee"
    assert works_for["toObjectType"] == "company"
