from database import engine
from models.base import Base
from models.user import User
from models.customer import Customer
from models.contract import Contract
from models.event import Event

Base.metadata.create_all(bind=engine)
