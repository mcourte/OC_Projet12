from models.entities import Event


class EventBase:
    def __init__(self, session):
        self.session = session

    def create_event(self, data):
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
        return self.session.query(Event).filter_by(event_id=event_id).first()

    def get_all_events(self):
        return self.session.query(Event).all()

    def update_event(self, event_id, data):
        event = self.session.query(Event).filter_by(event_id=event_id).first()
        if not event:
            raise ValueError("Event not found")

        for key, value in data.items():
            setattr(event, key, value)

        self.session.commit()

    def delete_event(self, event_id):
        event = self.get_event(event_id)
        if not event:
            raise ValueError("Event not found")

        self.session.delete(event)
        self.session.commit()
