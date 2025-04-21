import pytest
from app.db.query import QueryExecutor


class TestQueryExecutor:
    
    def test_apply_parameters(self, db_session):
        """Test applying parameters to SQL query"""
        # Create executor
        executor = QueryExecutor(db_session)
        
        # Test data
        sql_query = "SELECT * FROM customers WHERE id = :customer_id"
        parameters = [
            {
                "name": "customer_id",
                "value": "1",
                "type": "number"
            }
        ]
        
        # Call method
        modified_sql, params_dict = executor.apply_parameters(sql_query, parameters)
        
        # Assertions
        assert modified_sql == "SELECT * FROM customers WHERE id = :customer_id"
        assert "customer_id" in params_dict
        assert params_dict["customer_id"] == 1.0  # Converted to float
    
    def test_apply_parameters_with_date(self, db_session):
        """Test applying date parameters to SQL query"""
        # Create executor
        executor = QueryExecutor(db_session)
        
        # Test data
        sql_query = "SELECT * FROM orders WHERE order_date = :order_date"
        parameters = [
            {
                "name": "order_date",
                "value": "2023-01-01",
                "type": "date"
            }
        ]
        
        # Call method
        modified_sql, params_dict = executor.apply_parameters(sql_query, parameters)
        
        # Assertions
        assert modified_sql == "SELECT * FROM orders WHERE order_date = :order_date"
        assert "order_date" in params_dict
        assert params_dict["order_date"] == "2023-01-01"
    
    def test_execute_query_select(self, db_with_data):
        """Test executing a SELECT query"""
        # Create executor
        executor = QueryExecutor(db_with_data)
        
        # Execute a simple query
        result = executor.execute_query("SELECT * FROM customers WHERE id = :id", [
            {
                "name": "id",
                "value": "1",
                "type": "number"
            }
        ])
        
        # Assertions
        assert result["success"] == True
        assert result["row_count"] == 1
        assert "rows" in result
        assert result["rows"][0]["name"] == "Test Customer"
    
    def test_execute_query_update(self, db_with_data):
        """Test executing an UPDATE query"""
        # Create executor
        executor = QueryExecutor(db_with_data)
        
        # Execute an update query
        result = executor.execute_query(
            "UPDATE customers SET name = :new_name WHERE id = :id",
            [
                {
                    "name": "new_name",
                    "value": "Updated Name",
                    "type": "string"
                },
                {
                    "name": "id",
                    "value": "1",
                    "type": "number"
                }
            ]
        )
        
        # Assertions
        assert result["success"] == True
        assert "affected_rows" in result
        assert result["affected_rows"] == 1
        
        # Verify the update worked
        verify_result = executor.execute_query("SELECT name FROM customers WHERE id = 1")
        assert verify_result["rows"][0]["name"] == "Updated Name"
    
    def test_execute_query_error(self, db_with_data):
        """Test executing a query with an error"""
        # Create executor
        executor = QueryExecutor(db_with_data)
        
        # Execute a query with an error
        result = executor.execute_query("SELECT * FROM nonexistent_table")
        
        # Assertions
        assert result["success"] == False
        assert "error" in result
