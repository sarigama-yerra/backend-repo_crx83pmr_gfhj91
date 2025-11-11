import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

from database import create_document, get_documents
from schemas import Student, Staff, Room, Allocation, Attendance, Visitor, Complaint

app = FastAPI(title="Hostel Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hostel Management System API running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    from database import db
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
                response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utility: simple rule-based sentiment and categorization
NEG_WORDS = {"bad", "terrible", "worst", "awful", "dirty", "late", "rude", "leak", "broken", "noisy", "slow"}
POS_WORDS = {"good", "great", "excellent", "helpful", "clean", "quick"}
CATEGORY_KEYWORDS = {
    "maintenance": ["leak", "broken", "repair", "power", "electric", "plumbing", "fan", "ac", "heater"],
    "food": ["mess", "food", "canteen", "meal", "breakfast", "dinner", "lunch"],
    "security": ["security", "guard", "gate", "theft", "steal"],
    "cleanliness": ["dirty", "clean", "trash", "garbage"],
    "discipline": ["noise", "noisy", "disturb", "fight"],
}

def analyze_text(text: str) -> Dict[str, Any]:
    t = text.lower()
    score = 0
    for w in NEG_WORDS:
        if w in t:
            score -= 1
    for w in POS_WORDS:
        if w in t:
            score += 1
    sentiment = "neutral"
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    # category
    best_cat = None
    best_hits = 0
    for cat, keys in CATEGORY_KEYWORDS.items():
        hits = sum(1 for k in keys if k in t)
        if hits > best_hits:
            best_cat = cat
            best_hits = hits
    # severity heuristic
    severity = "low"
    if sentiment == "negative":
        severity = "medium" if best_hits <= 1 else "high"
    return {"sentiment": sentiment, "category": best_cat, "severity": severity}

# Generic list responses
class ListResponse(BaseModel):
    items: List[Dict[str, Any]]

# Students
@app.post("/api/students", response_model=Dict[str, str])
def create_student(student: Student):
    _id = create_document("student", student)
    return {"id": _id}

@app.get("/api/students", response_model=ListResponse)
def list_students():
    docs = get_documents("student")
    return {"items": docs}

# Staff
@app.post("/api/staff", response_model=Dict[str, str])
def create_staff(staff: Staff):
    _id = create_document("staff", staff)
    return {"id": _id}

@app.get("/api/staff", response_model=ListResponse)
def list_staff():
    docs = get_documents("staff")
    return {"items": docs}

# Rooms
@app.post("/api/rooms", response_model=Dict[str, str])
def create_room(room: Room):
    _id = create_document("room", room)
    return {"id": _id}

@app.get("/api/rooms", response_model=ListResponse)
def list_rooms():
    docs = get_documents("room")
    return {"items": docs}

# Allocations
@app.post("/api/allocations", response_model=Dict[str, str])
def create_allocation(allocation: Allocation):
    _id = create_document("allocation", allocation)
    return {"id": _id}

@app.get("/api/allocations", response_model=ListResponse)
def list_allocations():
    docs = get_documents("allocation")
    return {"items": docs}

# Attendance
@app.post("/api/attendance", response_model=Dict[str, str])
def create_attendance(att: Attendance):
    _id = create_document("attendance", att)
    return {"id": _id}

@app.get("/api/attendance", response_model=ListResponse)
def list_attendance():
    docs = get_documents("attendance")
    return {"items": docs}

# Visitors
@app.post("/api/visitors", response_model=Dict[str, str])
def create_visitor(visitor: Visitor):
    _id = create_document("visitor", visitor)
    return {"id": _id}

@app.get("/api/visitors", response_model=ListResponse)
def list_visitors():
    docs = get_documents("visitor")
    return {"items": docs}

# Complaints
@app.post("/api/complaints", response_model=Dict[str, str])
def create_complaint(complaint: Complaint):
    # auto analyze
    analysis = analyze_text(f"{complaint.subject} {complaint.description}")
    comp_data = complaint.model_dump()
    for k, v in analysis.items():
        comp_data[k] = v
    _id = create_document("complaint", comp_data)
    return {"id": _id}

@app.get("/api/complaints", response_model=ListResponse)
def list_complaints():
    docs = get_documents("complaint")
    return {"items": docs}

@app.post("/api/complaints/analyze")
def analyze_complaint(payload: Dict[str, str]):
    text = (payload.get("subject") or "") + " " + (payload.get("description") or "")
    return analyze_text(text)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
