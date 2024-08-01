from sqlalchemy import Column, Integer, Sequence, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


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

    # Relations entre les différents modèles
    contracts = relationship("Contract", back_populates="customer")
    events = relationship("Event", back_populates="customer")
