from sqlalchemy import create_engine
from config import Base

engine = create_engine('sqlite:///:memory:')
Base.metadata.drop_all(engine)  # Supprimer toutes les tables
Base.metadata.create_all(engine)  # Recréer toutes les tables
