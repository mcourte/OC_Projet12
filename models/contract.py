from sqlalchemy import Column, Integer, Sequence, Float, Boolean
from .base import Base


class Contract(Base):
    __tablename__ = 'contracts'

    contract_id = Column(Integer, Sequence('contract_id_seq'), primary_key=True)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=True)
    is_signed = Column(Boolean, nullable=False)
    com_contact_id = Column(Integer, nullable=False)
    ges_contact_id = Column(Integer, nullable=False)
