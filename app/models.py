from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    amount = Column(Float)
    game_type = Column(String)
    confirmed = Column(Boolean, default=False)
    entry_code = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_winner = Column(Boolean, default=False)
    sms_id = Column(String, nullable=True)


class DrawEvent(Base):
    __tablename__ = "draw_events"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    phone = Column(String)
    entry_code = Column(String)
    draw_time = Column(DateTime(timezone=True), server_default=func.now())
    sms_id = Column(String)
    payout_status = Column(String, default="pending")  # pending, success, failed