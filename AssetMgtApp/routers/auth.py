from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    initials: str
    name: str
    userRole: str
    userStatus: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="AssetMgtApp/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

### Endpoints ###

def authenticate_user(username: str, password: str, db) -> Optional[Users]:
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashedPassword):
        return None
    return user

#def oldauthenticate_user(username: str, password: str, db):
#    user = db.query(Users).filter(Users.username == username).first()
#    if not user:
#        return False
#    if not bcrypt_context.verify(password, user.hashedPassword):
#        return False
#
#    return user

def create_access_token(username: str, userId: int, userRole: str, expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': userId,
        'userRole': userRole,
        'exp': (datetime.now(timezone.utc) + expires_delta).timestamp()
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



#def oldcreate_access_token(username: str, userId: int, userRole: str, expires_delta: timedelta):
#    encode = {'sub': username, 'id': userId, 'userRole': userRole}
#    expires = datetime.now(timezone.utc) + expires_delta
#    encode.update({'exp': expires})
#    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        userId: int = payload.get('id')
        userRole: str = payload.get('userRole')
        if username is None or userId is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='#1 Could not validate user.')
        return {'username': username, 'id': userId, 'userRole': userRole}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='#2 Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    try:
        create_user_model = Users(
            username=create_user_request.username,
            initials=create_user_request.initials,
            name=create_user_request.name,
            userRole=create_user_request.userRole,
            userStatus=create_user_request.userStatus,
            hashedPassword=bcrypt_context.hash(create_user_request.password),
            createdBy="KEL",
            updatedBy="KEL"
        )

        db.add(create_user_model)
        db.commit()
        return {"message": "User created successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="initials or username already exists")

@router.get("/list", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Users).all()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):


    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.userRole, timedelta(hours=8))

    return {'access_token': token, 'token_type': 'bearer'}







