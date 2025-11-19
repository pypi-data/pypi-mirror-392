from __future__ import annotations


def test_get_model_class_resolves_imported_models():
    # Import OGM and definitions to populate registry
    import ontology_definitions.models.core as core_models  # noqa: F401
    from ontologia import ogm as _ogm  # type: ignore[attr-defined]

    company = _ogm.get_model_class("company")
    employee = _ogm.get_model_class("employee")

    assert company is not None
    assert employee is not None
    assert getattr(company, "__object_type_api_name__", None) == "company"
    assert getattr(employee, "__object_type_api_name__", None) == "employee"
