from typing import Annotated

from click import confirm
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette import status
from ..models import Assets, Todos, Users
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="AssetMgtApp/templates")

router = APIRouter(
    prefix='/assets',
    tags=['assets']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class AssetRequest(BaseModel):
    majorArea: str = Field(min_length=3, max_length=10)
    minorArea: str = Field(min_length=3, max_length=10)
    assetType: str = Field(min_length=3, max_length=10)
    description: str = Field(min_length=3, max_length=40)
    assetState: str = Field(min_length=3, max_length=10)
    model: str = Field(max_length=20)
    satellite: str = Field(max_length=20)
    station: str = Field(max_length=20)
    gpsLat: Optional[float] = None
    gpsLng: Optional[float] = None


##this should be a shared function
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

@router.get("/asset-page")
async def render_asset_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
           return redirect_to_login()

        ## Get saved filtering values
        majorAreaFilter =request.cookies.get('majorAreaFilter')
        if majorAreaFilter is None:
            majorAreaFilter = '01ST' ##make the 1st the default to prevent loading a big table by default

        minorAreaFilter =request.cookies.get('minorAreaFilter')
        assetTypeFilter =request.cookies.get('assetTypeFilter')
        assetStateFilter =request.cookies.get('assetStateFilter')


        ##build dynamic query
        query = db.query(Assets)

        if majorAreaFilter is not None and majorAreaFilter != "ALL":
            query = query.filter(Assets.majorArea == majorAreaFilter)

        if minorAreaFilter is not None and minorAreaFilter != "ALL":
            query = query.filter(Assets.minorArea == minorAreaFilter)

        if assetTypeFilter is not None and assetTypeFilter != "ALL":
            query = query.filter(Assets.assetType == assetTypeFilter)

        if assetStateFilter is not None and assetStateFilter != "ALL":
            query = query.filter(Assets.assetState == assetStateFilter)

        assetList = query.all()

        return templates.TemplateResponse("asset.html", {"request": request, "assets": assetList, "currentUser": user})

    except:
        return redirect_to_login()


@router.get('/add-asset-page')
async def render_asset_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        #default values
        asset_default = Assets(
            majorArea="",
            minorArea="",
            assetType="",
            description="",
            assetState="",
            model="",
            satellite = "",
            station = "",
            gpsLat = "",
            gpsLng = ""
        )

        return templates.TemplateResponse("add-edit-asset.html", {"request": request,
                                    "asset" : asset_default, "currentUser": user,"mode": "ADD"})

    except:
        return redirect_to_login()

@router.get("/edit-asset-page/{asset_id}")
async def render_edit_asset_page(request: Request, asset_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        asset_model = db.query(Assets).filter(Assets.id == asset_id).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        #force None to ""
        if asset_model.gpsLat is None:
            asset_model.gpsLat = ""

        if asset_model.gpsLng is None:
            asset_model.gpsLng = ""

        return templates.TemplateResponse("add-edit-asset.html", {"request": request,
                                    "asset": asset_model, "currentUser": user, "mode": "EDIT"})

    except:
        return redirect_to_login()


@router.get("/view-asset-page/{asset_id}")
async def render_view_asset_page(request: Request, asset_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        asset_model = db.query(Assets).filter(Assets.id == asset_id).first()
        if asset_model is None:
            raise HTTPException(status_code=404, detail='Asset not found.')

        todo_list = db.query(Todos).filter(Todos.assetId == asset_id).all()

        return templates.TemplateResponse("view-asset.html", {"request": request, "asset": asset_model, "todo_list": todo_list, "currentUser": user})

    except:
        return redirect_to_login()

### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Assets).all()


@router.get("/asset/{asset_id}", status_code=status.HTTP_200_OK)
async def read_asset(user: user_dependency, db: db_dependency, asset_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    asset_model = db.query(Assets).filter(Assets.id == asset_id).first()

    if asset_model is not None:
        return asset_model
    raise HTTPException(status_code=404, detail=' not found.')


@router.post("/asset", status_code=status.HTTP_201_CREATED)
async def create_asset(user: user_dependency, db: db_dependency,
                      asset_request: AssetRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    create_asset_model = Assets(
        majorArea=asset_request.majorArea,
        minorArea=asset_request.minorArea,
        assetType=asset_request.assetType,
        description=asset_request.description,
        assetState=asset_request.assetState,
        model=asset_request.model,
        satellite = asset_request.satellite,
        station = asset_request.station,
        gpsLat=asset_request.gpsLat,
        gpsLng=asset_request.gpsLng,
        createdBy = login_user_model.initials,
    )

    #asset_model = Assets(**asset_request.model_dump())

    db.add(create_asset_model)
    db.commit()


@router.put("/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_asset(user: user_dependency, db: db_dependency,
                      asset_request: AssetRequest,
                      asset_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    login_user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if login_user_model is None:
        raise HTTPException(status_code=404, detail='login user Not found.')

    asset_model = db.query(Assets).filter(Assets.id == asset_id).first()

    if asset_model is None:
        raise HTTPException(status_code=404, detail='Asset not found.')

    errors = {}
    try:
        asset_model.majorArea = asset_request.majorArea
        asset_model.minorArea = asset_request.minorArea
        asset_model.assetType = asset_request.assetType
        asset_model.description = asset_request.description
        asset_model.assetState = asset_request.assetState
        asset_model.model = asset_request.model
        asset_model.satellite = asset_request.satellite
        asset_model.station = asset_request.station
        asset_model.gpsLat = asset_request.gpsLat
        asset_model.gpsLng = asset_request.gpsLng
        asset_model.updatedDate = func.now()
        asset_model.updatedBy= login_user_model.initials

        db.add(asset_model)
        db.commit()
        return {"message": "User updated successfully"}

    except IntegrityError as e:
        db.rollback()
        #no expected errors
        raise HTTPException(status_code=422, detail=errors)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=errors)


@router.delete("/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(user: user_dependency, db: db_dependency, asset_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')


    #delete all todos for asset
    db.query(Todos).filter(Todos.assetId == asset_id).delete()

    asset_model = db.query(Assets).filter(Assets.id == asset_id).first()
    if asset_model is None:
        raise HTTPException(status_code=404, detail='Asset not found.')
    db.query(Assets).filter(Assets.id == asset_id).delete()

    db.commit()

