from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from .database import Base

class Trade(Base):
    """
    Trade model representing energy commodity trades
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String(50), index=True, nullable=False)  # e.g., "electricity", "oil", "gas"
    price = Column(Float, nullable=False)  # Price per unit
    quantity = Column(Float, nullable=False)  # Quantity traded
    side = Column(String(10), nullable=False)  # "buy" or "sell"
    trader_id = Column(String(100), nullable=False)  # Trader identification
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Add indexes for common query patterns
    __table_args__ = (
        Index('idx_commodity_timestamp', 'commodity', 'timestamp'),
        Index('idx_trader_timestamp', 'trader_id', 'timestamp'),
        Index('idx_side_timestamp', 'side', 'timestamp'),
    )

    def __repr__(self):
        return f"<Trade(id={self.id}, commodity='{self.commodity}', price={self.price}, quantity={self.quantity}, side='{self.side}', trader_id='{self.trader_id}')>"
