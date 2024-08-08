from models.contract import Contract
from models.user import User
from controllers.generic_controllers import get_readonly_items
from constantes import get_sortable_attributes
from permissions import Permission, has_permission


class ContractController:
    def __init__(self, session=None, user_id=None):
        self.session = session
        self.user_id = user_id
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_contracts(self, attribute):
        if not has_permission(self.user_role, Permission.SORT_CONTRACT):
            raise PermissionError("Vous n'avez pas la permission de trier la liste des User.")

        sortable_attributes = get_sortable_attributes().get(User, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users

    def get_all_contracts(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            raise PermissionError("Vous n'avez pas la permission pour afficher les contracts.")
        return get_readonly_items(self.session, Contract)

    def create_contract(self, total_amount, remaining_amount, is_signed,
                        com_contact_id=None, ges_contact_id=None, customer_id=None):
        """Permet de créer un Contract dans la BD"""
        if total_amount is None:
            raise ValueError("Le montant total ne peut pas être nul.")
        if remaining_amount is None:
            raise ValueError("Le montant restant ne peut pas être nul.")
        if is_signed is None:
            raise ValueError("Le statut de signature ne peut être nul.")

        if not has_permission(self.user_role, Permission.CREATE_CONTRACT):
            raise PermissionError("Vous n'avez pas la permission de créer un Contract.")

        print("Validation passed for creating contract")

        self._create_contract_in_db(total_amount, remaining_amount, is_signed,
                                    com_contact_id, ges_contact_id, customer_id)

    def _create_contract_in_db(self, total_amount, remaining_amount, is_signed,
                               com_contact_id=None, ges_contact_id=None, customer_id=None):
        """Méthode privée pour créer le contrat dans la base de données"""
        if not has_permission(self.user_role, Permission.CREATE_CONTRACT):
            raise PermissionError("Vous n'avez pas la permission de créer un Contract.")
        try:
            new_contract = Contract(
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
                com_contact_id=com_contact_id,
                ges_contact_id=ges_contact_id,
                customer_id=customer_id
            )
            self.session.add(new_contract)
            self.session.commit()
            print(f"Nouveau Contrat créé : {new_contract.contract_id}")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création du Contrat : {e}")

    def edit_contract(self, contract_id, **kwargs):
        """Permet de modifier un Evènement dans la BD"""
        if not has_permission(self.user_role, Permission.EDIT_CONTRACT):
            raise PermissionError("Vous n'avez pas la permission de modifier un Contrat.")

        contract_to_edit = self.session.query(Contract).filter_by(contract_id=contract_id).first()
        if contract_to_edit is None:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}")
            return
        try:
            # Ajouter les modifications à la session
            for key, value in kwargs.items():
                setattr(contract_to_edit, key, value)
                self.session.commit()
                print(f"Contrat avec l'ID {contract_id} mis à jour avec succès.")
        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du contrat : {e}")

    def delete_contract(self, contract_id):
        """Permet de supprimer un contrat de la BD"""
        if not has_permission(self.user_role, Permission.DELETE_CONTRACT):
            raise PermissionError("Vous n'avez pas la permission de supprimer un User.")

        contract_to_delete = self.session.query(Contract).filter_by(contract_id=contract_id).first()

        if contract_to_delete is None:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}")
            return

        try:
            self.session.delete(contract_to_delete)
            self.session.commit()
            print(f"Contrat avec l'ID {contract_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression du contrat : {e}")

    def get_contract(self):
        return self.session.query(Contract).all()
