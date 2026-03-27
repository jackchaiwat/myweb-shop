from sqlalchemy.orm import Session
from models.user import User
from auth.jwt_handler import hash_password

def get_user_by_username(db: Session, username: str):

    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username, email, password):
    
    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
