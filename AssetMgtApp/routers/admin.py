from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..database import SessionLocal  #was ..
from ..models import Assets            #was ..
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/assets", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Assets).all()


@router.delete("/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(user: user_dependency, db: db_dependency, Assets_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    asset_model = db.query(Assets).filter(Asset.id == asset_id).first()
    if asset_model is None:
        raise HTTPException(status_code=404, detail='Asset not found.')
    db.query(Assets).filter(Asset.id == asset_id).delete()
    db.commit()
