from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.orm import declarative_base

PYTHONPATH = '/home/magali/OpenClassrooms/Formation/Projet_12-V1:/home/magali/OpenClassrooms/Formation/Projet_12-V1/env/lib/python3.12/site-packages'

load_dotenv('.cli_env')

# Configurations de la base de données
db_user = os.getenv('DB_USER', 'app_user')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'app_db')

DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}'

SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
TOKEN_DELTA = os.getenv('TOKEN_DELTA', '3600')
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
