from models.contract import Contract
from models.user import User, Role
from controllers.generic_controllers import get_readonly_items
from constantes import get_sortable_attributes


class ContractController:
    def __init__(self, session=None, user_id=None):
        self.session = session
        self.user_id = user_id
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_contracts(self, attribute):
        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de trier la liste des User.")

        sortable_attributes = get_sortable_attributes().get(User, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users

    def get_all_contracts(self):
        if self.user_role not in [Role.GES, Role.ADM, Role.COM, Role.SUP]:
            raise PermissionError("Vous n'avez pas la permission pour afficher les contracts.")
        return get_readonly_items(self.session, Contract)

    def create_contract(self, total_amount, remaining_amount, is_signed):
        """Permet de créer un Contract dans la BD"""
        # Vérification des champs requis
        if not total_amount:
            raise ValueError("Le prénom ne peut pas être nul.")

        if not remaining_amount:
            raise ValueError("Le nom ne peut pas être nul.")

        if not is_signed:
            raise ValueError("Le statut de signature ne peut être vide.")

        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de créer un Contract.")

        # Si toutes les conditions sont remplies, vous pouvez procéder à la création
        print("Validation passed for creating contract")

        # Ici, vous pouvez appeler une méthode ou un service pour procéder à la création effective
        self._create_event_in_db(total_amount, remaining_amount, is_signed)

    def _create_event_in_db(self, total_amount, remaining_amount, is_signed):
        """Méthode privée pour créer l'utilisateur dans la base de données"""
        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de créer un User.")
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
        if self.user_role not in [Role.GES, Role.ADM, Role.COM]:
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
        if self.user_role not in [Role.ADM]:
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
