from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, Group, User, Availability
from schemas import GroupCreate, UserCreate, AvailabilityCreate
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

@app.get("/create-group")
async def get_create_group(request: Request):
    return templates.TemplateResponse("create_group.html", {"request": request})

@app.post("/groups/")
async def post_create_group(name: str = Form(...), db: Session = Depends(get_db)):
    db_group = Group(name=name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return {"status": "Group created successfully"}

@app.get("/add-member")
async def get_add_member(request: Request):
    groups = db.query(Group).all()
    return templates.TemplateResponse("add_member.html", {"request": request, "groups": groups})

@app.post("/users/")
async def post_add_member(username: str = Form(...), group_id: int = Form(...), db: Session = Depends(get_db)):
    db_user = User(username=username, group_id=group_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"status": "User added successfully"}

@app.get("/submit-availability")
async def get_submit_availability(request: Request):
    users = db.query(User).all()
    return templates.TemplateResponse("submit_availability.html", {"request": request, "users": users})

@app.post("/availabilities/")
async def post_submit_availability(user_id: int = Form(...), availability: str = Form(...), db: Session = Depends(get_db)):
    db_availability = Availability(user_id=user_id, availability=availability)
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return {"status": "Availability submitted successfully"}

@app.get("/groups/{group_id}/best-times")
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
    return {"best_times": best_times}

@app.get("/display-best-times")
async def get_display_best_times(request: Request):
    groups = db.query(Group).all()
    return templates.TemplateResponse("display_best_times.html", {"request": request, "groups": groups})

def parse_time_slots(availability_str):
    time_slots = []
    for match in re.finditer(r'(\d{2}:\d{2})-(\d{2}:\d{2})', availability_str):
        start, end = match.groups()
        time_slots.append(f"{start}-{end}")
    return time_slots
