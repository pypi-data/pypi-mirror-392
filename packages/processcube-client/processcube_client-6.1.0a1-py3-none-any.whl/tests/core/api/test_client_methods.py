"""
Tests for Client class method consistency with handlers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from processcube_client.core.api.client import Client
from processcube_client.core.api.helpers.user_tasks import UserTaskQuery, ReserveUserTaskRequest
from processcube_client.core.api.helpers.manual_tasks import ManualTaskQuery
from processcube_client.core.api.helpers.empty_tasks import EmptyTaskQuery
from processcube_client.core.api.helpers.flow_node_instances import FlowNodeInstancesQuery
from processcube_client.core.api.helpers.data_object_instances import DataObjectInstancesQuery
from processcube_client.core.api.helpers.process_instances import ProcessInstanceQueryRequest
from processcube_client.core.api.helpers.process_definitions import ProcessDefinitionUploadPayload
from processcube_client.core.api.helpers.process_models import ProcessStartRequest
from processcube_client.core.api.helpers.events import MessageTriggerRequest


class TestClientMethodNaming:
    """Test that Client methods match handler method names."""
    
    def test_client_initialization(self):
        client = Client("http://localhost:56100")
        assert client._url == "http://localhost:56100"
        assert client._api_version == "v1"
    
    @patch('processcube_client.core.api.helpers.user_tasks.UserTaskHandler.query')
    def test_user_task_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        query = UserTaskQuery(process_instance_id="test123")
        
        result = client.user_task_query(query)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.user_tasks.UserTaskHandler.finish')
    def test_user_task_finish(self, mock_finish):
        mock_finish.return_value = True
        
        client = Client("http://localhost:56100")
        client.user_task_finish("task123", {"result": "done"})
        
        mock_finish.assert_called_once_with("task123", {"result": "done"})
    
    @patch('processcube_client.core.api.helpers.user_tasks.UserTaskHandler.reserve')
    def test_user_task_reserve(self, mock_reserve):
        mock_reserve.return_value = True
        
        client = Client("http://localhost:56100")
        request = ReserveUserTaskRequest(actual_owner_id="user123")
        client.user_task_reserve("task123", request)
        
        mock_reserve.assert_called_once_with("task123", request)
    
    @patch('processcube_client.core.api.helpers.user_tasks.UserTaskHandler.cancel_reservation')
    def test_user_task_cancel_reservation(self, mock_cancel):
        mock_cancel.return_value = True
        
        client = Client("http://localhost:56100")
        client.user_task_cancel_reservation("task123")
        
        mock_cancel.assert_called_once_with("task123")
    
    @patch('processcube_client.core.api.helpers.manual_tasks.ManualTaskHandler.query')
    def test_manual_task_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        query = ManualTaskQuery(process_instance_id="test123")
        
        result = client.manual_task_query(query)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.manual_tasks.ManualTaskHandler.finish')
    def test_manual_task_finish(self, mock_finish):
        mock_finish.return_value = True
        
        client = Client("http://localhost:56100")
        client.manual_task_finish("task123")
        
        mock_finish.assert_called_once_with("task123")
    
    @patch('processcube_client.core.api.helpers.empty_tasks.EmptyTaskHandler.query')
    def test_empty_task_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        query = EmptyTaskQuery(process_instance_id="test123")
        
        result = client.empty_task_query(query)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.empty_tasks.EmptyTaskHandler.finish')
    def test_empty_task_finish(self, mock_finish):
        mock_finish.return_value = True
        
        client = Client("http://localhost:56100")
        client.empty_task_finish("task123")
        
        mock_finish.assert_called_once_with("task123")
    
    @patch('processcube_client.core.api.helpers.flow_node_instances.FlowNodeInstanceHandler.query')
    def test_flow_node_instance_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        query = FlowNodeInstancesQuery(process_instance_id="test123")
        
        result = client.flow_node_instance_query(query)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.data_object_instances.DataObjectInstanceHandler.query')
    def test_data_object_instance_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        query = DataObjectInstancesQuery(process_instance_id="test123")
        
        result = client.data_object_instance_query(query)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.process_instances.ProcessInstanceHandler.query')
    def test_process_instance_query(self, mock_query):
        mock_query.return_value = []
        
        client = Client("http://localhost:56100")
        request = ProcessInstanceQueryRequest(process_model_id="test")
        
        result = client.process_instance_query(request)
        mock_query.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.process_instances.ProcessInstanceHandler.terminate')
    def test_process_instance_terminate(self, mock_terminate):
        mock_terminate.return_value = True
        
        client = Client("http://localhost:56100")
        client.process_instance_terminate("instance123")
        
        mock_terminate.assert_called_once_with("instance123")
    
    @patch('processcube_client.core.api.helpers.process_definitions.ProcessDefinitionHandler.upload')
    def test_process_definition_upload(self, mock_upload):
        client = Client("http://localhost:56100")
        payload = ProcessDefinitionUploadPayload(xml="<test/>", overwrite_existing=True)
        
        client.process_definition_upload(payload)
        mock_upload.assert_called_once_with(payload)
    
    @patch('processcube_client.core.api.helpers.process_definitions.ProcessDefinitionHandler.delete')
    def test_process_definition_delete(self, mock_delete):
        client = Client("http://localhost:56100")
        
        client.process_definition_delete("def123", delete_all_related_data=True)
        mock_delete.assert_called_once_with("def123", True)
    
    @patch('processcube_client.core.api.helpers.process_models.ProcessModelHandler.start')
    def test_process_model_start(self, mock_start):
        from processcube_client.core.api.helpers.process_models import ProcessStartResponse
        mock_start.return_value = ProcessStartResponse(
            process_instance_id="inst123",
            correlation_id="corr123"
        )
        
        client = Client("http://localhost:56100")
        request = ProcessStartRequest(
            process_model_id="MyProcess",
            start_event_id="StartEvent_1"
        )
        
        result = client.process_model_start("MyProcess", request)
        mock_start.assert_called_once_with("MyProcess", request)
        assert result.process_instance_id == "inst123"
    
    @patch('processcube_client.core.api.helpers.events.EventsHandler.trigger_message')
    def test_trigger_message(self, mock_trigger):
        mock_trigger.return_value = True
        
        client = Client("http://localhost:56100")
        request = MessageTriggerRequest(payload={})
        
        client.trigger_message("MyMessage", request)
        mock_trigger.assert_called_once_with("MyMessage", request)
    
    @patch('processcube_client.core.api.helpers.events.EventsHandler.trigger_signal')
    def test_trigger_signal(self, mock_trigger):
        mock_trigger.return_value = True
        
        client = Client("http://localhost:56100")
        
        client.trigger_signal("MySignal")
        mock_trigger.assert_called_once_with("MySignal")


class TestClientRepr:
    """Test Client string representation."""
    
    def test_client_repr_default(self):
        client = Client("http://localhost:56100")
        assert repr(client) == "Client(url='http://localhost:56100', api_version='v1')"
    
    def test_client_repr_custom_version(self):
        client = Client("http://localhost:56100", api_version="v2")
        assert repr(client) == "Client(url='http://localhost:56100', api_version='v2')"


class TestClientDeployment:
    """Test deployment convenience methods."""
    
    @patch('processcube_client.core.api.helpers.process_definitions.ProcessDefinitionHandler.upload')
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.is_dir')
    def test_deploy_single_file(self, mock_is_dir, mock_is_file, mock_open, mock_upload):
        mock_is_file.return_value = True
        mock_is_dir.return_value = False
        mock_open.return_value.__enter__.return_value.read.return_value = "<bpmn>test</bpmn>"
        
        client = Client("http://localhost:56100")
        result = client.deploy_bpmn_from_path("test.bpmn")
        
        assert len(result.deployed_files) == 1
        assert result.deployed_files[0].deployed == True
        mock_upload.assert_called_once()
    
    @patch('processcube_client.core.api.helpers.process_definitions.ProcessDefinitionHandler.upload')
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.glob')
    def test_deploy_directory(self, mock_glob, mock_is_dir, mock_is_file, mock_open, mock_upload):
        from pathlib import Path
        
        mock_is_file.return_value = False
        mock_is_dir.return_value = True
        mock_glob.return_value = [Path("test1.bpmn"), Path("test2.bpmn")]
        mock_open.return_value.__enter__.return_value.read.return_value = "<bpmn>test</bpmn>"
        
        client = Client("http://localhost:56100")
        result = client.deploy_bpmn_from_path("processes/")
        
        assert len(result.deployed_files) == 2
        assert mock_upload.call_count == 2
