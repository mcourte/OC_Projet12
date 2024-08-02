from models.user import User, Role


class UserController:
    def __init__(self, session):
        self.session = session

    def create_user(self, first_name, last_name, role, password):
        """Permet de créer un User dans la BD"""
        if role not in Role._value2member_map_:
            raise ValueError(f"Rôle invalide, erreur: {role}")

        try:
            # Générer un username unique
            username = User.generate_unique_username(self.session, first_name, last_name)
            email = User.generate_unique_email(self.session, username)  # Génération de l'email

            # Convertir le rôle en Enum
            role_enum = Role(role)

            # Créer un nouvel utilisateur
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=role_enum,
                password="",  # Le mot de passe sera haché plus tard
                email=email
            )
            # Hacher le mot de passe et l'ajouter à l'utilisateur
            new_user.set_password(password)

            # Ajouter l'utilisateur à la session
            self.session.add(new_user)
            self.session.commit()

            print(f"Nouvel utilisateur créé : {new_user.username}, {new_user.role}")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la création de l'utilisateur : {e}")

    def edit_user(self, user_id, first_name=None, last_name=None, role=None, password=None):
        """Permet de modifier un utilisateur dans la BD"""
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
                # Convertir le rôle en Enum
                user.role = Role(role)
            if password:
                # Hacher le mot de passe et l'ajouter à l'utilisateur
                user.set_password(password)

            # Ajouter les modifications à la session
            self.session.commit()
            print(f"Utilisateur avec l'ID {user_id} mis à jour avec succès.")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour de l'utilisateur : {e}")

    def delete_user(self, user_id):
        """Permet de supprimer un utilisateur de la BD"""
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
