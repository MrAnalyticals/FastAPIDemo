from fastapi import FastAPI
from datetime import datetime

# Simple FastAPI app for initial testing without database
app = FastAPI(
    title="Energy Trading Platform - Local Test",
    description="FastAPI-based energy commodities trading platform (Test Mode)",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    """Root endpoint returning API information"""
    return {
        "message": "Energy Trading Platform API - Test Mode",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Basic health check without database"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database_connected": "not_tested",
        "mode": "local_test"
    }

@app.get("/test/trade")
async def test_trade_endpoint():
    """Test endpoint to simulate trade data structure"""
    sample_trade = {
        "id": 1,
        "commodity": "electricity",
        "price": 45.50,
        "quantity": 100.0,
        "side": "buy",
        "trader_id": "trader_001",
        "timestamp": datetime.utcnow().isoformat()
    }
    return {
        "message": "Sample trade data structure",
        "sample_trade": sample_trade
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
