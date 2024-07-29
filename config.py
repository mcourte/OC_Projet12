import os
from sqlalchemy import create_engine

# Utiliser des variables d'environnement pour les informations sensibles
db_user = os.getenv('DB_USER', 'app_user')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'app_db')

# Créer l'engine SQLAlchemy
engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}')