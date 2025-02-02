from typing import Annotated, Optional

from click import confirm
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request

from starlette import status
from ..models import Dropdown, Users
from ..database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="AssetMgtApp/templates")

router = APIRouter(
    prefix='/dropdown',
    tags=['dropdown']
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

class DropdownRequest(BaseModel):
    column: str = Field(min_length=4, max_length=20)
    value: str = Field(min_length=1, max_length=10)
    description: str = Field(min_length=1, max_length=20)
    order: Optional[float] = None


##this should be a shared function
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


@router.get("/dropdown-page")
async def render_dropdown_page(request: Request, db: db_dependency):
    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))

        if loginUser is None:
           return redirect_to_login()

        distinctColumnList = db.query(Dropdown.column).distinct().all()
        if distinctColumnList is None:
            return redirect_to_login()

        ## Get saved filtering values
        dropdownColumnFilter =request.cookies.get('dropdownColumnFilter')

        ##build dynamic query
        query = db.query(Dropdown)

        if dropdownColumnFilter is not None and dropdownColumnFilter != "ALL":
            query = query.filter(Dropdown.column == dropdownColumnFilter)

        query = query.order_by(Dropdown.column,Dropdown.order)

        dropdownList = query.all()

        return templates.TemplateResponse("dropdown.html", {"request": request, "dropdown": dropdownList,
                                          "distinctColumnList": distinctColumnList, "currentUser": loginUser})

    except:
        return redirect_to_login()



@router.get('/addx-dropdown-page')  #to start a new column.
async def render_dropdown_page(request: Request):
    try:

        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()

        #default values
        dropdown_default = Dropdown(
            column="",
            value="",
            description="",
            order=""
        )

        return templates.TemplateResponse("add-edit-view-dropdown.html",
                         {"request": request,"dropdown": dropdown_default, "currentUser": loginUser, "mode": "ADDX"})

    except:
        return redirect_to_login()


@router.get("/add-dropdown-page/{dropdown_id}")  #from and existing row button.. pass the column
async def render_dropdown_value_page(request: Request, dropdown_id: int, db: db_dependency):

    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()

        #lookup the details of the current row to get the column
        dropdown_model = db.query(Dropdown).filter(Dropdown.id == dropdown_id).first()
        if dropdown_model is None:
            raise HTTPException(status_code=404, detail='dropdown not found.')

        #default values
        dropdown_default = Dropdown(
            column=dropdown_model.column,
            value="",
            description="",
            order=""
        )

        return templates.TemplateResponse("add-edit-view-dropdown.html",
                        {"request": request, "dropdown": dropdown_default, "currentUser": loginUser, "mode": "ADD"})

    except:
        return redirect_to_login()

@router.get("/edit-dropdown-page/{dropdown_id}")
async def render_dropdown_edit_page(request: Request, dropdown_id: int, db: db_dependency):

    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()

        dropdown_model = db.query(Dropdown).filter(Dropdown.id == dropdown_id).first()
        if dropdown_model is None:
            raise HTTPException(status_code=404, detail='dropdown not found.')

        #force None to ""
        if dropdown_model.order is None:
            dropdown_model.order = ""


        return templates.TemplateResponse("add-edit-view-dropdown.html",
                        {"request": request, "dropdown": dropdown_model, "currentUser": loginUser, "mode": "EDIT"})

    except:
        return redirect_to_login()

@router.get("/view-dropdown-page/{dropdown_id}")
async def render_dropdown_view_page(request: Request, dropdown_id: int, db: db_dependency):
    try:
        loginUser = await get_current_user(request.cookies.get('access_token'))
        if loginUser is None:
            return redirect_to_login()


        dropdown_model = db.query(Dropdown).filter(Dropdown.id == dropdown_id).first()
        if dropdown_model is None:
            raise HTTPException(status_code=404, detail='Dropdown not found.')

        return templates.TemplateResponse("add-edit-view-dropdown.html",
                                {"request": request, "dropdown": dropdown_model, "currentUser": loginUser, "mode": "VIEW"})
    except:
        return redirect_to_login()




@router.post("/dropdown", status_code=status.HTTP_201_CREATED)
async def create_dropdown(user: user_dependency, db: db_dependency,
                        dropdown_request: DropdownRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    errors = {}
    try:
        create_dropdown_model = Dropdown(
            column=dropdown_request.column.upper(),
            value=dropdown_request.value.upper(),
            description=dropdown_request.description,
            order=dropdown_request.order,
            createdBy=login_user_model.initials,
        )
        create_dropdown_model.createdDate = func.now()

        db.add(create_dropdown_model)
        db.commit()

        return {"message": "Dropdown created successfully"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=errors)

    except SQLAlchemyError as e:
        db.rollback()
        #confirm(e.__str__())
        raise HTTPException(status_code=422, detail=errors)


@router.put("/dropdown/{dropdown_id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_dropdown_value(user: user_dependency, db: db_dependency,
                      dropdown_request: DropdownRequest,
                      dropdown_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    dropdown_model = db.query(Dropdown).filter(Dropdown.id == dropdown_id).first()
    if dropdown_model is None:
        raise HTTPException(status_code=404, detail='Dropdown not found.')

    errors = {}
    try:
        dropdown_model.column = dropdown_request.column.upper()
        dropdown_model.value = dropdown_request.value.upper()
        dropdown_model.description = dropdown_request.description
        dropdown_model.order = dropdown_request.order
        dropdown_model.updatedDate = func.now()
        dropdown_model.updatedBy= login_user_model.initials

        db.add(dropdown_model)
        db.commit()
        return {"message": "Dropdown updated successfully"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=errors)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=errors)


@router.delete("/dropdown/{dropdown_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency,
                      dropdown_id: int = Path(gt=0)):

    if user is None or user.get('userRole') != 'ADMIN' :
        raise HTTPException(status_code=401, detail='Authentication Failed')

    dropdown_model = db.query(Dropdown).filter(Dropdown.id == dropdown_id).first()
    if dropdown_model is None:
        raise HTTPException(status_code=404, detail='Dropdown Not found.')

    db.query(Dropdown).filter(Dropdown.id == dropdown_id).delete()
    db.commit()


