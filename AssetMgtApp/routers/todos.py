from typing import Annotated

from click import confirm
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.cyextension.processors import to_str
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.testing.schema import mapped_column
from starlette import status
from ..models import Todos, Assets, Users
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="AssetMgtApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str
    priority: str = Field(min_length=3, max_length=10)
    todoStatus: str = Field(min_length=3, max_length=10)
    assignedTo: str

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
           return redirect_to_login()

        ## Get saved filtering values
        assignedToFilter =request.cookies.get('assignedToFilter')
        todoStatusFilter =request.cookies.get('todoStatusFilter')
        priorityFilter =request.cookies.get('priorityFilter')
        majorAreaFilter =request.cookies.get('majorAreaFilter')
        minorAreaFilter =request.cookies.get('minorAreaFilter')
        assetTypeFilter =request.cookies.get('assetTypeFilter')


        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.title,
            Todos.assignedTo,
            Todos.assetId,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType
        ).join(Assets, Todos.assetId == Assets.id)

#       todoList = query.all()

#       build dynamic query
        if assignedToFilter is not None and assignedToFilter != "All":
            query = query.filter(Todos.assignedTo == assignedToFilter)

        if todoStatusFilter is not None and todoStatusFilter != "All":
            query = query.filter(Todos.todoStatus == todoStatusFilter)

        if priorityFilter is not None and priorityFilter != "All":
            query = query.filter(Todos.priority == priorityFilter)

        if majorAreaFilter is not None and majorAreaFilter != "All":
            query = query.filter(Assets.majorArea == majorAreaFilter)

        if minorAreaFilter is not None and minorAreaFilter != "All":
            query = query.filter(Assets.minorArea == minorAreaFilter)

        if assetTypeFilter is not None and assetTypeFilter != "All":
            query = query.filter(Assets.assetType == assetTypeFilter)

        todoList = query.all()

        return templates.TemplateResponse("todo.html", {"request": request,
                                    "todos": todoList, "currentUser": user})

    except:
        return redirect_to_login()


@router.get("/todo-list/{todo_id}")
async def render_todo_list(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
           return redirect_to_login()

        ## Get saved filtering values
        assignedToFilter =request.cookies.get('assignedToFilter')
        todoStatusFilter =request.cookies.get('todoStatusFilter')
        priorityFilter =request.cookies.get('priorityFilter')
        majorAreaFilter =request.cookies.get('majorAreaFilter')
        minorAreaFilter =request.cookies.get('minorAreaFilter')
        assetTypeFilter =request.cookies.get('assetTypeFilter')


        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.title,
            Todos.assignedTo,
            Todos.assetId,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType
        ).join(Assets, Todos.assetId == Assets.id)

#       todoList = query.all()

#       build dynamic query
        if assignedToFilter is not None and assignedToFilter != "All":
            query = query.filter(Todos.assignedTo == assignedToFilter)

        if todoStatusFilter is not None and todoStatusFilter != "All":
            query = query.filter(Todos.todoStatus == todoStatusFilter)

        if priorityFilter is not None and priorityFilter != "All":
            query = query.filter(Todos.priority == priorityFilter)

        if majorAreaFilter is not None and majorAreaFilter != "All":
            query = query.filter(Assets.majorArea == majorAreaFilter)

        if minorAreaFilter is not None and minorAreaFilter != "All":
            query = query.filter(Assets.minorArea == minorAreaFilter)

        if assetTypeFilter is not None and assetTypeFilter != "All":
            query = query.filter(Assets.assetType == assetTypeFilter)

        todoList = query.all()

        #todo_id is passed to set the current row in the table
        return templates.TemplateResponse("todo.html", {"request": request,
                                    "todos": todoList, "todo_id": todo_id, "currentUser": user})

    except:
        return redirect_to_login()


@router.get('/add-todo-page/{asset_id}')
async def render_todo_page(request: Request, asset_id: int,db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
        if login_user_model is None:
            raise HTTPException(status_code=404, detail='login user Not found.')

        #list of users for assignedTo select options
        userList = db.query(Users).all()

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == asset_id).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        #default values
        todo_default = Todos(
            title="",
            description="",
            todoStatus="",
            priority="",
            assignedTo=login_user_model.initials, # current user should be default assignedTo
            assetId=asset_id
        )

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request,
                            "todo" : todo_default, "asset": asset_model, "todo_id" : 0,
                              "currentUser": user, "users": userList, "redirect": "T","mode": "ADD"})
    except:
        return redirect_to_login()

@router.get('/add-todo-asset-page/{asset_id}')
async def render_todo_page(request: Request, asset_id: int,db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
        if login_user_model is None:
            raise HTTPException(status_code=404, detail='login user Not found.')

        #list of users for assignedTo select options
        userList = db.query(Users).all()

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == asset_id).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        #default values
        todo_default = Todos(
            title="",
            description="",
            todoStatus="",
            priority="",
            assignedTo=login_user_model.initials,
            assetId=asset_id
        )
        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request,
                            "todo" : todo_default, "asset": asset_model, "todo_id" : 0,
                            "currentUser": user, "users": userList,"redirect": "A","mode": "ADD"})

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        #list of users for assignedTo select options
        userList = db.query(Users).all()

        # get the current todo details
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                     "asset": asset_model, "todo_id": todo_id, "users": userList,
                                    "currentUser": user,"redirect": "T","mode": "EDIT"})

    except:
        return redirect_to_login()

@router.get("/edit-todo-asset-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        #list of users for assignedTo select options
        userList = db.query(Users).all()

        # get the current todo details
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                     "asset": asset_model, "todo_id": todo_id, "users": userList,
                                     "currentUser": user,"redirect": "A","mode": "EDIT"})
    except:
        return redirect_to_login()

@router.get("/view-todo-page/{todo_id}")
async def render_view_asset_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                     "asset": asset_model, "todo_id": todo_id,
                                     "currentUser": user, "redirect": "T", "mode": "VIEW"})

    except:
        return redirect_to_login()

@router.get("/view-todo-asset-page/{todo_id}")
async def render_view_asset_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                    "asset": asset_model, "todo_id": todo_id,
                                    "currentUser": user, "redirect": "A", "mode": "VIEW"})

    except:
        return redirect_to_login()

### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail=' not found.')

@router.post("/todo-add/{asset_id}", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      asset_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    create_todo_model = Todos(
       title=todo_request.title,
       description=todo_request.description,
       todoStatus=todo_request.todoStatus,
       priority=todo_request.priority,
       assignedTo =todo_request.assignedTo,
       assetId = asset_id,
       createdBy = login_user_model.initials,
    )

#    todo_model = Todos(**todo_request.model_dump())

    db.add(create_todo_model)
    db.commit()

@router.put("/todo-update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')


    # get the rows current values
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    #update the columns with form data
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.todoStatus = todo_request.todoStatus
    todo_model.assignedTo = todo_request.assignedTo
    todo_model.updatedDate = server_default=func.now()
    todo_model.updatedBy= login_user_model.initials

    db.add(todo_model)
    db.commit()


@router.delete("/todo-delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()
