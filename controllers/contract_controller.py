from models.entities import Contract
from .decorator import is_authenticated, is_admin, is_commercial, is_gestion


class ContractBase:
    def __init__(self, session):
        self.session = session

    @is_authenticated
    @is_admin
    @is_gestion
    def create_contract(self, data):
        """Permet de créer un contrat
        Informations à fournir : description, montant total, reste à payer, statut, l'ID du client"""
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

    @is_authenticated
    @is_admin
    @is_gestion
    def get_contract(self, contract_id):
        """ Permet de retrouver un contrat via son ID"""
        return self.session.query(Contract).filter_by(contract_id=contract_id).first()

    def get_all_contracts(self):
        """ Permet de retourner la liste de tous les contrats"""
        return self.session.query(Contract).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def update_contract(self, contract_id, data):
        """Permet de mettre à jour un contrat"""
        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Il n'existe pas de Contrat avec cet ID")

        for key, value in data.items():
            setattr(contract, key, value)

        self.session.commit()

    @is_authenticated
    @is_admin
    @is_gestion
    def find_by_customer(self, customer_id):
        """Permet de retrouver les contrats affiliés à un Client"""
        return self.session.query(Contract).filter_by(customer_id=customer_id).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def find_by_state(self, state):
        """Permet de lister les Contrats via leurs statuts"""
        return self.session.query(Contract).filter_by(state=state).all()

    @is_authenticated
    @is_admin
    @is_gestion
    @is_commercial
    def find_by_paiement_state(self, paiement_state):
        """Permet de lister les Contrats via leurs statuts de paiement"""
        return self.session.query(Contract).filter_by(paiement_state=paiement_state).all()
