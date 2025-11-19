from __future__ import annotations

from pydantic import Field

from ontologia.ogm import LinkModel, ObjectModel


class Employee(ObjectModel):
    __object_type_api_name__ = "employee"
    __primary_key__ = "employee_id"
    __display_name__ = "Employee"
    model_config = {"arbitrary_types_allowed": True}

    employee_id: str = Field(title="Employee ID")
    name: str = Field(title="Name")
    department: str | None = Field(default=None, title="Department")
    company: LinkModel = LinkModel(
        "works_for",
        inverse="has_employees",
        cardinality="many_to_one",
        properties={
            "role": {"dataType": "string", "displayName": "Role"},
            "since": {"dataType": "date", "displayName": "Since"},
        },
    )


class Company(ObjectModel):
    __object_type_api_name__ = "company"
    __primary_key__ = "company_id"
    __display_name__ = "Company"
    model_config = {"arbitrary_types_allowed": True}

    company_id: str = Field(title="Company ID")
    name: str = Field(title="Name")
    industry: str | None = Field(default=None, title="Industry")
    employees: LinkModel = LinkModel(
        "has_employees",
        inverse="works_for",
        direction="incoming",
        cardinality="one_to_many",
    )


# Fix target models after class definition
from ontologia.ogm.link import _link_registry

if "works_for" in _link_registry:
    _link_registry["works_for"]._target_model = Company
if "has_employees" in _link_registry:
    _link_registry["has_employees"]._target_model = Employee
