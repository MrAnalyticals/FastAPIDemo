import os
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

def create_connection_string():
    """Create appropriate connection string based on authentication method"""
    
    if use_managed_identity:
        # Managed Identity authentication
        print("Using Azure Managed Identity for database authentication")
        
        # Get access token
        access_token = get_access_token()
        
        # Create connection string with access token
        connection_string = (
            f"mssql+pyodbc://@{server}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
            "&Authentication=ActiveDirectoryMsi"
        )
        
        # We'll set the access token in the connection event
        return connection_string, access_token
    else:
        # SQL Authentication (for local development)
        print("Using SQL Authentication for database connection")
        username = os.getenv("AZURE_SQL_USERNAME")
        password = os.getenv("AZURE_SQL_PASSWORD")
        
        if not username or not password:
            raise ValueError("Database credentials not found. Set AZURE_SQL_USERNAME and AZURE_SQL_PASSWORD environment variables.")
        
        connection_string = (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )
        
        return connection_string, None

def create_database_engine():
    """Create SQLAlchemy engine with appropriate authentication"""
    
    connection_string, access_token = create_connection_string()
    
    # Create engine
    engine = create_engine(
        connection_string,
        echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=3600,   # Recycle connections every hour
    )
    
    if use_managed_identity and access_token:
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
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1 as test")
            print(f"Database connection successful: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection when running this file directly
    test_connection()
