from models.user import User


class UserController:
    def __init__(self, session):
        self.session = session

    def create_user(self, first_name, last_name, role, password):
        """Permet de créer un User dans la BD"""
        if role not in User.get_all_roles():
            raise ValueError(f"Rôle invalide, erreur: {role}")

        try:
            # Générer un username unique
            username = User.generate_unique_username(self.session, first_name, last_name)

            # Créer un nouvel utilisateur
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=role
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
