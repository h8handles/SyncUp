from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, Group, User, Availability
from schemas import GroupCreate
from fastapi.templating import Jinja2Templates
import re
import secrets
import string
import logging

# Configure simple INFO-level logging for MVP debugging and route visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
async def read_root(request: Request):
    logger.info("Homepage loaded")
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.post("/groups/", response_model=GroupCreate)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    # Generate a unique invite code
    invite_code = generate_invite_code(db)
    
    db_group = Group(name=group.name, invite_code=invite_code)  # Assign the generated invite code
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    logger.info(f"Group created: {db_group.name} with invite code: {db_group.invite_code}")
    return db_group

@app.get("/create-group")
async def get_create_group(request: Request):
    logger.info("Create group page loaded")
    return templates.TemplateResponse(request, "create_group.html", {"request": request})

@app.post("/create-group")  # Ensure this route is correctly defined
async def post_create_group(name: str = Form(...), db: Session = Depends(get_db)):
    try:
        new_group = Group(name=name)
        invite_code = generate_invite_code(db)  # Generate a unique invite code
        new_group.invite_code = invite_code  # Assign the generated invite code
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        logger.info(f"Group created: {new_group.name} with invite code: {db_group.invite_code}")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/add-member")
async def get_add_member(request: Request, db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    return templates.TemplateResponse(request, "add_member.html", {"request": request, "groups": groups})

@app.post("/users/")
async def post_add_member(username: str = Form(...), group_id: int = Form(...), db: Session = Depends(get_db)):
    db_user = User(username=username, group_id=group_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {db_user.username} in group: {group_id}")
    return {"status": "User added successfully"}

@app.get("/submit-availability")
async def get_submit_availability(request: Request, db: Session = Depends(get_db)):
    """
    Render the submit availability form page.
    """
    users = db.query(User).all()
    logger.info("Submit availability page loaded")
    return templates.TemplateResponse(request, "submit_availability.html", {"request": request, "users": users})

@app.post("/submit-availability")
async def post_submit_availability(
    user_id: int = Form(...),
    day: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    status_value: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle the submit availability form submission and save the record.
    
    Note: Form field names are mapped to the model's actual column names.
    """
    try:
        # Map form fields to the correct model fields
        new_availability = Availability(
            user_id=user_id,
            availability=f"{start_time}-{end_time}",
            status_value=status_value
        )
        db.add(new_availability)
        db.commit()
        db.refresh(new_availability)
        logger.info(f"Availability submitted for user {user_id} on {day} from {start_time} to {end_time} with status {status_value}")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error submitting availability: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/groups/{group_id}/best-times")
def get_best_times(group_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to get the best times for a specific group.
    
    Args:
        group_id (int): The ID of the group. This is a path parameter, not a query string.
        
    Returns:
        dict: A dictionary containing the best times for the group.
    """
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
    logger.info(f"Best times calculated for group {group_id}: {best_times}")
    return {"best_times": best_times}

@app.get("/display-best-times")
async def get_display_best_times(request: Request, db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    logger.info("Display best times page loaded")
    return templates.TemplateResponse(request, "display_best_times.html", {"request": request, "groups": groups})

@app.get("/groups/join")
async def get_join_group(request: Request):
    """Render the join group form page."""
    logger.info("Join group page loaded")
    return templates.TemplateResponse(
        request,
        "join_group.html",
        {"request": request}
    )

@app.post("/groups/join")
async def join_group(
    request: Request,  # Add request parameter
    display_name: str = Form(...),
    invite_code: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle join form submission and re-render the page on invalid invite codes.
    """
    group = db.query(Group).filter(Group.invite_code == invite_code).first()
    if not group:
        logger.warning(f"Invalid invite code submitted: {invite_code}")
        return templates.TemplateResponse(request, "join_group.html", {"request": request, "error": "Invalid invite code"})
    
    db_user = User(username=display_name, group_id=group.id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {display_name} joined group with invite code: {invite_code}")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/groups")
async def get_groups(request: Request, db: Session = Depends(get_db)):
    """
    Simple testing page for viewing created groups.
    """
    groups = db.query(Group).all()
    logger.info("Groups listing page loaded")
    return templates.TemplateResponse(request, "groups.html", {"request": request, "groups": groups})

def parse_time_slots(availability_str):
    time_slots = []
    for match in re.finditer(r'(\d{2}:\d{2})-(\d{2}:\d{2})', availability_str):
        start, end = match.groups()
        time_slots.append(f"{start}-{end}")
    return time_slots

def generate_invite_code(db: Session) -> str:
    """
    Generate a unique invite code for a new group.
    
    Args:
        db (Session): The database session to check for existing invite codes.
        
    Returns:
        str: A unique invite code.
    """
    while True:
        # Generate a random 6-character alphanumeric string
        invite_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        # Check if the generated invite code already exists
        existing_group = db.query(Group).filter(Group.invite_code == invite_code).first()
        if not existing_group:
            return invite_code
