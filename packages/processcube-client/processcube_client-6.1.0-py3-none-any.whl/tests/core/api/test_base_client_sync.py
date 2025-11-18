"""
Tests for the synchronous BaseClient URL building functionality.
"""

import pytest
from processcube_client.core.api.base_client import BaseClient


def test_base_client_initialization():
    """Test BaseClient initialization with default parameters."""
    client = BaseClient("http://localhost:56100")
    
    assert client._base_url == "http://localhost:56100"
    assert client._api_version == "v1"
    
    # Test default identity
    identity = client._get_identity()
    assert identity["token"] == "ZHVtbXlfdG9rZW4="


def test_base_client_custom_api_version():
    """Test BaseClient with custom API version."""
    client = BaseClient("http://localhost:56100", api_version="v2")
    
    assert client._api_version == "v2"


def test_base_client_custom_identity():
    """Test BaseClient with custom identity."""
    def custom_identity():
        return {"token": "custom_token_123"}
    
    client = BaseClient("http://localhost:56100", identity=custom_identity)
    
    identity = client._get_identity()
    assert identity["token"] == "custom_token_123"


def test_build_url_basic():
    """Test URL building with basic path."""
    client = BaseClient("http://localhost:56100")
    
    url = client._build_url("process_models")
    assert url == "http://localhost:56100/atlas_engine/api/v1/process_models"


def test_build_url_with_leading_slash():
    """Test URL building removes leading slash from path."""
    client = BaseClient("http://localhost:56100")
    
    url = client._build_url("/process_models")
    assert url == "http://localhost:56100/atlas_engine/api/v1/process_models"


def test_build_url_with_query_params():
    """Test URL building with query parameters."""
    client = BaseClient("http://localhost:56100")
    
    url = client._build_url("process_instances/query?limit=10&offset=0")
    assert url == "http://localhost:56100/atlas_engine/api/v1/process_instances/query?limit=10&offset=0"


def test_build_url_custom_api_version():
    """Test URL building with custom API version."""
    client = BaseClient("http://localhost:56100", api_version="v2")
    
    url = client._build_url("process_models")
    assert url == "http://localhost:56100/atlas_engine/api/v2/process_models"


def test_build_url_trailing_slash_base_url():
    """Test URL building with trailing slash in base URL."""
    client = BaseClient("http://localhost:56100/")
    
    url = client._build_url("process_models")
    assert url == "http://localhost:56100/atlas_engine/api/v1/process_models"


def test_build_url_complex_path():
    """Test URL building with complex path including IDs."""
    client = BaseClient("http://localhost:56100")
    
    url = client._build_url("process_models/MyProcess/start")
    assert url == "http://localhost:56100/atlas_engine/api/v1/process_models/MyProcess/start"


def test_auth_headers():
    """Test authentication header generation."""
    client = BaseClient("http://localhost:56100")
    
    headers = client._get_auth_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer ZHVtbXlfdG9rZW4="


def test_auth_headers_custom_token():
    """Test authentication header with custom token."""
    def custom_identity():
        return {"token": "my_custom_token"}
    
    client = BaseClient("http://localhost:56100", identity=custom_identity)
    
    headers = client._get_auth_headers()
    assert headers["Authorization"] == "Bearer my_custom_token"


def test_default_headers():
    """Test default headers."""
    client = BaseClient("http://localhost:56100")
    
    headers = client._get_default_headers()
    assert headers["Content-Type"] == "application/json"
