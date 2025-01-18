import datetime

from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double, Table, DateTime, func
from datetime import datetime

from sqlalchemy.orm import declarative_base, relationship, Mapped


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    initials = Column(String, unique=True)
    name = Column(String)
    userRole = Column(String)
    userStatus = Column(String)
    hashedPassword = Column(String)
    createdBy = Column(String, ForeignKey("users.initials"))
    createdDate = Column(DateTime, server_default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    updatedDate = Column(DateTime)

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
    createdBy = Column(String, ForeignKey("users.initials"))
    createdDate = Column(DateTime, server_default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    updatedDate = Column(DateTime)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    todoStatus = Column(String)
    assetId = Column(Integer, ForeignKey("assets.id"))
    assignedTo = Column(String, ForeignKey("users.initials"))
    closedBy = Column(String, ForeignKey("users.initials"))
    closedDate = Column(DateTime)
    createdBy = Column(String, ForeignKey("users.initials"))
    createdDate = Column(DateTime, server_default=func.now())
    updatedBy = Column(String, ForeignKey("users.initials"))
    updatedDate = Column(DateTime)

