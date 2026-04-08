from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the database URL from the environment
database_url = os.getenv("DATABASE_URL")

# Create the database engine — check_same_thread=False is required for SQLite with FastAPI
engine = create_engine(database_url, connect_args={"check_same_thread": False})

# SessionLocal is a factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, bind=engine)

# Base is the parent class all models inherit from so SQLAlchemy knows about them
Base = declarative_base()

# Dependency used in routes to get a database session, then close it when done
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provide the session to the route handler
    finally:
        db.close()  # Always close the session after the request finishes
