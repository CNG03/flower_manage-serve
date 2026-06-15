from database.db import SessionLocal
from models.user import User

from auth.auth import hash_password


def create_default_users():

    db = SessionLocal()

    try:

        # kiểm tra root tồn tại chưa
        root = db.query(User).filter(
            User.username == "root"
        ).first()


        if not root:

            root_user = User(
                username="root",
                password=hash_password("@root123#"),
                role="root"
            )

            db.add(root_user)

            print("Created root account")


        # kiểm tra user tồn tại chưa
        normal = db.query(User).filter(
            User.username == "user"
        ).first()


        if not normal:

            normal_user = User(
                username="user",
                password=hash_password("hoilacha123"),
                role="user"
            )

            db.add(normal_user)

            print("Created user account")


        db.commit()


    except Exception as e:

        db.rollback()
        print("ERROR:", e)


    finally:
        db.close()



if __name__ == "__main__":
    create_default_users()