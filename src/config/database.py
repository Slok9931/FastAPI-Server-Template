from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import time
from src.config.settings import settings

# Add retry logic for database connection
def create_database_engine(max_retries=5, retry_delay=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_timeout=settings.database_pool_timeout,
                pool_recycle=settings.database_pool_recycle,
                echo=settings.debug and settings.is_development
            )
            # Test the connection
            engine.connect()
            print(f"Database connection successful on attempt {attempt + 1}")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise e

engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()