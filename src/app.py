"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr


class StudentProfile(BaseModel):
    email: EmailStr
    name: str
    grade_level: str
    contact_number: Optional[str] = None
    enrolled_at: Optional[str] = None


class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    grade_level: Optional[str] = None
    contact_number: Optional[str] = None
    enrolled_at: Optional[str] = None


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory student profiles
students: Dict[str, StudentProfile] = {
    "michael@mergington.edu": StudentProfile(
        email="michael@mergington.edu",
        name="Michael Johnson",
        grade_level="10",
        contact_number="555-0101",
        enrolled_at="2024-09-01"
    ),
    "emma@mergington.edu": StudentProfile(
        email="emma@mergington.edu",
        name="Emma Williams",
        grade_level="11",
        contact_number="555-0202",
        enrolled_at="2023-09-01"
    ),
    "liam@mergington.edu": StudentProfile(
        email="liam@mergington.edu",
        name="Liam Brown",
        grade_level="12",
        contact_number="555-0303",
        enrolled_at="2022-09-01"
    ),
    "ava@mergington.edu": StudentProfile(
        email="ava@mergington.edu",
        name="Ava Miller",
        grade_level="11",
        contact_number="555-0404",
        enrolled_at="2024-09-01"
    )
}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/students")
def get_students():
    return list(students.values())


@app.get("/students/{email}")
def get_student(email: str):
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[email]


@app.post("/students")
def create_student(profile: StudentProfile):
    if profile.email in students:
        raise HTTPException(status_code=400, detail="Student profile already exists")
    students[profile.email] = profile
    return profile


@app.put("/students/{email}")
def update_student(email: str, profile_update: StudentProfileUpdate):
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    current_profile = students[email]
    updated_profile = current_profile.copy(update=profile_update.dict(exclude_unset=True))
    students[email] = updated_profile
    return updated_profile


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Ensure the student profile exists before signup
    if email not in students:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
