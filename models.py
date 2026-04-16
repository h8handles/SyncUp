from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    invite_code = Column(String, unique=True, index=True, nullable=False)  # New field for invite code

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="users")

class Availability(Base):
    __tablename__ = 'availabilities'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    availability = Column(String)  # Correct field name
    status_value = Column(String)  # Correct field name

Group.users = relationship("User", order_by=User.id, back_populates="group")
