"""
Database Schemas for Hostel Management System

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Student -> "student").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import date

class Student(BaseModel):
    roll_no: str = Field(..., description="Unique roll number")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    department: Optional[str] = Field(None, description="Department/Program")
    year: Optional[int] = Field(None, ge=1, le=8, description="Year of study")

class Staff(BaseModel):
    staff_id: str = Field(..., description="Unique staff ID")
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Role/Designation")
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None)

class Room(BaseModel):
    number: str = Field(..., description="Room number")
    capacity: int = Field(..., ge=1, description="Total capacity")
    floor: Optional[int] = Field(None, ge=0)
    type: Optional[Literal["single", "double", "triple"]] = Field(None)

class Allocation(BaseModel):
    student_roll_no: str = Field(..., description="Roll number of student")
    room_number: str = Field(..., description="Allocated room number")
    start_date: date = Field(...)
    end_date: Optional[date] = Field(None)
    status: Literal["active", "completed", "cancelled"] = Field("active")

class Attendance(BaseModel):
    att_date: date = Field(..., description="Attendance date")
    student_roll_no: str = Field(...)
    status: Literal["present", "absent", "leave"] = Field("present")
    noted_by: Optional[str] = Field(None, description="Staff ID or name")

class Visitor(BaseModel):
    name: str = Field(...)
    visiting_student_roll_no: Optional[str] = Field(None)
    purpose: Optional[str] = Field(None)
    in_time: str = Field(..., description="ISO time or description")
    out_time: Optional[str] = Field(None)

class Complaint(BaseModel):
    raised_by_roll_no: Optional[str] = Field(None, description="Student roll number (if applicable)")
    raised_by_staff_id: Optional[str] = Field(None, description="Staff ID (if applicable)")
    subject: str = Field(...)
    description: str = Field(...)
    category: Optional[str] = Field(None, description="Auto or manual category")
    sentiment: Optional[str] = Field(None, description="Auto sentiment label")
    severity: Optional[Literal["low", "medium", "high"]] = Field(None)
