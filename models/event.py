from sqlalchemy import Column, Integer, Sequence, String, DateTime
from .base import Base


class Event(Base):
    __tablename__ = 'events'

    event_id = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    customer_id = Column(Integer, nullable=False)
    ges_contact_id = Column(Integer, nullable=False)
    sup_contact_id = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(250), nullable=False)
    attendees = Column(Integer(20), nullable=False)
    notes = Column(String(1000), nullable=False)
