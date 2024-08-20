from models.entities import Contract, Paiement
from controllers.decorator import is_authenticated, is_admin, is_commercial, is_gestion
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from views.data_view import DataView


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
            customer_id=data['customer_id'],
            paiement_state=data.get('paiement_state', 'N')
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
    @is_commercial
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
    def state_signed(self):
        """Permet de lister les Contrats via leurs statuts"""
        return self.session.query(Contract).filter_by(state="S").all()

    @is_authenticated
    @is_admin
    @is_gestion
    @is_commercial
    def find_by_paiement_state(self, paiement_state):
        """Permet de lister les Contrats via leurs statuts de paiement"""
        return self.session.query(Contract).filter_by(paiement_state=paiement_state).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def add_paiement(self, ref_contract, data) -> None:
        """Create a new paiement for the contract in the database"""
        contract = Contract.find_by_ref(self.session, ref_contract)
        if int(data['amount']) > contract.remaining_amount:
            DataView.display_error_contract_amount()
            raise ValueError("Le montant dépasse le restant dû")
        else:
            paiement = Paiement(
                ref=data['ref'], amount=data['amount'], contract_id=contract.contract_id)
            if int(data['amount']) == contract.remaining_amount:
                contract.paiement_state = 'S'
                self.session.add(contract)
            try:
                self.session.add(paiement)
                self.session.commit()
                DataView.display_data_update()
            except IntegrityError:
                self.session.rollback()
                DataView.display_error_unique()

    @is_authenticated
    @is_admin
    @is_gestion
    def signed(self, ref_contract) -> None:
        """
        Update the state of the contract to 'S' (Signed).

        Args:
            ref_contract (int): ID of the contract.
        """
        try:
            contract = Contract.find_by_ref(self.session, ref_contract)
        except NoResultFound:
            raise ValueError(f"Aucun contrat trouvé avec la référence {ref_contract}")

        contract.state = 'S'
        self.session.add(contract)
        self.session.commit()
        DataView.display_data_update()
