from models.customer import Customer


class CustomerController:
    def __init__(self, session):
        self.session = session

    def create_customer(self, first_name, last_name, phone, email, company_name):
        """Permet de créer un Customer dans la BD"""

        try:

            # Créer un nouveau client
            new_customer = Customer(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                company_name=company_name
            )

            # Ajouter le client à la session
            self.session.add(new_customer)
            self.session.commit()

            print(f"Nouveau client créé : {new_customer.first_name}, {new_customer.last_name}")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la création du client : {e}")

    def edit_customer(self, customer_id, first_name=None, last_name=None, phone=None, email=None, company_name=None):
        """Permet de modifier un utilisateur dans la BD"""
        customer = self.session.query(Customer).filter_by(customer_id=customer_id).first()

        if customer is None:
            print(f"Aucun client trouvé avec l'ID {customer_id}")
            return

        try:
            if first_name:
                customer.first_name = first_name
            if last_name:
                customer.last_name = last_name
            if phone:
                customer.phone = phone
            if email:
                customer.email = email
            if company_name:
                customer.company_name = company_name

            # Ajouter les modifications à la session
            self.session.commit()
            print(f"Client avec l'ID {customer_id} mis à jour avec succès.")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du client : {e}")

    def delete_customer(self, customer_id):
        """Permet de supprimer un client de la BD"""
        customer = self.session.query(Customer).filter_by(customer_id=customer_id).first()

        if customer is None:
            print(f"Aucun client trouvé avec l'ID {customer_id}")
            return

        try:
            self.session.delete(customer)
            self.session.commit()
            print(f"Client avec l'ID {customer_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression du client : {e}")

    def get_customer(self):
        return self.session.query(Customer).all()
