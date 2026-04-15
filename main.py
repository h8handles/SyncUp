from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base, Group, User, Availability
from .schemas import GroupCreate, UserCreate, AvailabilityCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.post("/groups/", response_model=GroupCreate)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, group_id=user.group_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/availabilities/", response_model=AvailabilityCreate)
def create_availability(availability: AvailabilityCreate, db: Session = Depends(get_db)):
    db_availability = Availability(user_id=availability.user_id, availability=availability.availability)
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

@app.get("/groups/{group_id}/availabilities/", response_model=list[AvailabilityCreate])
def list_group_availabilities(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    availabilities = db.query(Availability).filter(Availability.user_id.in_([user.id for user in group.users])).all()
    return availabilities
