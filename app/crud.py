from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from typing import List, Optional

def create_trade(db: Session, trade: schemas.TradeCreate) -> models.Trade:
    """
    Create a new trade in the database
    """
    db_trade = models.Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def get_trades(
    db: Session, 
    limit: int = 100, 
    offset: int = 0,
    commodity: Optional[str] = None,
    trader_id: Optional[str] = None,
    side: Optional[str] = None
) -> List[models.Trade]:
    """
    Retrieve trades with optional filtering
    """
    query = db.query(models.Trade)
    
    # Apply filters if provided
    if commodity:
        query = query.filter(models.Trade.commodity == commodity.lower())
    if trader_id:
        query = query.filter(models.Trade.trader_id == trader_id)
    if side:
        query = query.filter(models.Trade.side == side.lower())
    
    # Order by timestamp (most recent first) and apply pagination
    return query.order_by(desc(models.Trade.timestamp)).offset(offset).limit(limit).all()

def get_trade_by_id(db: Session, trade_id: int) -> Optional[models.Trade]:
    """
    Get a specific trade by ID
    """
    return db.query(models.Trade).filter(models.Trade.id == trade_id).first()

def get_trades_count(
    db: Session,
    commodity: Optional[str] = None,
    trader_id: Optional[str] = None,
    side: Optional[str] = None
) -> int:
    """
    Get total count of trades with optional filtering
    """
    query = db.query(models.Trade)
    
    # Apply same filters as get_trades
    if commodity:
        query = query.filter(models.Trade.commodity == commodity.lower())
    if trader_id:
        query = query.filter(models.Trade.trader_id == trader_id)
    if side:
        query = query.filter(models.Trade.side == side.lower())
    
    return query.count()

def get_recent_trades_by_commodity(db: Session, commodity: str, limit: int = 10) -> List[models.Trade]:
    """
    Get recent trades for a specific commodity
    """
    return db.query(models.Trade).filter(
        models.Trade.commodity == commodity.lower()
    ).order_by(desc(models.Trade.timestamp)).limit(limit).all()

def get_trader_trades(db: Session, trader_id: str, limit: int = 50) -> List[models.Trade]:
    """
    Get trades for a specific trader
    """
    return db.query(models.Trade).filter(
        models.Trade.trader_id == trader_id
    ).order_by(desc(models.Trade.timestamp)).limit(limit).all()
