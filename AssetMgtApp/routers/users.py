from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette import status
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="AssetMgtApp/templates")

router = APIRouter(
    prefix='/users',
    tags=['users']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    email: str = Field(min_length=3, max_length=20)
    firstname: str = Field(min_length=1, max_length=15)
    lastname: str = Field(min_length=3, max_length=15)
    userRole: str = Field(min_length=3,max_length=10)
    userStatus: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=5, max_length=30)
    confirmPassword: str = Field(min_length=5, max_length=30)

##this should be a shared function
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

@router.get("/user-page")
async def render_user_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
           return redirect_to_login()

        ## Get saved filtering values
        userRoleFilter =request.cookies.get('userRoleFilter')
        userStatusFilter =request.cookies.get('userStatusFilter')


        ##build dynamic query
        query = db.query(Users)

        if userRoleFilter is not None and userRoleFilter != "All":
            query = query.filter(Users.userRole == userRoleFilter)

        if userStatusFilter is not None and userStatusFilter != "All":
            query = query.filter(Users.userStatus == userStatusilter)

        userList = query.all()

        return templates.TemplateResponse("user.html", {"request": request, "users": userList, "currentUser": user})

    except:
        return redirect_to_login()

@router.get('/add-user-page')
async def render_user_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-user.html", {"request": request, "currentUser": user})

    except:
        return redirect_to_login()


@router.get("/edit-user-page/{user_id}")
async def render_edit_edit_page(request: Request, user_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None:
            raise HTTPException(status_code=404, detail='User not found.')

        return templates.TemplateResponse("edit-user.html", {"request": request, "user": user_model, "currentUser": user})

    except:
        return redirect_to_login()



@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashedPassword):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashedPassword = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()







