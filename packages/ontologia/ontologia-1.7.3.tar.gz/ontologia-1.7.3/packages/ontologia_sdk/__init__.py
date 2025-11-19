"""
ontologia_sdk
--------------
Python SDK for the Ontology API.

This package provides a lightweight client (`OntologyClient`) and (optionally) statically
generated, strongly-typed classes under `ontologia_sdk.ontology` via the `ontologia-cli generate-sdk`
command.
"""

from .client import OntologyClient as OntologyClientSync
from .client_v2 import OntologyClient
from .session import create_local_client, create_remote_client, create_session

__all__ = [
    "OntologyClient",
    "OntologyClientSync",
    "create_session",
    "create_remote_client",
    "create_local_client",
]
