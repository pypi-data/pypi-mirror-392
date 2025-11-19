from __future__ import annotations

import tempfile

from sqlmodel import create_engine


def test_local_session_with_ogm_create_get_list():
    # Create temp SQLite DB
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tf:
        conn = f"sqlite:///{tf.name}"

        # Import models and SDK
        from ontologia_sdk.session import LocalSession  # type: ignore

        import ontology_definitions.models.core as core_models  # noqa: F401
        from ontologia.ogm import Ontology

        # Prepare engine and ontology
        engine = create_engine(conn)
        onto = Ontology(engine)
        onto.initialize_database()
        # Register models and apply schema
        onto.model(core_models.Company)
        onto.model(core_models.Employee)
        onto.apply_schema([core_models.Company, core_models.Employee])

        # Local session with OGM enabled
        session = LocalSession(conn, use_ogm=True, ogm_module="ontology_definitions.models")

        # Create object via OGM
        company = {
            "company_id": "c1",
            "name": "Acme",
            "industry": "Manufacturing",
        }
        created = None
        import asyncio

        created = asyncio.run(session.create_object("company", company))
        assert created["company_id"] == "c1"

        # Get object
        got = asyncio.run(session.get_object("company", "c1"))
        assert got is not None
        if "name" in got:
            assert got["name"] == "Acme"
        else:
            assert got.get("properties", {}).get("name") == "Acme"

        # List objects with filter
        lst = asyncio.run(session.list_objects("company", name="Acme"))
        assert isinstance(lst, list) and lst
        first = lst[0]
        if "name" in first:
            assert first["name"] == "Acme"
        else:
            assert first.get("properties", {}).get("name") == "Acme"
