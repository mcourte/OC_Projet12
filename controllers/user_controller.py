from models.user import User, Role
from permissions import has_permission, Permission
from .generic_controllers import sort_items, get_readonly_items
from constantes import get_sortable_attributes


class UserController:
    def __init__(self, session, user_id):
        self.session = session
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_users(self, sort_by: str, order: str = 'asc'):
        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas les droits trier les utilisateurs.")
        sortable_attributes = get_sortable_attributes()
        return sort_items(self.session, User, sort_by, order, self.user_role, sortable_attributes)

    def get_all_users(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            print("Permission refusée : Vous n'avez pas les droits pour afficher les utilisateurs.")
            return []
        return get_readonly_items(self.session, User)

    def create_user(self, first_name, last_name, role, password):
        """Permet de créer un User dans la BD"""
        if isinstance(role, str):
            try:
                role = Role(role)
            except ValueError:
                raise ValueError(f"Rôle invalide, erreur: {role}")

        if role not in Role:
            raise ValueError(f"Rôle invalide, erreur: {role}")

        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas les droits pour créer un utilisateur.")

        try:
            username = User.generate_unique_username(self.session, first_name, last_name)
            email = User.generate_unique_email(self.session, username)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=role,
                password="",  # The password will be hashed later
                email=email
            )
            new_user.set_password(password)
            self.session.add(new_user)
            self.session.commit()

            print(f"Nouvel utilisateur créé : {new_user.username}, {new_user.role}")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création de l'utilisateur : {e}")

    def edit_user(self, user_id, first_name=None, last_name=None, role=None, password=None):
        """Permet de modifier un utilisateur dans la BD"""
        if not has_permission(self.user_role, Permission.EDIT_USER):
            print("Permission refusée : Vous n'avez pas les droits pour modifier cet utilisateur.")
            return
        user = self.session.query(User).filter_by(user_id=user_id).first()

        if user is None:
            print(f"Aucun utilisateur trouvé avec l'ID {user_id}")
            return

        if role and role not in Role._value2member_map_:
            raise ValueError(f"Rôle invalide, erreur: {role}")

        try:
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if role:
                user.role = Role(role)
            if password:
                user.set_password(password)

            self.session.commit()
            print(f"Utilisateur avec l'ID {user_id} mis à jour avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la mise à jour de l'utilisateur : {e}")

    def delete_user(self, user_id):
        """Permet de supprimer un utilisateur de la BD"""
        if not has_permission(self.user_role, Permission.DELETE_USER):
            print("Permission refusée : Vous n'avez pas les droits pour supprimer un utilisateur.")
            return
        user = self.session.query(User).filter_by(user_id=user_id).first()

        if user is None:
            print(f"Aucun utilisateur trouvé avec l'ID {user_id}")
            return

        try:
            self.session.delete(user)
            self.session.commit()
            print(f"Utilisateur avec l'ID {user_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression de l'utilisateur : {e}")

    def get_users(self):
        return self.session.query(User).all()
