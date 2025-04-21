import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


class TestQueryAPI:
    
    @patch("app.api.routes.query.get_db")
    @patch("app.api.routes.query.get_llm_client")
    def test_process_query_success(self, mock_get_llm, mock_get_db, db_with_data, mock_llm_client):
        """Test successful query processing"""
        # Configure mocks
        mock_get_db.return_value = db_with_data
        mock_get_llm.return_value = mock_llm_client
        
        # Create client
        client = TestClient(app)
        
        # Send request
        response = client.post(
            "/api/v1/query/process",
            json={"query": "Show me customer with ID 1"}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "sql_query" in data
        assert "parameters" in data
        assert "explanation" in data
        assert "results" in data
        assert data["results"]["success"] == True
    
    @patch("app.api.routes.query.get_db")
    @patch("app.api.routes.query.get_llm_client")
    def test_process_query_llm_error(self, mock_get_llm, mock_get_db, db_with_data):
        """Test handling of LLM errors"""
        # Configure mocks
        mock_get_db.return_value = db_with_data
        
        mock_llm = MagicMock()
        mock_llm.generate_sql.return_value = {"error": "LLM API Error"}
        mock_get_llm.return_value = mock_llm
        
        # Create client
        client = TestClient(app)
        
        # Send request
        response = client.post(
            "/api/v1/query/process",
            json={"query": "Show me customer with ID 1"}
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "LLM API Error"
    
    @patch("app.api.routes.query.get_db")
    @patch("app.api.routes.query.get_llm_client")
    def test_process_query_unsafe_sql(self, mock_get_llm, mock_get_db, db_with_data):
        """Test handling of unsafe SQL"""
        # Configure mocks
        mock_get_db.return_value = db_with_data
        
        mock_llm = MagicMock()
        mock_llm.generate_sql.return_value = {
            "sql_query": "SELECT * FROM customers WHERE id = '1'",
            "parameters": [],
            "explanation": "Test query"
        }
        mock_llm.validate_sql.return_value = {
            "is_safe": False,
            "analysis": "Potential SQL injection vulnerability"
        }
        mock_get_llm.return_value = mock_llm
        
        # Create client
        client = TestClient(app)
        
        # Send request
        response = client.post(
            "/api/v1/query/process",
            json={"query": "Show me customer with ID 1"}
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "security validation" in data["detail"]
    
    @patch("app.api.routes.query.get_db")
    @patch("app.api.routes.query.get_llm_client")
    def test_process_query_execution_error(self, mock_get_llm, mock_get_db, db_with_data):
        """Test handling of query execution errors"""
        # Configure mocks
        mock_get_db.return_value = db_with_data
        
        mock_llm = MagicMock()
        mock_llm.generate_sql.return_value = {
            "sql_query": "SELECT * FROM nonexistent_table",
            "parameters": [],
            "explanation": "Test query that will fail"
        }
        mock_llm.validate_sql.return_value = {
            "is_safe": True,
            "analysis": "The query is safe"
        }
        mock_get_llm.return_value = mock_llm
        
        # Create client
        client = TestClient(app)
        
        # Send request
        response = client.post(
            "/api/v1/query/process",
            json={"query": "Show me a nonexistent table"}
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
