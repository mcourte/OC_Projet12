from models.entities import Event


class EventBase:
    def __init__(self, session):
        self.session = session

    def create_event(self, data):
        """Permet de créer un Evènement
        Informations à fournir : Titre, description, Location, Nombre de participants,
        Date de début, Date de fin, l'ID du contrat, l'ID du Client, et l'ID de l'utilisateur Support"""
        event = Event(
            title=data['title'],
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees', 0),
            report=data.get('report'),
            date_started=data['date_started'],
            date_ended=data['date_ended'],
            contract_id=data.get('contract_id'),
            customer_id=data.get('customer_id'),
            support_id=data.get('support_id')
        )
        self.session.add(event)
        self.session.commit()
        return event

    def get_event(self, event_id):
        """Permet de retrouver un évènement via son ID"""
        return self.session.query(Event).filter_by(event_id=event_id).first()

    def get_all_events(self):
        """Permet de lister la liste de tous les évènements"""
        return self.session.query(Event).all()

    def update_event(self, event_id, data):
        """Permet de mettre à jour un évènement"""
        event = self.session.query(Event).filter_by(event_id=event_id).first()
        if not event:
            raise ValueError("Event not found")

        for key, value in data.items():
            setattr(event, key, value)

        self.session.commit()
