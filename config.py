from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys
from sqlalchemy.orm import declarative_base


# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = os.getenv('PYTHONPATH')
if project_root:
    sys.path.append(project_root)
else:
    print("PYTHONPATH n'est pas défini dans .env")

# Configurations de la base de données
db_user = os.getenv('DB_USER', 'app_user')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'app_db')

DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}'

SECRET_KEY = os.getenv('SECRET_KEY')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
