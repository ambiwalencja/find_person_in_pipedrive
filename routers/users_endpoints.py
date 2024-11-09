# endpoints for managing users: creating, displaying, deleting, login etc
from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
import os
from db.db_connect import get_db
from schemas.users_schemas import UserBase, UserDisplay, UserSignIn, UserAuth
from db_models.user import User
from auth.hashing import Hash
from auth.oauth2 import create_access_token, get_current_user
from auth import db_users as db_users_functions


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post('/create/{passphrase}', response_model=UserDisplay)
def create_user(request: UserBase, passphrase: str, db: Session = Depends(get_db)):
    # check passphrase
    if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect passphrase')
    # check if email ends with @futurecollars.com
    if not request.email.endswith('@futurecollars.com'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only Future Collars email addresses are allowed')
    # check if user already exists
    if db.query(User).filter(User.Username == request.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists')
    return db_users_functions.create_user(db, request)


@router.post('/login')
def login(request: UserSignIn, db: Session = Depends(get_db)):
    user = db_users_functions.get_user_by_username(db, request.username)
    if not Hash.verify(user.Password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.ID,
        'username': user.Email
    }

@router.post('/display')
def display_users(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    data = db.query(User.ID, User.Username, User.Email).all()
    response_data = []
    for row in data:
        response_data.append({
            'ID': row[0],
            'Username': row[1],
            'Email': row[2]
        })
    return response_data


@router.post('/delete')
def delete_users(term: str, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)): 
    if '@futurecollars.com' in term:
        user = db.query(User).filter(User.Email == term).first()
    else:
        user = db.query(User).filter(User.Username == term).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {term} does not exist')
    db.delete(user)
    db.commit()
    return True


@router.post('/reset')
def reset_password_for_user(request: UserSignIn, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    user = db.query(User).filter(User.Username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {request.username} does not exist')
    user.Password = Hash.bcrypt(request.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return True