from models.entities import Customer, Contract
from datetime import datetime


class CustomerBase:
    def __init__(self, session):
        self.session = session

    def create_customer(self, customer_data):
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

    def get_customer(self, customer_id):
        return self.session.query(Customer).filter_by(customer_id=customer_id).first()

    def get_all_customers(self):
        return self.session.query(Customer).all()

    def update_customer(self, customer_id, data):
        customer = self.session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        for key, value in data.items():
            setattr(customer, key, value)

        self.session.commit()

    def delete_customer(self, customer_id):
        customer = self.get_customer(customer_id)
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        self.session.delete(customer)
        self.session.commit()

    def find_without_contract(self):
        return self.session.query(Customer).outerjoin(Customer.contracts).filter(Contract.customer_id.is_(None)).all()
