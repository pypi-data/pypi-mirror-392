"""
🏭 Test Factories for Ontologia
Modern factory pattern for creating test data with realistic defaults.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import factory

from ontologia.domain.metamodels.instances.models_sql import (
    LinkedObject as SQLLinkedObject,
)
from ontologia.domain.metamodels.instances.models_sql import (
    ObjectInstance as SQLObjectInstance,
)
from ontologia.domain.metamodels.types import (
    ActionType,
    LinkedObject,
    LinkType,
    ObjectInstance,
    ObjectType,
    PropertyDefinition,
)


class PropertyDefinitionFactory(factory.Factory):
    """Factory for property definitions"""

    class Meta:
        model = PropertyDefinition

    data_type = "string"
    display_name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    required = False
    default_value = None
    validation_rules = {}


class ObjectTypeFactory(factory.Factory):
    """Factory for object types"""

    class Meta:
        model = ObjectType

    name = factory.Faker("word")
    display_name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    primary_key = "id"
    properties = factory.LazyAttribute(
        lambda _: {
            "id": PropertyDefinitionFactory(data_type="string", display_name="ID", required=True),
            "created_at": PropertyDefinitionFactory(
                data_type="datetime", display_name="Created At", required=True, auto_generate=True
            ),
        }
    )
    extends = None
    is_abstract = False
    tags = []


class LinkTypeFactory(factory.Factory):
    """Factory for link types"""

    class Meta:
        model = LinkType

    name = factory.Faker("word")
    display_name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    source_object_type = factory.SubFactory(ObjectTypeFactory)
    target_object_type = factory.SubFactory(ObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda _: {
            "created_at": PropertyDefinitionFactory(
                data_type="datetime", display_name="Created At", required=True, auto_generate=True
            )
        }
    )
    is_bidirectional = False
    cardinality = "many-to-many"
    tags = []


class ActionTypeFactory(factory.Factory):
    """Factory for action types"""

    class Meta:
        model = ActionType

    name = factory.Faker("word")
    display_name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    input_object_type = factory.SubFactory(ObjectTypeFactory)
    output_object_type = factory.SubFactory(ObjectTypeFactory)
    parameters = factory.LazyAttribute(
        lambda _: {
            "batch_size": PropertyDefinitionFactory(
                data_type="integer", display_name="Batch Size", default_value=100
            )
        }
    )
    implementation_code = "def execute(context): pass"
    is_async = False
    timeout_seconds = 30
    tags = []


class ObjectInstanceFactory(factory.Factory):
    """Factory for object instances"""

    class Meta:
        model = ObjectInstance

    id = factory.LazyAttribute(lambda _: str(uuid4()))
    object_type = factory.SubFactory(ObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda obj_type: {
            "id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "name": factory.Faker("name").generate({}),
            "email": factory.Faker("email").generate({}),
        }
    )
    tenant_id = "default"
    created_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    updated_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    version = 1
    is_active = True


class LinkedObjectFactory(factory.Factory):
    """Factory for linked objects"""

    class Meta:
        model = LinkedObject

    id = factory.LazyAttribute(lambda _: str(uuid4()))
    link_type = factory.SubFactory(LinkTypeFactory)
    source_object = factory.SubFactory(ObjectInstanceFactory)
    target_object = factory.SubFactory(ObjectInstanceFactory)
    properties = factory.LazyAttribute(
        lambda _: {
            "created_at": datetime.now(UTC).isoformat(),
            "strength": factory.Faker("pyfloat", min_value=0.0, max_value=1.0).generate({}),
        }
    )
    tenant_id = "default"
    created_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    updated_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    version = 1
    is_active = True


class SQLObjectInstanceFactory(factory.Factory):
    """Factory for SQL object instances"""

    class Meta:
        model = SQLObjectInstance

    id = factory.LazyAttribute(lambda _: str(uuid4()))
    object_type_name = factory.Faker("word")
    properties = factory.LazyAttribute(
        lambda _: {
            "id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "name": factory.Faker("name").generate({}),
        }
    )
    tenant_id = "default"
    created_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    updated_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    version = 1
    is_active = True


class SQLLinkedObjectFactory(factory.Factory):
    """Factory for SQL linked objects"""

    class Meta:
        model = SQLLinkedObject

    id = factory.LazyAttribute(lambda _: str(uuid4()))
    link_type_name = factory.Faker("word")
    source_object_id = factory.LazyAttribute(lambda _: str(uuid4()))
    target_object_id = factory.LazyAttribute(lambda _: str(uuid4()))
    properties = factory.LazyAttribute(
        lambda _: {
            "created_at": datetime.now(UTC).isoformat(),
            "strength": 0.8,
        }
    )
    tenant_id = "default"
    created_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    updated_at = factory.LazyAttribute(lambda _: datetime.now(UTC))
    version = 1
    is_active = True


# 🏭 Specialized Factories for Common Test Scenarios


class CustomerObjectTypeFactory(ObjectTypeFactory):
    """Factory for Customer object type"""

    name = "Customer"
    display_name = "Customer"
    description = "Business customer account"
    properties = factory.LazyAttribute(
        lambda _: {
            "id": PropertyDefinitionFactory(
                data_type="string", display_name="Customer ID", required=True
            ),
            "name": PropertyDefinitionFactory(
                data_type="string", display_name="Full Name", required=True
            ),
            "email": PropertyDefinitionFactory(
                data_type="string",
                display_name="Email Address",
                required=True,
                validation_rules={"format": "email"},
            ),
            "tier": PropertyDefinitionFactory(
                data_type="enum",
                display_name="Customer Tier",
                values=["basic", "premium", "enterprise"],
                default_value="basic",
            ),
            "created_at": PropertyDefinitionFactory(
                data_type="datetime", display_name="Created At", required=True, auto_generate=True
            ),
        }
    )


class ProductObjectTypeFactory(ObjectTypeFactory):
    """Factory for Product object type"""

    name = "Product"
    display_name = "Product"
    description = "Products available for sale"
    properties = factory.LazyAttribute(
        lambda _: {
            "sku": PropertyDefinitionFactory(
                data_type="string",
                display_name="SKU",
                required=True,
                validation_rules={"pattern": "^[A-Z0-9]{8,12}$"},
            ),
            "name": PropertyDefinitionFactory(
                data_type="string", display_name="Product Name", required=True
            ),
            "price": PropertyDefinitionFactory(
                data_type="decimal",
                display_name="Price",
                required=True,
                validation_rules={"min_value": 0},
            ),
            "category": PropertyDefinitionFactory(
                data_type="enum",
                display_name="Category",
                values=["electronics", "clothing", "books", "home", "sports"],
                required=True,
            ),
            "is_active": PropertyDefinitionFactory(
                data_type="boolean", display_name="Is Active", default_value=True
            ),
        }
    )


class CustomerPurchasesLinkTypeFactory(LinkTypeFactory):
    """Factory for Customer purchases Product link type"""

    name = "Customer_Purchases"
    display_name = "Customer Purchases"
    description = "Customer purchases products"
    source_object_type = factory.SubFactory(CustomerObjectTypeFactory)
    target_object_type = factory.SubFactory(ProductObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda _: {
            "quantity": PropertyDefinitionFactory(
                data_type="integer",
                display_name="Quantity",
                required=True,
                validation_rules={"min_value": 1},
            ),
            "purchase_date": PropertyDefinitionFactory(
                data_type="datetime", display_name="Purchase Date", required=True
            ),
            "unit_price": PropertyDefinitionFactory(
                data_type="decimal", display_name="Unit Price", required=True
            ),
        }
    )
    cardinality = "many-to-many"


class CustomerObjectInstanceFactory(ObjectInstanceFactory):
    """Factory for Customer object instances"""

    object_type = factory.SubFactory(CustomerObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda _: {
            "id": str(uuid4()),
            "name": factory.Faker("name").generate({}),
            "email": factory.Faker("email").generate({}),
            "tier": factory.Faker(
                "random_element", elements=["basic", "premium", "enterprise"]
            ).generate({}),
            "created_at": datetime.now(UTC).isoformat(),
        }
    )


class ProductObjectInstanceFactory(ObjectInstanceFactory):
    """Factory for Product object instances"""

    object_type = factory.SubFactory(ProductObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda _: {
            "sku": factory.Faker("bothify", text="????????").generate({}).upper(),
            "name": factory.Faker("catch_phrase").generate({}),
            "price": round(factory.Faker("pyfloat", min_value=10, max_value=1000).generate({}), 2),
            "category": factory.Faker(
                "random_element", elements=["electronics", "clothing", "books", "home", "sports"]
            ).generate({}),
            "is_active": True,
        }
    )


# 🎯 Test Data Builder Pattern


class TestDataBuilder:
    """Builder pattern for creating complex test scenarios"""

    def __init__(self):
        self.object_types = []
        self.link_types = []
        self.object_instances = []
        self.linked_objects = []

    def with_customer_object_type(self, **overrides):
        """Add customer object type"""
        customer_type = CustomerObjectTypeFactory.create(**overrides)
        self.object_types.append(customer_type)
        return self

    def with_product_object_type(self, **overrides):
        """Add product object type"""
        product_type = ProductObjectTypeFactory.create(**overrides)
        self.object_types.append(product_type)
        return self

    def with_customer_purchases_link(self, **overrides):
        """Add customer purchases link type"""
        link_type = CustomerPurchasesLinkTypeFactory.create(**overrides)
        self.link_types.append(link_type)
        return self

    def with_customers(self, count: int = 3, **overrides):
        """Add multiple customer instances"""
        for _ in range(count):
            customer = CustomerObjectInstanceFactory.create(**overrides)
            self.object_instances.append(customer)
        return self

    def with_products(self, count: int = 5, **overrides):
        """Add multiple product instances"""
        for _ in range(count):
            product = ProductObjectInstanceFactory.create(**overrides)
            self.object_instances.append(product)
        return self

    def build(self):
        """Build the test data structure"""
        return {
            "object_types": self.object_types,
            "link_types": self.link_types,
            "object_instances": self.object_instances,
            "linked_objects": self.linked_objects,
        }


# 🛠️ Utility Functions


def create_test_scenario(
    customers_count: int = 3, products_count: int = 5, include_purchases: bool = True
) -> dict[str, Any]:
    """Create a complete test scenario with customers, products, and purchases"""

    builder = TestDataBuilder()

    # Create object types
    builder.with_customer_object_type()
    builder.with_product_object_type()

    if include_purchases:
        builder.with_customer_purchases_link()

    # Create instances
    builder.with_customers(customers_count)
    builder.with_products(products_count)

    return builder.build()


def create_tenant_scenario(tenant_id: str, **kwargs) -> dict[str, Any]:
    """Create a test scenario for a specific tenant"""
    scenario = create_test_scenario(**kwargs)

    # Update all objects with tenant ID
    for instance in scenario["object_instances"]:
        instance.tenant_id = tenant_id

    for link in scenario["linked_objects"]:
        link.tenant_id = tenant_id

    return scenario
