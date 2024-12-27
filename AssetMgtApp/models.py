from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double, Table

from sqlalchemy.orm import declarative_base, relationship, Mapped


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    firstname = Column(String)
    lastname = Column(String)
    userRole = Column(String)
    userStatus = Column(String)
    hashedPassword = Column(String)
    createdById = Column(Integer)
    updatedById = Column(Integer)

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
    createdById = Column(Integer, ForeignKey("users.id"))
    updatedById = Column(Integer, ForeignKey("users.id"))


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    todoStatus = Column(String)
    assetId = Column(Integer, ForeignKey("assets.id"))
    ownerId = Column(Integer, ForeignKey("users.id"))
    createdById = Column(Integer, ForeignKey("users.id"))
    updatedById = Column(Integer, ForeignKey("users.id"))
    closedById = Column(Integer, ForeignKey("users.id"))

