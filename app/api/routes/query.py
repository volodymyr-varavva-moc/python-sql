from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.db.base import get_db
from app.api.deps import get_llm_client
from app.llm.openai_client import LLMClient
from app.db.query import QueryExecutor
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql_query: str
    parameters: List[Dict[str, Any]]
    explanation: str
    results: Dict[str, Any]

@router.post("/process", response_model=QueryResponse)
def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client)
) -> Dict[str, Any]:
    """
    Process a natural language query:
    1. Generate SQL using LLM
    2. Validate SQL
    3. Execute SQL
    4. Return results
    """
    # Generate SQL from natural language
    llm_response = llm_client.generate_sql(request.query)
    
    if "error" in llm_response:
        raise HTTPException(status_code=400, detail=llm_response["error"])
    
    # Validate SQL
    validation = llm_client.validate_sql(llm_response["sql_query"])
    if not validation["is_safe"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Generated SQL query failed security validation: {validation['analysis']}"
        )
    
    # Execute SQL query
    query_executor = QueryExecutor(db)
    results = query_executor.execute_query(
        llm_response["sql_query"], 
        llm_response["parameters"]
    )
    
    if not results["success"]:
        raise HTTPException(status_code=400, detail=results["error"])
    
    # Return results
    return {
        "sql_query": llm_response["sql_query"],
        "parameters": llm_response["parameters"],
        "explanation": llm_response["explanation"],
        "results": results
    }
