from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
import re

# Auth Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[0-9]", v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfileUpdate(BaseModel):
    goal_id: str
    experience_level: str = "beginner"
    available_hours_per_week: int = 10
    learning_style: str = "visual"

class Token(BaseModel):
    access_token: str
    token_type: str

# Skill Schemas
class ExtractSkillsRequest(BaseModel):
    free_text: str

class ExtractedSkill(BaseModel):
    skill_name: str
    matched_skill_id: Optional[str] = None
    confidence: float

class ExtractSkillsResponse(BaseModel):
    extracted_skills: List[ExtractedSkill]
    desired_skills: Optional[List[ExtractedSkill]] = []

# Roadmap Schemas
class ResourceSchema(BaseModel):
    title: str
    url: str
    type: str

class ProjectSchema(BaseModel):
    title: str
    description: str

class RoadmapPhase(BaseModel):
    title: str
    duration: str
    skills: List[str]
    resources: List[ResourceSchema]
    projects: List[ProjectSchema]
    completed: bool = False

class RoadmapResponse(BaseModel):
    phases: Optional[List[RoadmapPhase]] = []
    roadmap_text: Optional[str] = None
    is_complete: bool = False

# Feedback Schema
class FeedbackRequest(BaseModel):
    content_id: str
    content_type: str # resource, project, phase
    rating: int # 1-5
    comments: Optional[str] = None

class RoadmapFeedbackRequest(BaseModel):
    rating: int
    comments: Optional[str] = None
