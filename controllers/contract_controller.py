from models.entities import Contract


class ContractBase:
    def __init__(self, session):
        self.session = session

    def create_contract(self, data):
        contract = Contract(
            description=data['description'],
            total_amount=data['total_amount'],
            remaining_amount=data.get('remaining_amount'),
            state=data.get('state', 'C'),
            customer_id=data['customer_id']
        )
        self.session.add(contract)
        self.session.commit()
        return contract

    def get_contract(self, contract_id):
        return self.session.query(Contract).filter_by(contract_id=contract_id).first()

    def get_all_contracts(self):
        return self.session.query(Contract).all()

    def update_contract(self, contract_id, data):
        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Contract not found")

        for key, value in data.items():
            setattr(contract, key, value)

        self.session.commit()

    def delete_contract(self, contract_id):
        contract = self.get_contract(contract_id)
        if not contract:
            raise ValueError("Contract not found")

        self.session.delete(contract)
        self.session.commit()

    def find_by_customer(self, customer_id):
        return self.session.query(Contract).filter_by(customer_id=customer_id).all()

    def find_by_state(self, state):
        return self.session.query(Contract).filter_by(state=state).all()
