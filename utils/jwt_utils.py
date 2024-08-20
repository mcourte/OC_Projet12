import jwt
import datetime

SECRET_KEY = 'openclassroom_projet12'
ALGORITHM = 'HS256'


def create_token(data):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Jeton valide pendant 1 heure
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        print("Le jeton a expiré.")
        return None
    except jwt.InvalidTokenError:
        print("Jeton invalide.")
        return None
