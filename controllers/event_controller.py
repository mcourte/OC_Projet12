from models.event import Event


class EventController:
    def __init__(self, session):
        self.session = session

    def create_event(self, name, start_date, end_date, location, attendees, notes):
        """Permet de créer un Event dans la BD"""

        try:

            # Créer un nouveau client
            new_event = Event(
                name=name,
                start_date=start_date,
                end_date=end_date,
                location=location,
                attendees=attendees,
                notes=notes
            )

            # Ajouter le client à la session
            self.session.add(new_event)
            self.session.commit()

            print(f"Nouvel Evenement crée : {new_event.name} ")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la création de l'évènement : {e}")

    def edit_event(self, name, event_id, customer_id, ges_contact_id, sup_contact_id,
                   start_date, end_date, location, attendees, notes):
        """Permet de modifier un Evènement dans la BD"""
        event = self.session.query(Event).filter_by(event_id=event_id).first()

        if event is None:
            print(f"Aucun client trouvé avec l'ID {event_id}")
            return

        try:
            if name:
                event.name = name
            if start_date:
                event.start_date = start_date
            if end_date:
                event.end_date = end_date
            if location:
                event.location = location
            if attendees:
                event.attendees = attendees
            if notes:
                event.notes = notes

            # Ajouter les modifications à la session
            self.session.commit()
            print(f"Evènement avec l'ID {customer_id} mis à jour avec succès.")

        except Exception as e:
            # Autres exceptions possibles
            self.session.rollback()
            print(f"Erreur lors de la mise à jour de l'éèvement : {e}")

    def delete_event(self, event_id):
        """Permet de supprimer un évènement de la BD"""
        event = self.session.query(Event).filter_by(event_id=event_id).first()

        if event is None:
            print(f"Aucun évènement trouvé avec l'ID {event_id}")
            return

        try:
            self.session.delete(event)
            self.session.commit()
            print(f"Evènement avec l'ID {event_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression de l'évènement : {e}")

    def get_event(self):
        return self.session.query(Event).all()
