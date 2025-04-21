import pytest
from unittest.mock import patch
import json

from fastapi.testclient import TestClient
from app.main import app
from app.db.base import get_db
from app.api.deps import get_llm_client


@pytest.fixture
def mock_openai_completion():
    """Mock OpenAI chat completion for integration testing"""
    class MockResponse:
        def __init__(self, content):
            self.content = content
            
    class MockMessage:
        def __init__(self, tool_call):
            self.tool_calls = [tool_call]
            
    class MockFunctionCall:
        def __init__(self, arguments):
            self.function = MockFunction(arguments)
            
    class MockFunction:
        def __init__(self, arguments):
            self.arguments = arguments
            
    class MockChoice:
        def __init__(self, message):
            self.message = message
    
    # Generate a mock tool call for customer query
    customer_query_json = json.dumps({
        "sql_query": "SELECT * FROM customers",
        "parameters": [],
        "explanation": "This query retrieves all customers from the database."
    })
    
    tool_call = MockFunctionCall(customer_query_json)
    message = MockMessage(tool_call)
    choice = MockChoice(message)
    
    # Return mocked response
    return [choice]


@pytest.mark.integration
class TestEndToEndIntegration:
    
    @patch("openai.OpenAI")
    def test_full_query_flow(self, mock_openai, db_with_data, mock_openai_completion):
        """Test the full query flow from user input to results"""
        # Configure mock
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.chat.completions.create.return_value.choices = mock_openai_completion
        
        # Create test client
        with patch("app.api.routes.query.get_db") as mock_get_db:
            mock_get_db.return_value = db_with_data
            
            client = TestClient(app)
            
            # Send request
            response = client.post(
                "/api/v1/query/process",
                json={"query": "Show me all customers"}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            
            # Check SQL and results
            assert data["sql_query"] == "SELECT * FROM customers"
            assert data["explanation"] == "This query retrieves all customers from the database."
            assert data["results"]["success"] == True
            assert data["results"]["row_count"] == 2  # Our test data has 2 customers
            
            # Check actual customer data
            customers = data["results"]["rows"]
            assert any(c["name"] == "Test Customer" for c in customers)
            assert any(c["name"] == "Another Customer" for c in customers)
    
    @patch("openai.OpenAI")
    def test_filtered_query_flow(self, mock_openai, db_with_data):
        """Test a query with filters"""
        # Configure mock
        mock_openai_instance = mock_openai.return_value
        
        # Create a mock response for a filtered query
        class MockChoice:
            class Message:
                class ToolCalls:
                    class Function:
                        def __init__(self, args):
                            self.arguments = args
                    
                    def __init__(self, args):
                        self.function = self.Function(args)
                
                def __init__(self, args):
                    self.tool_calls = [self.ToolCalls(args)]
            
            def __init__(self, args):
                self.message = self.Message(args)
        
        filter_query_json = json.dumps({
            "sql_query": "SELECT * FROM customers WHERE id = :customer_id",
            "parameters": [
                {
                    "name": "customer_id",
                    "value": "1",
                    "type": "number"
                }
            ],
            "explanation": "This query retrieves the customer with ID 1."
        })
        
        mock_openai_instance.chat.completions.create.return_value.choices = [
            MockChoice(filter_query_json)
        ]
        
        # Create test client
        with patch("app.api.routes.query.get_db") as mock_get_db:
            mock_get_db.return_value = db_with_data
            
            client = TestClient(app)
            
            # Send request
            response = client.post(
                "/api/v1/query/process",
                json={"query": "Show me customer with ID 1"}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            
            # Check SQL and parameters
            assert "WHERE id = :customer_id" in data["sql_query"]
            assert len(data["parameters"]) == 1
            assert data["parameters"][0]["name"] == "customer_id"
            
            # Check results - should be just one customer
            assert data["results"]["success"] == True
            assert data["results"]["row_count"] == 1
            assert data["results"]["rows"][0]["name"] == "Test Customer"
