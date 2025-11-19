#!/usr/bin/env python3
"""Debug session assignment issue"""

import sys

sys.path.append("/Users/kevinsaltarelli/Documents/GitHub/ontologia")

import sqlmodel

from ontologia.application.actions_service import ActionsService

# Create a session
session = sqlmodel.Session(sqlmodel.create_engine("sqlite:///:memory:"))
print(f"Original session ID: {id(session)}")
print(f"Original session object: {session}")

# Create ActionsService
svc = ActionsService(session, service="ontology", instance="default")
print(f"ActionsService.session ID: {id(svc.session)}")
print(f"ActionsService.session object: {svc.session}")

# Check if they're the same
print(f"Same object? {session is svc.session}")


# Try direct assignment
class TestClass:
    def __init__(self, session):
        print(f"TestClass.__init__ session ID: {id(session)}")
        self.session = session
        print(f"TestClass.session ID: {id(self.session)}")


test = TestClass(session)
print(f"TestClass.session same as original? {test.session is session}")
