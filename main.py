from database import SessionLocal
from controllers import UserController


def main():
    session = SessionLocal()
    user_controller = UserController(session)


if __name__ == "__main__":
    main()
