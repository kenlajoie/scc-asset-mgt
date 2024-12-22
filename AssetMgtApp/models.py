from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Assets(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, index=True)
    majorArea = Column(String)
    minorArea = Column(String)
    microArea = Column(String)
    assetType = Column(String)
    description = Column(String)
    assetState = Column(String)
    gpsLat  = Column(Double)
    gpsLng = Column(Double)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    asset_id = Column(Integer, ForeignKey("assets.id"))

