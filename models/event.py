from sqlalchemy import Column, Integer, Sequence, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Event(Base):
    """ Définition de la classe Event qui sera la table dans la BD"""
    __tablename__ = 'events'

    event_id = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
    ges_contact_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    sup_contact_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(250), nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String(1000), nullable=False)

    # Relation entre les différents models
    events = relationship("Event", back_populates="customer")
