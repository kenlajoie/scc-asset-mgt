
from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Double, DateTime
from sqlalchemy.sql import func


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    initials = Column(String, unique=True, nullable=False)
    name = Column(String)
    userRole = Column(String)
    userStatus = Column(String)
    hashedPassword = Column(String)
    createdBy = Column(String, ForeignKey("users.initials"))
    #createdDate = Column(DateTime, func.now())
    createdDate = Column(DateTime, default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    #updatedDate = Column(DateTime, func.now())
    updatedDate = Column(DateTime, default=func.now(), onupdate=func.now())

class Assets(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, index=True)
    majorArea = Column(String)
    minorArea = Column(String)
    assetType = Column(String)
    model = Column(String)
    description = Column(String)
    assetState = Column(String)
    satellite = Column(String)
    station = Column(String)
    gpsLat  = Column(Double)
    gpsLng = Column(Double)
    distance = Column(Integer)
    createdBy = Column(String, ForeignKey("users.initials"))
    #createdDate = Column(DateTime, func.now())
    createdDate = Column(DateTime, default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    #updatedDate = Column(DateTime, func.now())
    updatedDate = Column(DateTime, default=func.now(), onupdate=func.now())


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    note = Column(String)
    priority = Column(String)
    todoStatus = Column(String)
    assetId = Column(Integer, ForeignKey("assets.id"))
    assignedTo = Column(String, ForeignKey("users.initials"))
    closedBy = Column(String, ForeignKey("users.initials"))
    closedDate = Column(DateTime)
    createdBy = Column(String, ForeignKey("users.initials"))
    #createdDate = Column(DateTime, func.now())
    createdDate = Column(DateTime, default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    #updatedDate = Column(DateTime, func.now())
    updatedDate = Column(DateTime, default=func.now(), onupdate=func.now())


class Dropdown(Base):
    __tablename__ = 'dropdown'

    id = Column(Integer, primary_key=True, index=True)
    column = Column(String)
    value = Column(String)
    description = Column(String)
    order  = Column(Double)
    gpsLat  = Column(Double)
    gpsLng = Column(Double)
    createdBy = Column(String, ForeignKey("users.initials"))
    #createdDate = Column(DateTime, func.now())
    createdDate = Column(DateTime, default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    #updatedDate = Column(DateTime, func.now())
    updatedDate = Column(DateTime, default=func.now(), onupdate=func.now())
