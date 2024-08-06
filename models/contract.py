from sqlalchemy import Column, Integer, Sequence, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Contract(Base):
    """ Définition de la classe Contract qui sera la table dans la BD """
    __tablename__ = 'contracts'

    contract_id = Column(Integer, Sequence('contract_id_seq'), primary_key=True)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=True)
    is_signed = Column(Boolean, nullable=False, index=True)
    com_contact_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    ges_contact_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)

    com_contact = relationship('User', foreign_keys=[com_contact_id], back_populates='com_contracts')
    ges_contact = relationship('User', foreign_keys=[ges_contact_id], back_populates='ges_contracts')
    customer = relationship('Customer', back_populates='contracts')

    def __init__(self, contract_id, total_amount, remaining_amount, is_signed,
                 com_contact_id, ges_contact_id, customer_id):
        self.contract_id = contract_id
        self.customer_id = customer_id
        self.ges_contact_id = ges_contact_id
        self.com_contact_id = com_contact_id
        self.total_amount = total_amount
        self.remaining_amount = remaining_amount
        self.is_signed = is_signed
