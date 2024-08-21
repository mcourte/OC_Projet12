from models.entities import Contract, Paiement
from controllers.decorator import is_authenticated, is_admin, is_commercial, is_gestion
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from views.data_view import DataView


class ContractBase:
    """
    Classe de base pour la gestion des contrats, permettant de créer, récupérer,
    mettre à jour et gérer les paiements associés à un contrat.
    """

    def __init__(self, session):
        """
        Initialise la classe ContractBase avec une session SQLAlchemy.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        """
        self.session = session

    @is_authenticated
    @is_admin
    @is_gestion
    def create_contract(self, data):
        """
        Permet de créer un contrat.

        Paramètres :
        ------------
        data : dict
            Un dictionnaire contenant les informations du contrat à créer.

        Retourne :
        ----------
        Contract : Le contrat créé.
        """
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
        """
        Permet de retrouver un contrat via son ID.

        Paramètres :
        ------------
        contract_id : int
            L'ID du contrat à retrouver.

        Retourne :
        ----------
        Contract : Le contrat correspondant à l'ID, ou None s'il n'existe pas.
        """
        return self.session.query(Contract).filter_by(contract_id=contract_id).first()

    def get_all_contracts(self):
        """
        Permet de retourner la liste de tous les contrats.

        Retourne :
        ----------
        list[Contract] : La liste de tous les contrats.
        """
        return self.session.query(Contract).all()

    @is_authenticated
    @is_admin
    @is_gestion
    @is_commercial
    def update_contract(self, contract_id, data):
        """
        Permet de mettre à jour un contrat existant.

        Paramètres :
        ------------
        contract_id : int
            L'ID du contrat à mettre à jour.
        data : dict
            Un dictionnaire contenant les nouvelles valeurs pour les attributs du contrat.

        Exceptions :
        ------------
        ValueError :
            Levée si aucun contrat n'est trouvé avec l'ID spécifié.
        """
        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Il n'existe pas de contrat avec cet ID")

        for key, value in data.items():
            setattr(contract, key, value)

        self.session.commit()

    @is_authenticated
    @is_admin
    @is_gestion
    def find_by_customer(self, customer_id):
        """
        Permet de retrouver les contrats affiliés à un client spécifique.

        Paramètres :
        ------------
        customer_id : int
            L'ID du client pour lequel retrouver les contrats.

        Retourne :
        ----------
        list[Contract] : La liste des contrats du client.
        """
        return self.session.query(Contract).filter_by(customer_id=customer_id).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def find_by_state(self, state):
        """
        Permet de lister les contrats en fonction de leur statut.

        Paramètres :
        ------------
        state : str
            Le statut des contrats à retrouver (par exemple, 'C' pour créé, 'S' pour signé).

        Retourne :
        ----------
        list[Contract] : La liste des contrats correspondant au statut donné.
        """
        return self.session.query(Contract).filter_by(state=state).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def state_signed(self):
        """
        Permet de lister tous les contrats qui sont signés.

        Retourne :
        ----------
        list[Contract] : La liste des contrats signés.
        """
        return self.session.query(Contract).filter_by(state="S").all()

    @is_authenticated
    @is_admin
    @is_gestion
    @is_commercial
    def find_by_paiement_state(self, paiement_state):
        """
        Permet de lister les contrats en fonction de leur état de paiement.

        Paramètres :
        ------------
        paiement_state : str
            L'état de paiement des contrats à retrouver ('P' pour soldé, 'N' pour non soldé).

        Retourne :
        ----------
        list[Contract] : La liste des contrats correspondant à l'état de paiement donné.
        """
        return self.session.query(Contract).filter_by(paiement_state=paiement_state).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def add_paiement(self, ref_contract, data) -> None:
        """
        Ajoute un nouveau paiement au contrat dans la base de données.

        Paramètres :
        ------------
        ref_contract : int
            La référence du contrat auquel ajouter le paiement.
        data : dict
            Les informations sur le paiement à ajouter.

        Exceptions :
        ------------
        ValueError :
            Levée si le montant du paiement dépasse le restant dû du contrat.
        IntegrityError :
            Levée si un problème d'intégrité des données survient lors de l'ajout du paiement.
        """
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
        Met à jour l'état du contrat en 'S' (Signé).

        Paramètres :
        ------------
        ref_contract : int
            ID du contrat à marquer comme signé.

        Exceptions :
        ------------
        ValueError :
            Levée si aucun contrat n'est trouvé avec la référence donnée.
        """
        try:
            contract = Contract.find_by_ref(self.session, ref_contract)
        except NoResultFound:
            raise ValueError(f"Aucun contrat trouvé avec la référence {ref_contract}")

        contract.state = 'S'
        self.session.add(contract)
        self.session.commit()
        DataView.display_data_update()
