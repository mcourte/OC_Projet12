from models.user import User, Role
from .generic_controllers import get_readonly_items
from constantes import get_sortable_attributes


class UserController:
    def __init__(self, session=None, user_id=None):
        self.session = session
        self.user_id = user_id
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def get_users(self):
        return self.session.query(User).all()

    def get_all_users(self):
        if self.user_role not in [Role.GES, Role.ADM, Role.COM, Role.SUP]:
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

        if role not in Role:
            raise ValueError(f"Rôle invalide: {role}")

        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de créer un User.")

        # Si toutes les conditions sont remplies, vous pouvez procéder à la création
        print(f"Validation passed for creating user: {first_name} {last_name}, Role: {role}")

        # Ici, vous pouvez appeler une méthode ou un service pour procéder à la création effective
        self._create_user_in_db(first_name, last_name, role, password)

    def _create_user_in_db(self, first_name, last_name, role, password):
        """Méthode privée pour créer l'utilisateur dans la base de données"""
        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de créer un User.")
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
        if self.user_role not in [Role.GES, Role.ADM]:
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
        if self.user_role not in [Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de supprimer un User.")

        user_to_delete = self.session.query(User).filter_by(user_id=user_id).first()

        if user_to_delete:
            self.session.delete(user_to_delete)

            # Valider la suppression dans la base de données
            self.session.commit()
        else:
            raise ValueError("User not found")

    def sort_users(self, attribute):
        if self.user_role not in [Role.GES, Role.ADM]:
            raise PermissionError("Vous n'avez pas la permission de trier la liste des User.")

        sortable_attributes = get_sortable_attributes().get(User, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users
