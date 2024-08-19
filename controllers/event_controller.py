from models.entities import Event
from controllers.decorator import is_authenticated, is_admin, is_commercial, is_gestion


class EventBase:
    def __init__(self, session):
        self.session = session

    @is_authenticated
    @is_admin
    @is_commercial
    def create_event(self, data):
        """Permet de créer un Evènement"""
        # Use .get() to handle missing keys
        event = Event(
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees', 0),  # Default to 0 if not provided
            date_started=data.get('date_started'),
            date_ended=data.get('date_ended'),
            contract_id=data.get('contract_id'),
            customer_id=data.get('customer_id'),
            support_id=data.get('support_id')
        )
        self.session.add(event)
        self.session.commit()
        return event

    @is_authenticated
    @is_admin
    @is_commercial
    def get_event(self, event_id):
        """Permet de retrouver un évènement via son ID"""
        return self.session.query(Event).filter_by(event_id=event_id).first()

    @is_authenticated
    def get_all_events(self):
        """Permet de lister tous les évènements"""
        return self.session.query(Event).all()

    @is_authenticated
    @is_admin
    @is_commercial
    @is_gestion
    def update_event(self, event_id, data):
        """Permet de mettre à jour un évènement"""
        event = self.session.query(Event).filter_by(event_id=event_id).first()
        if not event:
            raise ValueError("Événement non trouvé.")

        for key, value in data.items():
            setattr(event, key, value)

        self.session.commit()
