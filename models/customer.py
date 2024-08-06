from sqlalchemy import Column, Integer, Sequence, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base


class Customer(Base):
    """ Définition de la classe Customer qui sera la table dans la BD """

    __tablename__ = 'customers'

    customer_id = Column(Integer, Sequence('customer_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(254), nullable=False, index=True)
    phone = Column(Integer, nullable=False, index=True)
    company_name = Column(String(100), nullable=False, index=True)
    creation_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    com_contact_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    contracts = relationship('Contract', back_populates='customer')
    events = relationship('Event', back_populates='customer')

    def __init__(self, first_name, last_name, email, phone, company_name,
                 creation_time, update_time, com_contact_id):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.company_name = company_name
        self.creation_time = creation_time
        self.update_time = update_time
        self.com_contact_id = com_contact_id
