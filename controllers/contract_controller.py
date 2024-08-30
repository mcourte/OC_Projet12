# Import généraux
import os
import sys
from decimal import Decimal

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Import des Views
from views.data_view import DataView
from views.console_view import console
# Import des Modèles
from models.entities import Contract, Paiement
# Import des Controllers
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
        Crée un nouveau contrat avec les informations fournies.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        data : dict
            Un dictionnaire contenant les informations du contrat à créer,
            telles que 'description', 'total_amount', 'remaining_amount',
            'state', 'customer_id', 'paiement_state' et 'commercial_id'.

        Retourne :
        ----------
        Contract
            Le contrat nouvellement créé.
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
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
    def update_contract(contract_id, data, session):
        """
        Met à jour un contrat existant avec les nouvelles valeurs fournies.

        Paramètres :
        ------------
        contract_id : int
            L'ID du contrat à mettre à jour.
        data : dict
            Un dictionnaire contenant les nouvelles valeurs pour les attributs du contrat.

        Exceptions :
        ------------
        ValueError
            Levée si aucun contrat n'est trouvé avec l'ID spécifié.
        """
        contract = session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Il n'existe pas de contrat avec cet ID")
        for key, value in data.items():
            setattr(contract, key, value)

        session.commit()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def add_paiement(self, session, contract_id, data) -> None:
        """
        Ajoute un nouveau paiement à un contrat dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        contract_id : int
            L'ID du contrat auquel ajouter le paiement.
        data : dict
            Un dictionnaire contenant les informations du paiement, y compris 'paiement_id' et 'amount'.

        Exceptions :
        ------------
        ValueError
            Levée si le paiement existe déjà pour le contrat ou si le montant du paiement dépasse le montant restant dû.
        """
        try:
            amount = Decimal(data['amount'])
            paiement_id = data['paiement_id']

            # Vérifier si le paiement existe déjà pour le contrat donné
            existing_paiement = session.query(Paiement).filter_by(paiement_id=paiement_id, contract_id=contract_id).first()
            if existing_paiement:
                raise ValueError(f"Un paiement avec la référence {paiement_id} existe déjà pour le contrat ID={contract_id}.")

            # Récupérer le contrat associé
            contract = session.query(Contract).filter_by(contract_id=contract_id).first()
            if not contract:
                raise ValueError("Contrat introuvable")

            # Vérifier si le montant du paiement dépasse le restant dû
            if contract.remaining_amount is not None and amount > contract.remaining_amount:
                text = "Le montant du paiement dépasse le restant dû du contrat."
                console.print(text, style="bold red")
                raise ValueError

            # Créer le paiement
            paiement = Paiement(
                paiement_id=paiement_id,
                amount=amount,
                contract_id=contract_id
            )
            session.add(paiement)

            # Mettre à jour le montant restant dû du contrat
            if contract.remaining_amount is not None:
                contract.remaining_amount -= float(amount)
                if contract.remaining_amount < 0:
                    contract.remaining_amount = 0

            # Mettre à jour l'état du paiement du contrat
            if contract.remaining_amount == 0:
                contract.paiement_state = 'P'  # Soldé
            else:
                contract.paiement_state = 'N'  # Non Soldé

            # Ajouter la mise à jour du contrat à la session
            session.add(contract)

            session.commit()
            text = f"Paiement enregistré avec succès : {paiement.paiement_id}"
            console.print(text, style="bold green")
            text = f"Contrat mis à jour: ID={contract.contract_id}, Montant restant={contract.remaining_amount}"
            console.print(text, style="cyan")
            return paiement

        except Exception as e:
            session.rollback()
            text = f"Erreur lors de l'enregistrement du paiement : {e}"
            raise

    @staticmethod
    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def signed(session, contract_id):
        """
        Met à jour l'état d'un contrat pour le marquer comme signé.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        contract_id : int
            L'ID du contrat à mettre à jour.

        Exceptions :
        ------------
        ValueError
            Levée si aucun contrat n'est trouvé avec l'ID spécifié.
        """
        contract = session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError(f"Aucun contrat trouvé avec l'ID {contract_id}")
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
        Met à jour le commercial attribué à un contrat.

        Paramètres :
        ------------
        cls : type
            La classe ContractBase.
        current_user : EpicUser
            L'utilisateur actuel effectuant la mise à jour.
        session : Session
            La session SQLAlchemy utilisée pour effectuer les opérations de base de données.
        contract_id : int
            L'ID du contrat à mettre à jour.
        gestion_id : int
            L'ID du nouveau commercial à attribuer au contrat.

        Exceptions :
        ------------
        ValueError
            Levée si aucun contrat n'est trouvé avec l'ID spécifié.
        """
        contract = session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Aucun contrat trouvé avec l'ID spécifié.")

        # Mise à jour du commercial
        contract.gestion_id = gestion_id
        session.commit()
        text = f"Gestionnaire ID {gestion_id} attribué au contrat ID {contract_id}."
        console.print(text, style="cyan")
