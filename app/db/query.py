from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self, db: Session):
        self.db = db
    
    def apply_parameters(self, sql_query: str, parameters: List[Dict[str, Any]]) -> tuple:
        """
        Apply parameters to the SQL query template
        
        Args:
            sql_query: The SQL query with placeholders
            parameters: List of parameters with name, value and type
            
        Returns:
            Tuple of (query with named parameters, parameters dict)
        """
        params_dict = {}
        
        # Convert SQL to use named parameters
        modified_sql = sql_query
        
        for param in parameters:
            param_name = param["name"]
            param_value = param["value"]
            param_type = param["type"]
            
            # Convert parameter value based on type
            if param_type == "number":
                try:
                    param_value = float(param_value)
                except ValueError:
                    logger.warning(f"Could not convert {param_value} to number, using as string")
            
            # Add to parameters dictionary
            params_dict[param_name] = param_value
            
            # For date parameters, ensure proper formatting
            if param_type == "date":
                if not (param_value.startswith("'") and param_value.endswith("'")):
                    param_value = f"'{param_value}'"
        
        return modified_sql, params_dict
    
    def execute_query(self, sql_query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Execute SQL query with parameters and return results
        
        Args:
            sql_query: SQL query to execute
            parameters: Optional list of parameters
            
        Returns:
            Dict with results or error message
        """
        try:
            params_dict = {}
            if parameters:
                sql_query, params_dict = self.apply_parameters(sql_query, parameters)
            
            # Execute query
            logger.info(f"Executing query: {sql_query} with params: {params_dict}")
            result = self.db.execute(text(sql_query), params_dict)
            
            # Get column names
            if result.returns_rows:
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                return {
                    "success": True,
                    "columns": list(columns),
                    "rows": rows,
                    "row_count": len(rows)
                }
            else:
                row_count = result.rowcount
                return {
                    "success": True,
                    "affected_rows": row_count,
                    "message": f"Query executed successfully. {row_count} rows affected."
                }
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
