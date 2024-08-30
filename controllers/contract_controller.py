import os
import sys
from decimal import Decimal

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
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
    def update_contract(contract_id, data, session):
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
        print(f"data du controller: {data}")
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
        Ajoute un nouveau paiement au contrat dans la base de données.
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

            # Log de la valeur du montant restant avant mise à jour
            print(f"Montant restant avant mise à jour : {contract.remaining_amount}")

            # Vérifier si le montant du paiement dépasse le restant dû
            if contract.remaining_amount is not None and amount > contract.remaining_amount:
                raise ValueError("Le montant du paiement dépasse le restant dû du contrat.")

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

                # Log de la valeur du montant restant après mise à jour
                print(f"Montant restant après mise à jour : {contract.remaining_amount}")

            # Mettre à jour l'état du paiement du contrat
            if contract.remaining_amount == 0:
                contract.paiement_state = 'P'  # Soldé
            else:
                contract.paiement_state = 'N'  # Non Soldé

            # Ajouter la mise à jour du contrat à la session
            session.add(contract)

            session.commit()
            print(f"Paiement enregistré avec succès : {paiement.paiement_id}")
            print(f"Contrat mis à jour: ID={contract.contract_id}, Remaining Amount={contract.remaining_amount}")
            return paiement

        except Exception as e:
            session.rollback()
            print(f"Erreur lors de l'enregistrement du paiement : {e}")
            raise

    @staticmethod
    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def signed(session, contract_id):
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
