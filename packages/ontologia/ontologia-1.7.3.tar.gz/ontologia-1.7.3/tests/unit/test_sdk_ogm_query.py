from __future__ import annotations

import asyncio
import tempfile

from sqlmodel import create_engine


def test_ogm_query_local_mode():
    # Setup temp DB and OGM schema
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tf:
        conn = f"sqlite:///{tf.name}"
        import ontology_definitions.models.core as core_models  # noqa: F401
        from ontologia.ogm import Ontology

        engine = create_engine(conn)
        onto = Ontology(engine)
        onto.initialize_database()
        onto.model(core_models.Company)
        onto.model(core_models.Employee)
        onto.apply_schema([core_models.Company, core_models.Employee])

        # Create a company via OGM session
        from ontologia_sdk.session import LocalSession

        sess = LocalSession(conn, use_ogm=True, ogm_module="ontology_definitions.models")
        created = asyncio.run(sess.create_object("company", {"company_id": "c1", "name": "Acme"}))
        assert created.get("company_id") == "c1"

        # Query via client OGM query
        from ontologia_sdk.client_v2 import OntologyClient

        client = OntologyClient(
            connection_string=conn, use_ogm=True, ogm_module="ontology_definitions.models"
        )
        results = asyncio.run(
            client.ogm_query("company").where("name", "eq", "Acme").limit(10).all()
        )
        assert isinstance(results, list) and results
        first = results[0]
        assert (first.get("name") == "Acme") or (first.get("properties", {}).get("name") == "Acme")
