from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from . import models, schemas, crud
from .database import SessionLocal, engine, Base, test_connection

# Initialize FastAPI app
app = FastAPI(
    title="Energy Trading Platform",
    description="FastAPI-based energy commodities trading platform with Azure SQL Database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create database tables on first request instead of startup
tables_created = False

def ensure_tables_exist():
    """Ensure database tables exist, with retry logic"""
    global tables_created
    if not tables_created:
        try:
            Base.metadata.create_all(bind=engine)
            tables_created = True
            print("Database tables created successfully")
        except Exception as e:
            print(f"Failed to create database tables: {e}")
            # Don't raise exception, let the app continue and retry later

# Dependency to get database session
def get_db():
    ensure_tables_exist()  # Ensure tables exist before each database operation
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", summary="Root endpoint")
async def read_root():
    """Root endpoint returning API information"""
    return {
        "message": "Energy Trading Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=schemas.HealthCheck, summary="Health check")
async def health_check():
    """Health check endpoint to verify API and database connectivity"""
    ensure_tables_exist()  # Try to create tables if needed
    db_connected = test_connection()
    
    return schemas.HealthCheck(
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.utcnow(),
        database_connected=db_connected
    )

@app.post("/trades/", response_model=schemas.Trade, summary="Create a new trade")
async def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    """
    Create a new energy commodity trade
    
    - **commodity**: Type of energy commodity (electricity, oil, gas, etc.)
    - **price**: Price per unit (must be positive)
    - **quantity**: Quantity to trade (must be positive)
    - **side**: Trade side (buy or sell)
    - **trader_id**: Trader identification
    """
    try:
        return crud.create_trade(db=db, trade=trade)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create trade: {str(e)}")

@app.get("/trades/", response_model=schemas.TradeResponse, summary="Get trades")
async def get_trades(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of trades to return"),
    offset: int = Query(0, ge=0, description="Number of trades to skip"),
    commodity: Optional[str] = Query(None, description="Filter by commodity type"),
    trader_id: Optional[str] = Query(None, description="Filter by trader ID"),
    side: Optional[str] = Query(None, description="Filter by trade side (buy/sell)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve trades with optional filtering and pagination
    
    - **limit**: Maximum number of trades to return (1-1000)
    - **offset**: Number of trades to skip for pagination
    - **commodity**: Filter by specific commodity type
    - **trader_id**: Filter by specific trader
    - **side**: Filter by trade side (buy or sell)
    """
    try:
        trades = crud.get_trades(
            db=db, 
            limit=limit, 
            offset=offset,
            commodity=commodity,
            trader_id=trader_id,
            side=side
        )
        
        total = crud.get_trades_count(
            db=db,
            commodity=commodity,
            trader_id=trader_id,
            side=side
        )
        
        return schemas.TradeResponse(trades=trades, total=total)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve trades: {str(e)}")

@app.get("/trades/{trade_id}", response_model=schemas.Trade, summary="Get trade by ID")
async def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a specific trade by its ID"""
    trade = crud.get_trade_by_id(db=db, trade_id=trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.get("/trades/commodity/{commodity}", response_model=List[schemas.Trade], summary="Get recent trades by commodity")
async def get_trades_by_commodity(
    commodity: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of trades to return"),
    db: Session = Depends(get_db)
):
    """Get recent trades for a specific commodity"""
    try:
        trades = crud.get_recent_trades_by_commodity(db=db, commodity=commodity, limit=limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve commodity trades: {str(e)}")

@app.get("/trades/trader/{trader_id}", response_model=List[schemas.Trade], summary="Get trades by trader")
async def get_trades_by_trader(
    trader_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of trades to return"),
    db: Session = Depends(get_db)
):
    """Get trades for a specific trader"""
    try:
        trades = crud.get_trader_trades(db=db, trader_id=trader_id, limit=limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve trader trades: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
