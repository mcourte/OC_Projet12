from models.user import User
from .generic_controllers import get_readonly_items
from constantes import get_sortable_attributes
from permissions import Permission, has_permission, Role


class UserController:
    def __init__(self, session, user_id):
        self.session = session
        self.user_id = user_id
        self.user_role = self._get_user_role(user_id)

    def get_users(self):
        return self.session.query(User).all()

    def get_all_users(self):
        if not has_permission(self.user_role, Permission.SORT_USER):
            raise PermissionError("Vous n'avez pas la permission de voir la liste des Users.")
        return get_readonly_items(self.session, User)

    def create_user(self, first_name, last_name, role, password):
        """Vérifie les conditions avant de créer un utilisateur dans la BD"""

        # Vérification des champs requis
        if not first_name:
            raise ValueError("Le prénom ne peut pas être nul.")
        if not last_name:
            raise ValueError("Le nom ne peut pas être nul.")
        if not role:
            raise ValueError("Le rôle ne peut pas être nul.")
        if not password:
            raise ValueError("Le mot de passe ne peut pas être nul.")

        # Assurez-vous que role est une instance de Role
        if isinstance(role, str):
            role = Role(role)  # Convertir à partir de string si nécessaire
        if not isinstance(role, Role):
            raise ValueError("Role should be an instance of Role Enum")

        # Vérifiez les permissions avant de créer un utilisateur
        if not has_permission(self.user_role, Permission.CREATE_USER):
            raise PermissionError("Vous n'avez pas la permission de créer un User.")

        # Si toutes les conditions sont remplies, vous pouvez procéder à la création
        print(f"Validation passed for creating user: {first_name} {last_name}, Role: {role}")

        # Ici, vous pouvez appeler une méthode ou un service pour procéder à la création effective
        self._create_user_in_db(first_name, last_name, role, password)

    def _create_user_in_db(self, first_name, last_name, role, password):
        """Méthode privée pour créer l'utilisateur dans la base de données"""
        try:
            username = User.generate_unique_username(self.session, first_name, last_name)
            email = User.generate_unique_email(self.session, username)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=role,
                password="",  # Le mot de passe sera hachée après
                email=email
            )
            new_user.set_password(password)
            self.session.add(new_user)
            self.session.commit()

            print(f"User created: {new_user.username}, {new_user.role}")

        except Exception as e:
            self.session.rollback()
            print(f"Error creating user: {e}")

    def edit_user(self, user_id, new_first_name, new_last_name, new_role):
        """Permet de modifier un utilisateur dans la BD"""
        print(f"Editing user with role: {self.user_role}, Required permission: {Permission.EDIT_USER}")
        if not has_permission(self.user_role, Permission.EDIT_USER):
            raise PermissionError("Vous n'avez pas la permission de modifier un User.")

        user_to_edit = self.session.query(User).filter_by(user_id=user_id).first()

        if user_to_edit:
            user_to_edit.first_name = new_first_name
            user_to_edit.last_name = new_last_name
            user_to_edit.role = new_role

            # Valider les changements dans la base de données
            self.session.commit()
        else:
            raise ValueError("User not found")

    def delete_user(self, user_id):
        """Permet de supprimer un utilisateur de la BD"""
        print(f"Deleting user with role: {self.user_role}, Required permission: {Permission.DELETE_USER}")
        if not has_permission(self.user_role, Permission.DELETE_USER):
            raise PermissionError("Vous n'avez pas la permission de supprimer un User.")

        user_to_delete = self.session.query(User).filter_by(user_id=user_id).first()

        if user_to_delete:
            self.session.delete(user_to_delete)

            # Valider la suppression dans la base de données
            self.session.commit()
        else:
            raise ValueError("User not found")

    def sort_users(self, attribute):
        print(f"Sorting users with role: {self.user_role}, Required permission: {Permission.SORT_USER}")
        if not has_permission(self.user_role, Permission.SORT_USER):
            raise PermissionError("Vous n'avez pas la permission de trier la liste des User.")

        sortable_attributes = get_sortable_attributes().get(User, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users

    def _get_user_role(self, user_id):
        # Fetch the user and ensure the role is a Role enum
        role = self.session.query(User).get(user_id).role
        return Role(role)
