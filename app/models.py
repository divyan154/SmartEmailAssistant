from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
import datetime

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    date_received = Column(DateTime, default=datetime.datetime.utcnow)
    sentiment = Column(String, nullable=True)   # will add on Day 2
    priority = Column(String, nullable=True)    # will add on Day 2
    extracted_info = Column(Text, nullable=True) # JSON-like data
    response = Column(Text, nullable=True)
    status = Column(String, default="pending")
