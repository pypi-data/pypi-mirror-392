"""
Tests for handler consistency and correct URL building.
"""

import pytest
from processcube_client.core.api.helpers.application_info import ApplicationInfoHandler
from processcube_client.core.api.helpers.process_instances import ProcessInstanceHandler
from processcube_client.core.api.helpers.user_tasks import UserTaskHandler
from processcube_client.core.api.helpers.manual_tasks import ManualTaskHandler
from processcube_client.core.api.helpers.empty_tasks import EmptyTaskHandler
from processcube_client.core.api.helpers.flow_node_instances import FlowNodeInstanceHandler
from processcube_client.core.api.helpers.data_object_instances import DataObjectInstanceHandler
from processcube_client.core.api.helpers.process_models import ProcessModelHandler
from processcube_client.core.api.helpers.process_definitions import ProcessDefinitionHandler
from processcube_client.core.api.helpers.external_tasks import ExternalTaskHandler
from processcube_client.core.api.helpers.events import EventsHandler


class TestHandlerInitialization:
    """Test that all handlers initialize correctly with api_version."""
    
    def test_application_info_handler_init(self):
        handler = ApplicationInfoHandler("http://localhost:56100")
        assert handler._api_version == "v1"
        assert handler._base_url == "http://localhost:56100"
    
    def test_application_info_handler_custom_version(self):
        handler = ApplicationInfoHandler("http://localhost:56100", api_version="v2")
        assert handler._api_version == "v2"
    
    def test_process_instance_handler_init(self):
        handler = ProcessInstanceHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_user_task_handler_init(self):
        handler = UserTaskHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_manual_task_handler_init(self):
        handler = ManualTaskHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_empty_task_handler_init(self):
        handler = EmptyTaskHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_flow_node_instance_handler_init(self):
        handler = FlowNodeInstanceHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_data_object_instance_handler_init(self):
        handler = DataObjectInstanceHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_process_model_handler_init(self):
        handler = ProcessModelHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_process_definition_handler_init(self):
        handler = ProcessDefinitionHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_external_task_handler_init(self):
        handler = ExternalTaskHandler("http://localhost:56100")
        assert handler._api_version == "v1"
    
    def test_events_handler_init(self):
        handler = EventsHandler("http://localhost:56100")
        assert handler._api_version == "v1"


class TestHandlerURLBuilding:
    """Test that handlers build correct URLs."""
    
    def test_application_info_handler_urls(self):
        handler = ApplicationInfoHandler("http://localhost:56100")
        
        # Test info endpoint
        url = handler._build_url("info")
        assert url == "http://localhost:56100/atlas_engine/api/v1/info"
        
        # Test authority endpoint
        url = handler._build_url("authority")
        assert url == "http://localhost:56100/atlas_engine/api/v1/authority"
    
    def test_process_instance_handler_urls(self):
        handler = ProcessInstanceHandler("http://localhost:56100")
        
        url = handler._build_url("process_instances/query")
        assert url == "http://localhost:56100/atlas_engine/api/v1/process_instances/query"
        
        url = handler._build_url("process_instances/123/terminate")
        assert url == "http://localhost:56100/atlas_engine/api/v1/process_instances/123/terminate"
    
    def test_user_task_handler_urls(self):
        handler = UserTaskHandler("http://localhost:56100")
        
        url = handler._build_url("flow_node_instances")
        assert url == "http://localhost:56100/atlas_engine/api/v1/flow_node_instances"
        
        url = handler._build_url("user_tasks/123/reserve")
        assert url == "http://localhost:56100/atlas_engine/api/v1/user_tasks/123/reserve"
        
        url = handler._build_url("user_tasks/123/finish")
        assert url == "http://localhost:56100/atlas_engine/api/v1/user_tasks/123/finish"
    
    def test_manual_task_handler_urls(self):
        handler = ManualTaskHandler("http://localhost:56100")
        
        url = handler._build_url("manual_tasks/123/finish")
        assert url == "http://localhost:56100/atlas_engine/api/v1/manual_tasks/123/finish"
    
    def test_empty_task_handler_urls(self):
        handler = EmptyTaskHandler("http://localhost:56100")
        
        url = handler._build_url("empty_activities/123/finish")
        assert url == "http://localhost:56100/atlas_engine/api/v1/empty_activities/123/finish"
    
    def test_process_model_handler_urls(self):
        handler = ProcessModelHandler("http://localhost:56100")
        
        url = handler._build_url("process_models/MyProcess/start")
        assert url == "http://localhost:56100/atlas_engine/api/v1/process_models/MyProcess/start"
    
    def test_process_definition_handler_urls(self):
        handler = ProcessDefinitionHandler("http://localhost:56100")
        
        url = handler._build_url("process_definitions")
        assert url == "http://localhost:56100/atlas_engine/api/v1/process_definitions"
    
    def test_external_task_handler_urls(self):
        handler = ExternalTaskHandler("http://localhost:56100")
        
        url = handler._build_url("external_tasks/fetch_and_lock")
        assert url == "http://localhost:56100/atlas_engine/api/v1/external_tasks/fetch_and_lock"
        
        url = handler._build_url("external_tasks/123/finish")
        assert url == "http://localhost:56100/atlas_engine/api/v1/external_tasks/123/finish"
        
        url = handler._build_url("external_tasks/123/error")
        assert url == "http://localhost:56100/atlas_engine/api/v1/external_tasks/123/error"
    
    def test_events_handler_urls(self):
        handler = EventsHandler("http://localhost:56100")
        
        url = handler._build_url("messages/MyMessage/trigger")
        assert url == "http://localhost:56100/atlas_engine/api/v1/messages/MyMessage/trigger"
        
        url = handler._build_url("signals/MySignal/trigger")
        assert url == "http://localhost:56100/atlas_engine/api/v1/signals/MySignal/trigger"
    
    def test_data_object_instance_handler_urls(self):
        handler = DataObjectInstanceHandler("http://localhost:56100")
        
        url = handler._build_url("data_object_instances/query")
        assert url == "http://localhost:56100/atlas_engine/api/v1/data_object_instances/query"


class TestHandlerAPIVersion:
    """Test that handlers respect custom API versions."""
    
    def test_custom_api_version_v2(self):
        handler = ApplicationInfoHandler("http://localhost:56100", api_version="v2")
        url = handler._build_url("info")
        assert url == "http://localhost:56100/atlas_engine/api/v2/info"
    
    def test_custom_api_version_v3(self):
        handler = ProcessInstanceHandler("http://localhost:56100", api_version="v3")
        url = handler._build_url("process_instances/query")
        assert url == "http://localhost:56100/atlas_engine/api/v3/process_instances/query"


class TestHandlerIdentity:
    """Test that handlers handle identity correctly."""
    
    def test_default_identity(self):
        handler = ApplicationInfoHandler("http://localhost:56100")
        identity = handler._get_identity()
        assert identity["token"] == "ZHVtbXlfdG9rZW4="
    
    def test_custom_identity(self):
        def custom_identity():
            return {"token": "my_custom_token"}
        
        handler = ApplicationInfoHandler("http://localhost:56100", identity=custom_identity)
        identity = handler._get_identity()
        assert identity["token"] == "my_custom_token"
    
    def test_auth_headers_default(self):
        handler = ApplicationInfoHandler("http://localhost:56100")
        headers = handler._get_auth_headers()
        assert headers["Authorization"] == "Bearer ZHVtbXlfdG9rZW4="
    
    def test_auth_headers_custom(self):
        def custom_identity():
            return {"token": "custom_123"}
        
        handler = ApplicationInfoHandler("http://localhost:56100", identity=custom_identity)
        headers = handler._get_auth_headers()
        assert headers["Authorization"] == "Bearer custom_123"
