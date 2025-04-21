import datetime
import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the models and base only when necessary
# This helps avoid issues when running the script in different environments
from app.db.base import Base
from app.db.models import Customer, Order

def get_engine():
    """Get database engine with environment-aware configuration"""
    # Get database URL from environment or use default
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    logger.info(f"Using database: {database_url}")
    
    # Create engine with appropriate connect_args for SQLite
    if database_url.startswith('sqlite'):
        return create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        return create_engine(database_url)

def init_db(db: Session, engine) -> None:
    """Initialize database with tables and sample data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
        # Check if there's already data by safely querying
        inspector = inspect(engine)
        if "customers" in inspector.get_table_names():
            try:
                customer_count = db.query(Customer).count()
                if customer_count > 0:
                    logger.info("Database already contains data, skipping initialization")
                    return
            except Exception as e:
                logger.warning(f"Error checking existing data: {e}")
                # Continue with initialization
        
        # Sample data - Customers
        customers = [
            Customer(
                name="John Doe",
                email="john@example.com",
                phone="555-1234",
                address="123 Main St, Anytown USA"
            ),
            Customer(
                name="Jane Smith",
                email="jane@example.com",
                phone="555-5678",
                address="456 Elm St, Somewhere USA"
            ),
            Customer(
                name="Robert Johnson",
                email="robert@example.com",
                phone="555-9012",
                address="789 Oak St, Nowhere USA"
            ),
            Customer(
                name="Emily Davis",
                email="emily@example.com",
                phone="555-3456",
                address="101 Pine St, Elsewhere USA"
            ),
            Customer(
                name="Michael Wilson",
                email="michael@example.com",
                phone="555-7890",
                address="202 Maple St, Anywhere USA"
            )
        ]
        
        db.add_all(customers)
        db.commit()
        logger.info("Added sample customers")
        
        # Sample data - Orders
        today = datetime.date.today()
        orders = [
            Order(
                customer_id=1,
                order_date=today - datetime.timedelta(days=10),
                total_amount=125.99,
                status="delivered"
            ),
            Order(
                customer_id=1,
                order_date=today - datetime.timedelta(days=5),
                total_amount=89.50,
                status="shipped"
            ),
            Order(
                customer_id=2,
                order_date=today - datetime.timedelta(days=7),
                total_amount=45.00,
                status="delivered"
            ),
            Order(
                customer_id=3,
                order_date=today - datetime.timedelta(days=2),
                total_amount=199.99,
                status="processing"
            ),
            Order(
                customer_id=3,
                order_date=today - datetime.timedelta(days=20),
                total_amount=25.50,
                status="delivered"
            ),
            Order(
                customer_id=4,
                order_date=today - datetime.timedelta(days=15),
                total_amount=75.25,
                status="delivered"
            ),
            Order(
                customer_id=5,
                order_date=today,
                total_amount=55.99,
                status="pending"
            )
        ]
        
        db.add_all(orders)
        db.commit()
        
        logger.info("Database initialized with sample data")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        raise


def main() -> None:
    """Initialize the database with sample data."""
    logger.info("Creating initial data")
    
    try:
        # Get engine
        engine = get_engine()
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            init_db(db, engine)
            logger.info("Initial data created successfully")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
