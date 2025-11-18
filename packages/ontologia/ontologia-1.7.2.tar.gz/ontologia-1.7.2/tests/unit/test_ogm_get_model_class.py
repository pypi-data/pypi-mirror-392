from __future__ import annotations

def test_get_model_class_resolves_imported_models():
    # Import OGM and definitions to populate registry
    from ontologia import ogm as _ogm  # type: ignore[attr-defined]
    import ontology_definitions.models.core as core_models  # noqa: F401

    Company = _ogm.get_model_class("company")
    Employee = _ogm.get_model_class("employee")

    assert Company is not None
    assert Employee is not None
    assert getattr(Company, "__object_type_api_name__", None) == "company"
    assert getattr(Employee, "__object_type_api_name__", None) == "employee"

