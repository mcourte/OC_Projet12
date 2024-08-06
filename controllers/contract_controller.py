from models.contract import Contract
from permissions import has_permission, Permission
from models.user import User
from generic_controllers import sort_items, get_readonly_items
from constantes import get_sortable_attributes


class ContractController:
    def __init__(self, session, user_id):
        self.session = session
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_contracts(self, sort_by: str, order: str = 'asc'):
        if not has_permission(self.user_role, Permission.SORT_CONTRACT):
            print("Permission refusée : Vous n'avez pas les droits pour trier les contrats.")
            return []
        sortable_attributes = get_sortable_attributes()
        return sort_items(self.session, Contract, sort_by, order, self.user_role, sortable_attributes)

    def get_all_contracts(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            print("Permission refusée : Vous n'avez pas les droits pour afficher les contrats.")
            return []
        return get_readonly_items(self.session, Contract)

    def create_contract(self, total_amount, remaining_amount, is_signed):
        """Permet de créer un Contract dans la BD"""
        if not has_permission(self.user_role, Permission.CREATE_CONTRACT):
            print("Permission refusée : Vous n'avez pas les droits pour créer ce contrat.")
            return

        try:
            # Créer un nouveau client
            new_contract = Contract(
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
            )

            # Ajouter le client à la session
            self.session.add(new_contract)
            self.session.commit()

            print(f"Nouveau Contrat crée : {new_contract.contract_id} ")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la création du Contrat : {e}")

    def edit_contract(self, contract_id, **kwargs):
        """Permet de modifier un Evènement dans la BD"""
        if not has_permission(self.user_role, Permission.EDIT_CONTRACT):
            print("Permission refusée : Vous n'avez pas les droits pour modifier ce contrat.")
            return

        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()
        if contract is None:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}")
            return

        try:

            # Ajouter les modifications à la session
            for key, value in kwargs.items():
                setattr(contract, key, value)
                self.session.commit()
                print(f"Contrat avec l'ID {contract_id} mis à jour avec succès.")
        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du contrat : {e}")

    def delete_contract(self, contract_id):
        """Permet de supprimer un contrat de la BD"""
        if not has_permission(self.user_role, Permission.DELETE_CONTRACT):
            print("Permission refusée : Vous n'avez pas les droits pour modifier ce contrat.")
            return

        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()

        if contract is None:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}")
            return

        try:
            self.session.delete(contract)
            self.session.commit()
            print(f"Contrat avec l'ID {contract_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression du contrat : {e}")

    def get_contract(self):
        return self.session.query(Contract).all()
