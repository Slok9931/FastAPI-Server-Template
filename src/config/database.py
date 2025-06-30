from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection() -> bool:
    """Test database connection and return success status"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test the connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            
            print(f"Database connection successful on attempt {retry_count + 1}")
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            retry_count += 1
            logger.error(f"Database connection attempt {retry_count} failed: {e}")
            print(f"Database connection attempt {retry_count} failed: {e}")
            
            if retry_count >= max_retries:
                logger.error("All database connection attempts failed")
                print("❌ Database connection failed after all retries")
                return False
            
            # Wait before retrying (optional)
            import time
            time.sleep(2)
    
    return False

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        print(f"❌ Failed to create database tables: {e}")
        return False

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
        print("✅ Database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        print(f"❌ Failed to drop database tables: {e}")
        return False