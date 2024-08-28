import os
import sys
from decimal import Decimal
from sqlalchemy.orm.exc import NoResultFound

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from views.data_view import DataView
from models.entities import Contract, Paiement
from controllers.decorator import is_authenticated, requires_roles, sentry_activate


class ContractBase:
    """
    Classe de base pour la gestion des contrats, permettant de créer, récupérer,
    mettre à jour et gérer les paiements associés à un contrat.
    """

    def __init__(self, session, current_user):
        """
        Initialise la classe ContractBase avec une session SQLAlchemy.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        current_user : EpicUser
            L'utilisateur actuellement connecté.
        """
        self.session = session
        self.current_user = current_user

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def create_contract(session, data):
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
        # Créez l'instance du contrat
        contract = Contract(
            description=data['description'],
            total_amount=data['total_amount'],
            remaining_amount=data.get('remaining_amount'),
            state=data.get('state', 'C'),
            customer_id=data['customer_id'],
            paiement_state=data.get('paiement_state', 'N'),
            commercial_id=data.get('commercial_id')
        )

        # Utilisation de self.session pour ajouter et valider
        session.add(contract)
        session.commit()
        return contract

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
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

    @sentry_activate
    @is_authenticated
    def get_all_contracts(self):
        """
        Permet de retourner la liste de tous les contrats.

        Retourne :
        ----------
        list[Contract] : La liste de tous les contrats.
        """
        return self.session.query(Contract).all()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
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

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
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

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
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

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def state_signed(self):
        """
        Permet de lister tous les contrats qui sont signés.

        Retourne :
        ----------
        list[Contract] : La liste des contrats signés.
        """
        return self.session.query(Contract).filter_by(state="S").all()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
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

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def add_paiement(self, session, contract_id, data) -> None:
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

        try:
            amount = Decimal(data['amount'])
            paiement = Paiement(
                paiement_id=data['paiement_id'],
                amount=amount,
                contract_id=contract_id
            )
            session.add(paiement)
            session.commit()
            print(f"Paiement enregistré avec succès : {paiement.paiement_id}")
            return paiement
        except Exception as e:
            session.rollback()
            print(f"Erreur lors de l'enregistrement du paiement : {e}")
            raise

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def signed(self, session, contract_id) -> None:
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
            contract = session.query(Contract).filter_by(contract_id=contract_id[0]).all()
            print(contract)
        except NoResultFound:
            raise ValueError(f"Aucun contrat trouvé avec la référence {contract_id}")

        contract.state = 'S'
        session.add(contract)
        session.commit()
        DataView.display_data_update()

    @classmethod
    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_gestion_contract(cls, current_user, session, contract_id, gestion_id):
        """
        Met à jour le commercial attribué à un client.

        Paramètres :
        ------------
        current_user : EpicUser
            L'utilisateur actuel effectuant la mise à jour.
        session : SQLAlchemy Session
            La session utilisée pour effectuer les opérations de base de données.
        customer_id : int
            L'ID du client à mettre à jour.
        commercial_id : int
            L'ID du nouveau commercial à attribuer au client.

        Exceptions :
        ------------
        ValueError :
            Levée si aucun client n'est trouvé avec l'ID spécifié.
        """
        contract = session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Aucun contrat trouvé avec l'ID spécifié.")

        # Mise à jour du commercial
        contract.gestion_id = gestion_id
        session.commit()
        print(f"Gestionnaire ID {gestion_id} attribué au contrat ID {contract_id}.")
