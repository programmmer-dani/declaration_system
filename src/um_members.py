from auth import hash_password, verify_password
from database import init_db


def main():
    init_db()

if __name__ == "__main__":
    main()