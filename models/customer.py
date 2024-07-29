from sqlalchemy import Column, Integer, String, Sequence, DateTime
from .base import Base
from sqlalchemy.sql import func


class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, Sequence('customer_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(254), nullable=False)
    phone = Column(Integer(20), nullable=False)
    company_name = Column(String(100), nullable=False)
    creation_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    com_contact_id = Column(Integer, nullable=False)
