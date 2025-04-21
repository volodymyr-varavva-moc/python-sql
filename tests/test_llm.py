import pytest
from unittest.mock import patch, MagicMock
import json

from app.llm.openai_client import LLMClient


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response object"""
    mock_response = MagicMock()
    mock_tool_call = MagicMock()
    mock_tool_call.function.arguments = json.dumps({
        "sql_query": "SELECT * FROM customers WHERE id = :customer_id",
        "parameters": [
            {
                "name": "customer_id",
                "value": "1",
                "type": "number"
            }
        ],
        "explanation": "This query retrieves all information about the customer with ID 1."
    })
    
    mock_message = MagicMock()
    mock_message.tool_calls = [mock_tool_call]
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.fixture
def mock_validation_response():
    """Create a mock OpenAI validation response"""
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "The SQL query appears safe and does not contain any obvious security issues."
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response.choices = [mock_choice]
    return mock_response


class TestLLMClient:
    
    @patch('openai.OpenAI')
    def test_init(self, mock_openai):
        """Test that the LLM client initializes correctly"""
        client = LLMClient()
        assert client.model == "gpt-3.5-turbo-1106"
        assert mock_openai.called
    
    @patch('app.llm.openai_client.OpenAI')
    def test_generate_sql_success(self, mock_openai_class, mock_openai_response):
        """Test successful SQL generation"""
        # Set up the mock
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_openai_instance
        
        # Create client and call method
        client = LLMClient()
        result = client.generate_sql("Show me customer with ID 1")
        
        # Assert response is processed correctly
        assert result["sql_query"] == "SELECT * FROM customers WHERE id = :customer_id"
        assert len(result["parameters"]) == 1
        assert result["parameters"][0]["name"] == "customer_id"
        assert result["explanation"] is not None
    
    @patch('app.llm.openai_client.OpenAI')
    def test_generate_sql_exception(self, mock_openai_class):
        """Test error handling when OpenAI API fails"""
        # Set up the mock to raise an exception
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_openai_instance
        
        # Create client and call method
        client = LLMClient()
        result = client.generate_sql("Show me customer with ID 1")
        
        # Assert error is handled
        assert "error" in result
        assert "API Error" in result["error"]
    
    @patch('app.llm.openai_client.OpenAI')
    def test_validate_sql_safe(self, mock_openai_class, mock_validation_response):
        """Test SQL validation when query is safe"""
        # Set up the mock
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_validation_response
        mock_openai_class.return_value = mock_openai_instance
        
        # Create client and call method
        client = LLMClient()
        result = client.validate_sql("SELECT * FROM customers WHERE id = 1")
        
        # Assert response indicates query is safe
        assert result["is_safe"] == True
        assert result["analysis"] is not None
    
    @patch('app.llm.openai_client.OpenAI')
    def test_validate_sql_unsafe(self, mock_openai_class):
        """Test SQL validation when query is unsafe"""
        # Create response indicating injection vulnerability
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This query may be vulnerable to SQL injection attacks."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        # Set up the mock
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_openai_instance
        
        # Create client and call method
        client = LLMClient()
        result = client.validate_sql("SELECT * FROM users WHERE username = '" + input + "'")
        
        # Assert response indicates query is unsafe
        assert result["is_safe"] == False
        assert result["analysis"] is not None
