# functions for managing users that need connection to database
from fastapi import HTTPException, status
from db_models.user import User
from schemas.users_schemas import UserBase
from sqlalchemy.orm.session import Session
from auth.hashing import Hash

def create_user(db: Session, request: UserBase):
    new_user = User(
        Username = request.username,
        Email = request.email,
        Password = Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with username {username} not found')
    return user