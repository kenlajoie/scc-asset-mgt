from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import func
#from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
#from sqlalchemy.cyextension.processors import to_str

from sqlalchemy.orm import Session
from sqlalchemy import and_

#from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi import APIRouter, Depends, HTTPException, Path, Request
#from sqlalchemy.testing.schema import mapped_column
from starlette import status
#from ..models import Todos, Assets, Users, Dropdown
from ..models import Todos, Assets, Users
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from .dropdown import get_dropdown_list
from .users import get_user_dropdown_list

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
    task: str = Field(min_length=3, max_length=40)
    note: str
    priority: str = Field(min_length=3, max_length=10)
    todoStatus: str = Field(min_length=3, max_length=10)
    assignedTo: str= Field(min_length=3, max_length=10)

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

        #list of users for assignedTo select options
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        ## Get saved filtering values
        assignedToFilter =request.cookies.get('assignedToFilter')
        todoStatusFilter =request.cookies.get('todoStatusFilter')
        priorityFilter =request.cookies.get('priorityFilter')
        todoMajorAreaFilter =request.cookies.get('todoMajorAreaFilter')
        todoMinorAreaFilter =request.cookies.get('todoMinorAreaFilter')
        todoAssetTypeFilter =request.cookies.get('todoAssetTypeFilter')


        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.assignedTo,
            Todos.assetId,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType
#        ).join(Assets, Todos.assetId == Assets.id)
        ).join(Assets, Todos)

#       todoList = query.all()

#       build dynamic query

        query = query.filter(and_(Todos.assetId == Assets.id))

        if assignedToFilter is not None and assignedToFilter != "ALL":
            #query = query.filter(Todos.assignedTo == assignedToFilter)
            query = query.filter(and_(Todos.assignedTo == assignedToFilter))

        if todoStatusFilter is not None and todoStatusFilter != "ALL":
            #query = query.filter(Todos.todoStatus == todoStatusFilter)
            query = query.filter(and_(Todos.todoStatus == todoStatusFilter))

        if priorityFilter is not None and priorityFilter != "ALL":
            #query = query.filter(Todos.priority == priorityFilter)
            query = query.filter(and_(Todos.priority == priorityFilter))

        if todoMajorAreaFilter is not None and todoMajorAreaFilter != "ALL":
            #query = query.filter(Assets.majorArea == todoMajorAreaFilter)
            query = query.filter(and_(Assets.majorArea == todoMajorAreaFilter))

        if todoMinorAreaFilter is not None and todoMinorAreaFilter != "ALL":
            #query = query.filter(Assets.minorArea == todoMinorAreaFilter)
            query = query.filter(and_(Assets.minorArea == todoMinorAreaFilter))

        if todoAssetTypeFilter is not None and todoAssetTypeFilter != "ALL":
            #query = query.filter(Assets.assetType == todoAssetTypeFilter)
            query = query.filter(and_(Assets.assetType == todoAssetTypeFilter))

        todoList = query.all()

        return templates.TemplateResponse("todo.html", {"request": request,
                                    "todos": todoList, "currentUser": user,
                                     "users": userList,"dropdown": dropdownList})

    except:
        return redirect_to_login()


@router.get("/todo-report-page")
async def render_todo_report_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
           return redirect_to_login()

        ## Get saved filtering values
        assignedToFilter =request.cookies.get('assignedToFilter')
        todoStatusFilter =request.cookies.get('todoStatusFilter')
        priorityFilter =request.cookies.get('priorityFilter')
        todoMajorAreaFilter =request.cookies.get('todoMajorAreaFilter')
        todoMinorAreaFilter =request.cookies.get('todoMinorAreaFilter')
        todoAssetTypeFilter =request.cookies.get('todoAssetTypeFilter')

        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.note,
            Todos.assignedTo,
            Todos.assetId,
            func.strftime('%m/%d/%Y', Todos.createdDate).label('createdDate'),
            Todos.createdBy,
            func.strftime('%m/%d/%Y', Todos.updatedDate).label('updatedDate'),
            Todos.updatedBy,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType,
            Assets.model,
            Assets.assetState,
            Assets.satellite,
            func.ifnull(func.round(Assets.gpsLat,8),"").label('gpsLat'),
            func.ifnull(func.round(Assets.gpsLng,8),"").label('gpsLng'),
            func.ifnull(func.round(Assets.distance,1),"").label('distance')
#        ).join(Assets, Todos.assetId == Assets.id)
        ).join(Assets, Todos)

#       todoList = query.all()

#       build dynamic query
        query = query.filter(and_(Todos.assetId == Assets.id))

        if assignedToFilter is not None and assignedToFilter != "ALL":
            #query = query.filter(Todos.assignedTo == assignedToFilter)
            query = query.filter(and_(Todos.assignedTo == assignedToFilter))

        if todoStatusFilter is not None and todoStatusFilter != "ALL":
            #query = query.filter(Todos.todoStatus == todoStatusFilter)
            query = query.filter(and_(Todos.todoStatus == todoStatusFilter))

        if priorityFilter is not None and priorityFilter != "ALL":
            #query = query.filter(Todos.priority == priorityFilter)
            query = query.filter(and_(Todos.priority == priorityFilter))

        if todoMajorAreaFilter is not None and todoMajorAreaFilter != "ALL":
            #query = query.filter(Assets.majorArea == todoMajorAreaFilter)
            query = query.filter(and_(Assets.majorArea == todoMajorAreaFilter))

        if todoMinorAreaFilter is not None and todoMinorAreaFilter != "ALL":
            #query = query.filter(Assets.minorArea == todoMinorAreaFilter)
            query = query.filter(and_(Assets.minorArea == todoMinorAreaFilter))

        if todoAssetTypeFilter is not None and todoAssetTypeFilter != "ALL":
            #query = query.filter(Assets.assetType == todoAssetTypeFilter)
            query = query.filter(and_(Assets.assetType == todoAssetTypeFilter))

        todoList = query.all()

        return templates.TemplateResponse("todo-report.html", {"request": request,
                                    "todos": todoList, "currentUser": user})

    except:
        return redirect_to_login()


@router.get("/todo-list/{todo_id}")
async def render_todo_list(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
           return redirect_to_login()

        #list of users for assignedTo select options
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        ## Get saved filtering values
        assignedToFilter =request.cookies.get('assignedToFilter')
        todoStatusFilter =request.cookies.get('todoStatusFilter')
        priorityFilter =request.cookies.get('priorityFilter')
        todoMajorAreaFilter =request.cookies.get('todoMajorAreaFilter')
        todoMinorAreaFilter =request.cookies.get('todoMinorAreaFilter')
        todoAssetTypeFilter =request.cookies.get('todoAssetTypeFilter')


        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.assignedTo,
            Todos.assetId,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType
#        ).join(Assets, Todos.assetId == Assets.id)
        ).join(Assets, Todos)

#       todoList = query.all()

#       build dynamic query
        query = query.filter(and_(Todos.assetId == Assets.id))

        if assignedToFilter is not None and assignedToFilter != "ALL":
            #query = query.filter(Todos.assignedTo == assignedToFilter)
            query = query.filter(and_(Todos.assignedTo == assignedToFilter))

        if todoStatusFilter is not None and todoStatusFilter != "ALL":
            #query = query.filter(Todos.todoStatus == todoStatusFilter)
            query = query.filter(and_(Todos.todoStatus == todoStatusFilter))

        if priorityFilter is not None and priorityFilter != "ALL":
            #query = query.filter(Todos.priority == priorityFilter)
            query = query.filter(and_(Todos.priority == priorityFilter))

        if todoMajorAreaFilter is not None and todoMajorAreaFilter != "ALL":
            #query = query.filter(Assets.majorArea == todoMajorAreaFilter)
            query = query.filter(and_(Assets.majorArea == todoMajorAreaFilter))

        if todoMinorAreaFilter is not None and todoMinorAreaFilter != "ALL":
            #query = query.filter(Assets.minorArea == todoMinorAreaFilter)
            query = query.filter(and_(Assets.minorArea == todoMinorAreaFilter))

        if todoAssetTypeFilter is not None and todoAssetTypeFilter != "ALL":
            #query = query.filter(Assets.assetType == todoAssetTypeFilter)
            query = query.filter(and_(Assets.assetType == todoAssetTypeFilter))

        todoList = query.all()

        #todo_id is passed to set the current row in the table
        return templates.TemplateResponse("todo.html", {"request": request,
                                    "todos": todoList, "todo_id": todo_id, "currentUser": user,
                                    "users": userList,"dropdown": dropdownList})

    except:
        return redirect_to_login()


@router.get('/add-todo-page/{asset_id}')
async def render_todo_page(request: Request, asset_id: int,db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        #list of users for assignedTo select options
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        login_user_model = db.query(Users).filter(and_(Users.id == user.get('id'))).first()
        if login_user_model is None:
            raise HTTPException(status_code=404, detail='login user Not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(and_(Assets.id == asset_id)).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        #default values
        todo_default = Todos(
            task="",
            note="",
            todoStatus="",
            priority="",
            assignedTo=login_user_model.initials, # current user should be default assignedTo
            assetId=asset_id
        )

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request,
                            "todo" : todo_default, "asset": asset_model, "todo_id" : 0,
                              "currentUser": user, "users": userList, "dropdown": dropdownList,
                            "redirect": "T","mode": "ADD"})
    except:
        return redirect_to_login()

@router.get('/add-todo-asset-page/{asset_id}')
async def render_todo_page(request: Request, asset_id: int,db: db_dependency):
    try:
        # get the current user to set "by" columns
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        #list of users for assignedTo select options
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        login_user_model = db.query(Users).filter(and_(Users.id == user.get('id'))).first()
        if login_user_model is None:
            raise HTTPException(status_code=404, detail='login user Not found.')

        #list of users for assignedTo select options
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        # get the current asset details to show on the form in ready-only
        asset_model = db.query(Assets).filter(and_(Assets.id == asset_id)).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        #default values
        todo_default = Todos(
            task="",
            note="",
            todoStatus="",
            priority="",
            assignedTo=login_user_model.initials,
            assetId=asset_id
        )
        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request,
                            "todo" : todo_default, "asset": asset_model, "todo_id" : 0,
                            "currentUser": user, "users": userList, "dropdown": dropdownList,
                            "redirect": "A","mode": "ADD"})

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
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        # get the current todo details
        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.note,
            Todos.assignedTo,
            Todos.assetId,
            func.strftime('%m/%d/%Y', Todos.createdDate).label('createdDate'),
            Todos.createdBy,
            func.strftime('%m/%d/%Y', Todos.updatedDate).label('updatedDate'),
            Todos.updatedBy
        )
        todo_model = query.filter(and_(Todos.id == todo_id)).first()
        #todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        query = db.query(
            Assets.id,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType,
            Assets.model,
            Assets.assetState,
            Assets.satellite,
            Assets.station,
            func.ifnull(func.round(Assets.gpsLat,8),"").label('gpsLat'),
            func.ifnull(func.round(Assets.gpsLng,8),"").label('gpsLng'),
            func.ifnull(func.round(Assets.distance,1),"").label('distance'),
            func.strftime('%m/%d/%Y', Assets.createdDate).label('createdDate'),
            Assets.createdBy,
            func.strftime('%m/%d/%Y', Assets.updatedDate).label('updatedDate'),
            Assets.updatedBy
        )
        asset_model = query.filter(and_(Assets.id == todo_model.assetId)).first()
        #asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                     "asset": asset_model, "todo_id": todo_id, "currentUser": user,
                                    "users": userList,"dropdown": dropdownList,
                                    "redirect": "T","mode": "EDIT"})

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
        userList = get_user_dropdown_list(db)
        #userList = db.query(Users).all()
        if userList is None:
            raise HTTPException(status_code=404, detail='Dropdown User List not found.')

        dropdownList= get_dropdown_list(db)
        #dropdownList= db.query(Dropdown).order_by(Dropdown.column,Dropdown.order).all()
        if dropdownList is None:
           return redirect_to_login()

        # get the current todo details
        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.note,
            Todos.assignedTo,
            Todos.assetId,
            func.strftime('%m/%d/%Y', Todos.createdDate).label('createdDate'),
            Todos.createdBy,
            func.strftime('%m/%d/%Y', Todos.updatedDate).label('updatedDate'),
            Todos.updatedBy
        )
        todo_model = query.filter(and_(Todos.id == todo_id)).first()
        #todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        query = db.query(
            Assets.id,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType,
            Assets.model,
            Assets.assetState,
            Assets.satellite,
            Assets.station,
            func.ifnull(func.round(Assets.gpsLat,8),"").label('gpsLat'),
            func.ifnull(func.round(Assets.gpsLng,8),"").label('gpsLng'),
            func.ifnull(func.round(Assets.distance,1),"").label('distance'),
            func.strftime('%m/%d/%Y', Assets.createdDate).label('createdDate'),
            Assets.createdBy,
            func.strftime('%m/%d/%Y', Assets.updatedDate).label('updatedDate'),
            Assets.updatedBy
        )
        asset_model = query.filter(and_(Assets.id == todo_model.assetId)).first()
        #asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("add-edit-view-todo.html", {"request": request, "todo": todo_model,
                                     "asset": asset_model, "todo_id": todo_id, "currentUser": user,
                                     "users": userList,"dropdown": dropdownList,
                                     "redirect": "A","mode": "EDIT"})
    except:
        return redirect_to_login()

@router.get("/view-todo-page/{todo_id}")
async def render_view_asset_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.note,
            Todos.assignedTo,
            Todos.assetId,
            func.strftime('%m/%d/%Y', Todos.createdDate).label('createdDate'),
            Todos.createdBy,
            func.strftime('%m/%d/%Y', Todos.updatedDate).label('updatedDate'),
            Todos.updatedBy
        )
        todo_model = query.filter(and_(Todos.id == todo_id)).first()
        #todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        query = db.query(
            Assets.id,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType,
            Assets.model,
            Assets.assetState,
            Assets.satellite,
            Assets.station,
            func.ifnull(func.round(Assets.gpsLat,8),"").label('gpsLat'),
            func.ifnull(func.round(Assets.gpsLng,8),"").label('gpsLng'),
            func.ifnull(func.round(Assets.distance,1),"").label('distance'),
            func.strftime('%m/%d/%Y', Assets.createdDate).label('createdDate'),
            Assets.createdBy,
            func.strftime('%m/%d/%Y', Assets.updatedDate).label('updatedDate'),
            Assets.updatedBy
        )

        asset_model = query.filter(and_(Assets.id == todo_model.assetId)).first()
        #asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
             raise HTTPException(status_code=404, detail='Asset not found.')

        return templates.TemplateResponse("view-todo.html", {"request": request, "todo": todo_model,
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

        query = db.query(
            Todos.id,
            Todos.todoStatus,
            Todos.priority,
            Todos.task,
            Todos.note,
            Todos.assignedTo,
            Todos.assetId,
            func.strftime('%m/%d/%Y', Todos.createdDate).label('createdDate'),
            Todos.createdBy,
            func.strftime('%m/%d/%Y', Todos.updatedDate).label('updatedDate'),
            Todos.updatedBy
        )
        todo_model = query.filter(and_(Todos.id == todo_id)).first()
        #todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')

        # get the current asset details to show on the form in ready-only
        query = db.query(
            Assets.id,
            Assets.majorArea,
            Assets.minorArea,
            Assets.description,
            Assets.assetType,
            Assets.model,
            Assets.assetState,
            Assets.satellite,
            Assets.station,
            func.ifnull(func.round(Assets.gpsLat,8),"").label('gpsLat'),
            func.ifnull(func.round(Assets.gpsLng,8),"").label('gpsLng'),
            func.ifnull(func.round(Assets.distance,1),"").label('distance'),
            func.strftime('%m/%d/%Y', Assets.createdDate).label('createdDate'),
            Assets.createdBy,
            func.strftime('%m/%d/%Y', Assets.updatedDate).label('updatedDate'),
            Assets.updatedBy
        )
        asset_model = query.filter(and_(Assets.id == todo_model.assetId)).first()
        #asset_model = db.query(Assets).filter(Assets.id == todo_model.assetId).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')


        return templates.TemplateResponse("view-todo.html", {"request": request, "todo": todo_model,
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

    todo_model = db.query(Todos).filter(and_(Todos.id == todo_id)).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail=' not found.')

@router.post("/todo-add/{asset_id}", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      asset_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(and_(Users.id == user.get('id'))).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    create_todo_model = Todos(
       task=todo_request.task,
       note=todo_request.note,
       todoStatus=todo_request.todoStatus,
       priority=todo_request.priority,
       assignedTo =todo_request.assignedTo,
       assetId = asset_id,
       createdBy = login_user_model.initials,
       updatedBy=login_user_model.initials,
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

    login_user_model = db.query(Users).filter(and_(Users.id == user.get('id'))).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')


    # get the rows current values
    todo_model = db.query(Todos).filter(and_(Todos.id == todo_id)).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    #update the columns with form data
    todo_model.task = todo_request.task
    todo_model.note= todo_request.note
    todo_model.priority = todo_request.priority
    todo_model.todoStatus = todo_request.todoStatus
    todo_model.assignedTo = todo_request.assignedTo
#    todo_model.updatedDate = server_default=func.now()
    todo_model.updatedDate = func.now()
    todo_model.updatedBy= login_user_model.initials

    db.add(todo_model)
    db.commit()


@router.delete("/todo-delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(and_(Todos.id == todo_id)).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.query(Todos).filter(and_(Todos.id == todo_id)).delete()

    db.commit()

