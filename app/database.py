import os
import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import pyodbc
import struct
from dotenv import load_dotenv

load_dotenv()

# Database configuration
server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
use_managed_identity = os.getenv("USE_MANAGED_IDENTITY", "False").lower() == "true"
client_id = os.getenv("AZURE_CLIENT_ID")  # For User Assigned Managed Identity

# SQLAlchemy Base
Base = declarative_base()

def get_access_token():
    """Get Azure AD access token for SQL Database"""
    try:
        if client_id:
            # Use User Assigned Managed Identity
            credential = ManagedIdentityCredential(client_id=client_id)
        else:
            # Use System Assigned Managed Identity or DefaultAzureCredential
            credential = DefaultAzureCredential()
        
        # Get token for Azure SQL Database
        token = credential.get_token("https://database.windows.net/.default")
        return token.token
    except Exception as e:
        print(f"Failed to get access token: {e}")
        raise

def get_connection_string():
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    use_managed_identity = os.getenv("USE_MANAGED_IDENTITY", "false").lower() == "true"
    
    if use_managed_identity:
        # Use Managed Identity with access token - NO Authentication parameter
        connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    else:
        # Use username/password - NO Access Token
        username = os.getenv("AZURE_SQL_USERNAME")
        password = os.getenv("AZURE_SQL_PASSWORD")
        connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    
    return connection_string

def create_database_engine():
    """Create SQLAlchemy engine with appropriate authentication"""
    
    connection_string = get_connection_string()
    
    # Create engine with retry settings for serverless databases
    engine = create_engine(
        connection_string,
        echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=3600,   # Recycle connections every hour
        connect_args={
            "timeout": 60,  # Connection timeout for database wake-up
        }
    )
    
    if use_managed_identity:
        # Set up event listener to inject access token for managed identity connections
        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            # Get fresh token for each connection
            token = get_access_token()
            
            # Convert token to bytes and create token struct
            token_bytes = token.encode("utf-16-le")
            token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
            
            # Set the token in connection attributes
            cparams["attrs_before"] = {1256: token_struct}  # SQL_COPT_SS_ACCESS_TOKEN
    
    return engine

# Create engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection with retry logic for serverless databases"""
    max_retries = 5
    retry_delay = 30  # seconds - time for database to wake up
    
    for attempt in range(max_retries):
        try:
            print(f"Database connection attempt {attempt + 1}/{max_retries}")
            with engine.connect() as connection:
                result = connection.execute("SELECT 1 as test")
                print(f"Database connection successful: {result.fetchone()}")
                return True
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds... (Database may be waking up)")
                time.sleep(retry_delay)
            else:
                print("All database connection attempts failed")
                return False
    
    return False


if __name__ == "__main__":
    # Test connection when running this file directly
    test_connection()
