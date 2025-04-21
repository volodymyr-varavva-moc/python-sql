import json
import os
from typing import Dict, List, Any, Optional
import logging

from openai import OpenAI
from app.core.config import settings
from app.llm.schema import SQL_FUNCTION_SCHEMA, DATABASE_SCHEMA

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        if settings.USE_LOCAL_AI:
            logger.info(f"Using LocalAI at {settings.LOCAL_AI_BASE_URL}")
            # For LocalAI, we don't need an API key but need the base URL
            self.client = OpenAI(
                base_url=settings.LOCAL_AI_BASE_URL,
                api_key="not-needed"  # LocalAI doesn't need a key, but OpenAI SDK requires one
            )
            # Default LocalAI model (can be changed based on what you have loaded)
            self.model = "mistral"
        else:
            # Check if we have an API key for OpenAI
            api_key = settings.OPENAI_API_KEY
            if not api_key or api_key == "your_openai_api_key" or api_key == "dummy_key_for_build":
                logger.warning("No valid OpenAI API key found. LLM features will not work.")
                self.client = None
            else:
                logger.info("Using OpenAI API")
                self.client = OpenAI(api_key=api_key)
            
            self.model = "gpt-3.5-turbo-1106"
    
    def generate_sql(self, query: str) -> Dict[str, Any]:
        """
        Generate SQL from a natural language query using function calling
        
        Args:
            query: Natural language query
            
        Returns:
            Dict containing sql_query, parameters, and explanation
        """
        # If no client is available, return a mock response
        if not self.client:
            logger.warning("Returning mock SQL response because LLM client is not configured")
            return {
                "sql_query": "SELECT * FROM customers LIMIT 5",
                "parameters": [],
                "explanation": "This is a mock response due to missing LLM configuration."
            }
            
        try:
            logger.info(f"Generating SQL for query: {query}")
            
            messages = [
                {"role": "system", "content": (
                    "You are a SQL expert that converts natural language queries into SQL. "
                    "Use the database schema provided to generate accurate SQL queries. "
                    "Always use parameterized queries to prevent SQL injection."
                )},
                {"role": "user", "content": f"Database schema: {json.dumps(DATABASE_SCHEMA)}\n\nConvert this query to SQL: {query}"}
            ]
            
            # If using LocalAI, we need to handle differently since function calling might 
            # not be fully supported or might work differently
            if settings.USE_LOCAL_AI:
                # We'll use a simpler approach compatible with most LLMs
                prompt = f"""
As a SQL expert, convert the following natural language query to a SQL query.
Use parameterized queries with named parameters to prevent SQL injection.

Database Schema:
{json.dumps(DATABASE_SCHEMA, indent=2)}

Natural Language Query: {query}

Return your answer in this JSON format:
{{
  "sql_query": "SELECT * FROM ... WHERE ... = :param",
  "parameters": [
    {{
      "name": "param",
      "value": "extracted_value",
      "type": "string|number|date"
    }}
  ],
  "explanation": "This query retrieves..."
}}
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                
                content = response.choices[0].message.content
                logger.info(f"Raw LLM Response: {content}")
                
                # Extract JSON from the response
                try:
                    # Find JSON content between triple backticks if it exists
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_content = content.split("```")[1].split("```")[0].strip()
                    else:
                        # Try to find JSON within the response
                        start_idx = content.find("{")
                        end_idx = content.rfind("}") + 1
                        if start_idx >= 0 and end_idx > start_idx:
                            json_content = content[start_idx:end_idx]
                        else:
                            json_content = content
                    
                    result = json.loads(json_content)
                    
                    # Ensure result has the expected keys
                    if "sql_query" not in result:
                        raise ValueError("Missing sql_query in result")
                    if "parameters" not in result:
                        result["parameters"] = []
                    if "explanation" not in result:
                        result["explanation"] = "SQL query generated from natural language."
                    
                    logger.info(f"Generated SQL: {result['sql_query']}")
                    return result
                except Exception as json_err:
                    logger.error(f"Error parsing JSON response: {str(json_err)}")
                    return {
                        "error": f"Failed to parse LLM response: {str(json_err)}",
                        "raw_response": content
                    }
            else:
                # For OpenAI, use function calling as before
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=[{"type": "function", "function": SQL_FUNCTION_SCHEMA}],
                    tool_choice={"type": "function", "function": {"name": "generate_sql_query"}}
                )
                
                result = None
                if response.choices[0].message.tool_calls:
                    function_call = response.choices[0].message.tool_calls[0]
                    result = json.loads(function_call.function.arguments)
                    logger.info(f"Generated SQL: {result['sql_query']}")
                else:
                    logger.warning("No function call in response")
                    return {"error": "Failed to generate SQL query"}
                    
                return result
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return {"error": str(e)}
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate the SQL query for security and correctness
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Dict with validation result and issues if any
        """
        # If no client is available, return a mock response
        if not self.client:
            logger.warning("Returning mock validation response because LLM client is not configured")
            return {
                "is_safe": True,
                "analysis": "This is a mock response. No validation was performed."
            }
            
        try:
            messages = [
                {"role": "system", "content": (
                    "You are a SQL security expert. Analyze the SQL query for: "
                    "1. SQL injection vulnerabilities "
                    "2. Syntax errors "
                    "3. Potential performance issues "
                    "4. Data security concerns"
                )},
                {"role": "user", "content": f"Validate this SQL query for security and correctness: {sql}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            analysis = response.choices[0].message.content
            
            # Simple heuristic to determine if there are serious issues
            is_safe = "injection" not in analysis.lower() and "vulnerability" not in analysis.lower()
            
            return {
                "is_safe": is_safe,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error validating SQL: {str(e)}")
            return {"is_safe": False, "analysis": f"Error during validation: {str(e)}"}
