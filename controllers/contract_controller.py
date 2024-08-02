from models.contract import Contract


class ContractController:
    def __init__(self, session):
        self.session = session

    def create_contract(self, total_amount, remaining_amount, is_signed, contract_id):
        """Permet de créer un Contract dans la BD"""

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

    def edit_contract(self, contract_id, total_amount, remaining_amount, is_signed,
                      com_contact_id, ges_contact_id, customer_id):
        """Permet de modifier un Evènement dans la BD"""
        contract = self.session.query(Contract).filter_by(contract_id=contract_id).first()

        if contract is None:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}")
            return

        try:

            # Ajouter les modifications à la session
            self.session.commit()
            print(f"Contrat avec l'ID {contract_id} mis à jour avec succès.")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du contrat : {e}")

    def delete_contract(self, contract_id):
        """Permet de supprimer un contrat de la BD"""
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
