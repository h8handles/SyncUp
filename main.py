from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base, Group, User, Availability
from .schemas import GroupCreate, UserCreate, AvailabilityCreate
import re

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

@app.get("/groups/{group_id}/best-times", response_model=list[dict])
def get_best_times(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    availabilities = db.query(Availability).filter(Availability.user_id.in_([user.id for user in group.users])).all()
    
    availability_dict = {}
    for availability in availabilities:
        if availability.user_id not in availability_dict:
            availability_dict[availability.user_id] = []
        availability_dict[availability.user_id].extend(parse_time_slots(availability.availability))
    
    all_timeslots = set.intersection(*[set(timeslots) for timeslots in availability_dict.values()])
    best_times = []
    
    for timeslot in all_timeslots:
        users_available = [user_id for user_id, timeslots in availability_dict.items() if timeslot in timeslots]
        attendance_score = len(users_available) / len(group.users)
        best_times.append({
            "timeslot": timeslot,
            "users_available": users_available,
            "attendance_score": attendance_score
        })
    
    best_times.sort(key=lambda x: (-len(x['users_available']), -x['attendance_score']))
    return best_times

def parse_time_slots(availability_str):
    time_slots = []
    for match in re.finditer(r'(\d{2}:\d{2})-(\d{2}:\d{2})', availability_str):
        start, end = match.groups()
        time_slots.append(f"{start}-{end}")
    return time_slots
