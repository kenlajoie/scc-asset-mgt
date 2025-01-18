from _pyrepl import console
from typing import Annotated
from click import confirm
from pydantic import BaseModel, Field
from sqlalchemy import func
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


class UserAddRequest(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    initials: str = Field(min_length=2, max_length=4)
    name: str = Field(min_length=2, max_length=30)
    userRole: str = Field(min_length=3,max_length=10)
    userStatus: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=6, max_length=20)

class UserEditRequest(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    initials: str = Field(min_length=2, max_length=4)
    name: str = Field(min_length=2, max_length=30)
    userRole: str = Field(min_length=3,max_length=10)
    userStatus: str = Field(min_length=3, max_length=10)

class UserPasswordRequest(BaseModel):
    password: str = Field(min_length=6, max_length=20)

##this should be a shared function
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

@router.get("/user-page")
async def render_user_page(request: Request, db: db_dependency):
    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))

        if loginUser is None:
           return redirect_to_login()

        ## Get saved filtering values
        userRoleFilter =request.cookies.get('userRoleFilter')
        userStatusFilter =request.cookies.get('userStatusFilter')

        ##build dynamic query
        query = db.query(Users)

        if userRoleFilter is not None and userRoleFilter != "ALL":
            query = query.filter(Users.userRole == userRoleFilter)

        if userStatusFilter is not None and userStatusFilter != "ALL":
            query = query.filter(Users.userStatus == userStatusFilter)

        userList = query.all()

        return templates.TemplateResponse("user.html", {"request": request, "users": userList, "currentUser": loginUser})

    except:
        return redirect_to_login()

@router.get('/add-user-page')
async def render_user_page(request: Request):

    try:

        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()

        #default values
        user_default = Users(
            username="",
            initials="",
            name="",
            userRole="",
            userStatus="",
        )

        return templates.TemplateResponse("add-edit-view-user.html",
                         {"request": request,"user": user_default, "currentUser": loginUser, "mode": "ADD"})

    except:
        return redirect_to_login()


@router.get("/edit-user-page/{user_id}")
async def render_user_edit_page(request: Request, user_id: int, db: db_dependency):

    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()

        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None:
            raise HTTPException(status_code=404, detail='User not found.')

        return templates.TemplateResponse("add-edit-view-user.html",
                        {"request": request, "user": user_model, "currentUser": loginUser, "mode": "EDIT"})

    except:
        return redirect_to_login()

@router.get("/view-user-page/{user_id}")
async def render_user_view_page(request: Request, user_id: int, db: db_dependency):
    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))

        if loginUser is None:
            return redirect_to_login()


        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None:
            raise HTTPException(status_code=404, detail='User not found.')

        return templates.TemplateResponse("add-edit-view-user.html",
                                {"request": request, "user": user_model, "currentUser": loginUser, "mode": "VIEW"})
    except:
        return redirect_to_login()



@router.get("/password-user-page/{user_id}")
async def render_user_password_page(request: Request, user_id: int, db: db_dependency):
    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))

        if loginUser is None:
            return redirect_to_login()

        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None:
            raise HTTPException(status_code=404, detail='User not found.')

        return templates.TemplateResponse("password-user.html",
                                    {"request": request, "user": user_model, "currentUser": loginUser})

    except:
        return redirect_to_login()


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(user: user_dependency, db: db_dependency,
                      user_request: UserAddRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')


    create_user_model = Users(
        username = user_request.username,
        initials = user_request.initials,
        name = user_request.name,
        userRole = user_request.userRole,
        userStatus = user_request.userStatus,
        hashedPassword=bcrypt_context.hash(user_request.password),
        createdBy=login_user_model.initials,
    )

    db.add(create_user_model)
    db.commit()

@router.put("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency,
                      user_request: UserEditRequest,
                      user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')

    save = user_model.hashedPassword

    user_model.username = user_request.username
    user_model.initials = user_request.initials
    user_model.name = user_request.name
    user_model.userRole = user_request.userRole
    user_model.userStatus = user_request.userStatus
    user_model.updatedDate = server_default=func.now()
    user_model.updatedBy= login_user_model.initials

    db.add(user_model)
    db.commit()

@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency,
                      user_id: int = Path(gt=0)):

    if user is None or user.get('userRole') != 'ADMIN' :
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User Not found.')

    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()


@router.put("/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(user: user_dependency, db: db_dependency,
                      user_request: UserPasswordRequest,
                      user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')

    user_model.hashedPassword = bcrypt_context.hash(user_request.password)
    user_model.updatedDate = server_default=func.now()
    user_model.updatedBy = login_user_model.initials

    db.add(user_model)
    db.commit()


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(user.id == user_id).first()

    if user_model is not None:
        return user_model

    raise HTTPException(status_code=404, detail='user not found.')

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashedPassword):
       raise HTTPException(status_code=401, detail='Error on password change')

    user_model.hashedPassword = bcrypt_context.hash(user_verification.new_password)
    user_model.updatedDate = server_default=func.now()

    db.add(user_model)
    db.commit()


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()








