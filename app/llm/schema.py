# Schema for OpenAI function calling

SQL_FUNCTION_SCHEMA = {
    "name": "generate_sql_query",
    "description": "Generates an SQL query based on a natural language request",
    "parameters": {
        "type": "object",
        "properties": {
            "sql_query": {
                "type": "string",
                "description": "The SQL query string that corresponds to the natural language request"
            },
            "parameters": {
                "type": "array",
                "description": "List of parameters extracted from the query that need to be filled in",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Parameter name"
                        },
                        "value": {
                            "type": "string",
                            "description": "Parameter value extracted from the query"
                        },
                        "type": {
                            "type": "string",
                            "description": "Data type of the parameter (string, number, date)",
                            "enum": ["string", "number", "date"]
                        }
                    },
                    "required": ["name", "value", "type"]
                }
            },
            "explanation": {
                "type": "string",
                "description": "Explanation of what the SQL query does"
            }
        },
        "required": ["sql_query", "parameters", "explanation"]
    }
}

DATABASE_SCHEMA = {
    "tables": [
        {
            "name": "customers",
            "description": "Contains customer information",
            "columns": [
                {"name": "id", "type": "INTEGER", "description": "Unique identifier for the customer"},
                {"name": "name", "type": "STRING", "description": "Customer's full name"},
                {"name": "email", "type": "STRING", "description": "Customer's email address"},
                {"name": "phone", "type": "STRING", "description": "Customer's phone number"},
                {"name": "address", "type": "STRING", "description": "Customer's address"}
            ]
        },
        {
            "name": "orders",
            "description": "Contains order information",
            "columns": [
                {"name": "id", "type": "INTEGER", "description": "Unique identifier for the order"},
                {"name": "customer_id", "type": "INTEGER", "description": "Foreign key to customers table"},
                {"name": "order_date", "type": "DATE", "description": "Date when the order was placed"},
                {"name": "total_amount", "type": "FLOAT", "description": "Total amount of the order"},
                {"name": "status", "type": "STRING", "description": "Current status of the order (pending, processing, shipped, delivered)"},
                {"name": "notes", "type": "TEXT", "description": "Additional notes about the order"}
            ]
        }
    ],
    "relationships": [
        {
            "type": "1:N",
            "description": "One customer can have many orders",
            "tables": ["customers", "orders"],
            "keys": ["id", "customer_id"]
        }
    ]
}
