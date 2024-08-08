from models.customer import Customer
from generic_controllers import get_readonly_items
from permissions import Permission, has_permission, Role
from models.user import User
from constantes import get_sortable_attributes


class CustomerController:
    def __init__(self, session, user_id):
        self.session = session
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_customers(self, attribute):
        if not has_permission(self.user_role, Permission.SORT_CUSTOMER):
            raise PermissionError("Vous n'avez pas les droits pour trier les utilisateurs.")

        sortable_attributes = get_sortable_attributes().get(Customer, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users

    def get_all_customers(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            print("Permission refusée : Vous n'avez pas les droits pour afficher les clients.")
            return []
        return get_readonly_items(self.session, Customer)

    def create_customer(self, first_name, last_name, phone, email, company_name):
        """Permet de créer un Event dans la BD"""
        if not first_name or not last_name or not phone or not email or not company_name:
            raise ValueError("Tous les champs doivent être remplis.")

        if not has_permission(self.user_role, Permission.CREATE_CUSTOMER):
            raise PermissionError("Vous n'avez pas la permission de créer un Client.")

        print(f"Validation passed for creating Customer: {first_name} from {company_name}")
        self._create_customer_in_db(self, first_name, last_name, phone, email, company_name)

    def _create_customer_in_db(self, first_name, last_name, phone, email, company_name):
        """Méthode privée pour créer l'évènement dans la base de données"""
        try:
            new_customer = Customer(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                company_name=company_name
            )
            self.session.add(new_customer)
            self.session.commit()
            print(f"Nouveau Client crée : {new_customer.name}")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création du client : {e}")

    def edit_customer(self, customer_id, **kwargs):
        if not has_permission(self.user_role, Permission.EDIT_CUSTOMER):
            print("Permission refusée : Vous n'avez pas les droits pour modifier ce client.")
            return

        event = self.session.query(Customer).filter_by(customer_id=customer_id).first()
        if event is None:
            print(f"Aucun évènement trouvé avec l'ID {customer_id}")
            return

        try:
            for key, value in kwargs.items():
                if self.user_role == Role.SUP and key == 'assignee_id':
                    print("Permission refusée : Vous ne pouvez pas modifier l'attribution.")
                    continue
                setattr(event, key, value)
            self.session.commit()
            print(f"Client avec l'ID {customer_id} mis à jour avec succès.")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du client : {e}")

    def delete_customer(self, customer_id):
        """Permet de supprimer un client de la BD"""
        if not has_permission(self.user_role, Permission.DELETE_CUSTOMER):
            print("Permission refusée : Vous n'avez pas les droits pour supprimer ce client.")
            return

        customer_to_delete = self.session.query(User).filter_by(customer_id=customer_id).first()

        try:
            self.session.delete(customer_to_delete)
            self.session.commit()
            print(f"Client avec l'ID {customer_id} supprimé avec succès.")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression de l'évènement : {e}")

    def get_customer(self):
        return self.session.query(Customer).all()
