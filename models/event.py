from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from config import Base


class Event(Base):
    """ Définition de la classe Event qui sera la table dans la BD """

    __tablename__ = 'events'

    event_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String, nullable=False)
    customer_id = Column(Integer, nullable=True)
    ges_contact_id = Column(Integer, nullable=True)
    sup_contact_id = Column(Integer, nullable=True)

    customer = relationship('Customer', back_populates='events')
    ges_contact = relationship('User', foreign_keys=[ges_contact_id], back_populates='ges_events')
    sup_contact = relationship('User', foreign_keys=[sup_contact_id], back_populates='sup_events')

    def __init__(self, name, start_date, end_date, location, attendees, notes, customer_id=None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.attendees = attendees
        self.notes = notes
        self.customer_id = customer_id
