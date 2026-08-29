"""
Shared pytest fixtures for API tests.
"""

import pytest
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi.testclient import TestClient
from backend.api.main import app

@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient to avoid repeated app startup costs."""
    with TestClient(app) as c:
        yield c
