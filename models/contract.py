from sqlalchemy import Column, Integer, Sequence, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Contract(Base):
    __tablename__ = 'contracts'

    contract_id = Column(Integer, Sequence('contract_id_seq'), primary_key=True)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=True)
    is_signed = Column(Boolean, nullable=False, index=True)
    com_contact_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    ges_contact_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)

    com_contact = relationship("User", foreign_keys=[com_contact_id], back_populates="com_contracts")
    ges_contact = relationship("User", foreign_keys=[ges_contact_id], back_populates="ges_contracts")
    customer = relationship("Customer", back_populates="contracts")
