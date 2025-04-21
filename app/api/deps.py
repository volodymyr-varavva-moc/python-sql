from typing import Generator
from app.db.base import SessionLocal, get_db
from app.llm.openai_client import LLMClient

def get_llm_client() -> LLMClient:
    """
    Dependency for getting the LLM client.
    """
    return LLMClient()
