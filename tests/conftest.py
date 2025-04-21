import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict, Generator, Any
import datetime
from unittest.mock import MagicMock, patch

from app.db.base import Base
from app.db.models import Customer, Order
from app.llm.openai_client import LLMClient
from app.db.init_db import init_db

# Use in-memory SQLite for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database for each test
    """
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop the tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_with_data(db_session):
    """
    Creates a database with sample data for testing
    """
    # Add sample data
    customers = [
        Customer(
            id=1,
            name="Test Customer",
            email="test@example.com",
            phone="555-1234",
            address="123 Test St"
        ),
        Customer(
            id=2,
            name="Another Customer",
            email="another@example.com",
            phone="555-5678",
            address="456 Test Ave"
        )
    ]
    
    db_session.add_all(customers)
    db_session.commit()
    
    today = datetime.date.today()
    orders = [
        Order(
            id=1,
            customer_id=1,
            order_date=today - datetime.timedelta(days=5),
            total_amount=100.0,
            status="delivered"
        ),
        Order(
            id=2,
            customer_id=1,
            order_date=today - datetime.timedelta(days=2),
            total_amount=75.50,
            status="shipped"
        ),
        Order(
            id=3,
            customer_id=2,
            order_date=today,
            total_amount=200.0,
            status="pending"
        )
    ]
    
    db_session.add_all(orders)
    db_session.commit()
    
    return db_session


@pytest.fixture
def mock_llm_client():
    """
    Creates a mock LLM client for testing
    """
    mock_client = MagicMock(spec=LLMClient)
    
    # Mock the generate_sql method
    mock_client.generate_sql.return_value = {
        "sql_query": "SELECT * FROM customers WHERE id = :customer_id",
        "parameters": [
            {
                "name": "customer_id",
                "value": "1",
                "type": "number"
            }
        ],
        "explanation": "This query retrieves a customer with ID 1"
    }
    
    # Mock the validate_sql method
    mock_client.validate_sql.return_value = {
        "is_safe": True,
        "analysis": "The query is safe to execute."
    }
    
    return mock_client


@pytest.fixture
def app_client():
    """
    Creates a test client for the FastAPI app
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Patch the dependencies to use our test fixtures
    with patch("app.api.routes.query.get_db") as mock_get_db, \
         patch("app.api.routes.query.get_llm_client") as mock_get_llm_client:
        
        # Configure the mocks to return our fixtures
        mock_get_db.return_value = next(db_with_data(db_session()))
        mock_get_llm_client.return_value = mock_llm_client()
        
        client = TestClient(app)
        yield client
