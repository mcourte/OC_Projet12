from models.entities import Customer, Contract
from datetime import datetime
from .decorator import is_authenticated, is_admin, is_commercial


class CustomerBase:
    def __init__(self, session):
        self.session = session

    @is_authenticated
    @is_admin
    @is_commercial
    def create_customer(self, customer_data):
        """Permet de créer un Client"""
        customer = Customer(
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            email=customer_data['email'],
            phone=customer_data['phone'],
            company_name=customer_data['company_name'],
            creation_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
            commercial_id=customer_data.get('commercial_id')
        )
        self.session.add(customer)
        self.session.commit()
        return customer

    @is_authenticated
    @is_admin
    @is_commercial
    def get_customer(self, customer_id):
        """Permet de retrouver un client via son ID"""
        return self.session.query(Customer).filter_by(customer_id=customer_id).first()

    @is_authenticated
    def get_all_customers(self):
        """Permet de retourner la liste de tous les CLients"""
        return self.session.query(Customer).all()

    @is_authenticated
    @is_admin
    @is_commercial
    def update_customer(self, customer_id, data):
        """Permet de mettre à jour le profil d'un Client via son ID"""
        customer = self.session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        for key, value in data.items():
            setattr(customer, key, value)

        self.session.commit()

    @is_authenticated
    @is_admin
    @is_commercial
    def find_without_contract(self):
        """Permet de lister tous les clients qui n'ont pas de contract associé"""
        return self.session.query(Customer).outerjoin(Customer.contracts).filter(Contract.customer_id.is_(None)).all()
