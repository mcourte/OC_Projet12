# setup_db.py
from sqlalchemy import create_engine
from config import Base

# Création de l'engin SQLite pour les tests
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)  # Crée toutes les tables définies dans Base
