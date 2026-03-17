import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# -----------------------------
# USER AUTHENTICATION
# -----------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", v):
            raise ValueError(
                "Password must contain at least one special character (!@#$%^&* etc.)."
            )
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# -----------------------------
# SKILLS
# -----------------------------

class SkillBase(BaseModel):
    skill_name: str
    category: str
    difficulty: str
    estimated_learning_hours: int
    description: Optional[str] = None


class SkillOut(SkillBase):
    skill_id: int

    model_config = {"from_attributes": True}


# -----------------------------
# LEARNING GOALS
# -----------------------------

class LearningGoalBase(BaseModel):
    goal_name: str
    category: str
    description: Optional[str] = None
    target_skills: str
    estimated_total_hours: int


class LearningGoalOut(LearningGoalBase):
    goal_id: int

    model_config = {"from_attributes": True}


# -----------------------------
# SKILL DEPENDENCIES
# -----------------------------

class SkillDependencyBase(BaseModel):
    skill_id: int
    prerequisite_skill_id: int
    dependency_strength: float


class SkillDependencyOut(SkillDependencyBase):
    id: int

    model_config = {"from_attributes": True}


# -----------------------------
# LEARNING RESOURCES
# -----------------------------

class LearningResourceBase(BaseModel):
    skill_id: int
    resource_type: str
    resource_title: str
    difficulty: str
    estimated_time: int
    url: str


class LearningResourceOut(LearningResourceBase):
    resource_id: int

    model_config = {"from_attributes": True}


# -----------------------------
# SKILL SIMILARITY
# -----------------------------

class SkillSimilarityBase(BaseModel):
    skill_1: str
    skill_2: str
    similarity_score: float


class SkillSimilarityOut(SkillSimilarityBase):
    id: int

    model_config = {"from_attributes": True}


# -----------------------------
# LEARNING PATH
# -----------------------------

class LearningPathRequest(BaseModel):
    """Request from frontend to generate a learning path"""
    current_skills: List[str]  # User's existing skill names
    goal: str                   # Goal name (matches your models.py where goal_name is used)
    learning_pace: str
    preferences: List[str]


class LearningStep(BaseModel):
    """A single step in the learning path"""
    step_number: int
    skill_name: str              # Matches skill_name in Skill model
    resource_title: str          # Matches resource_title in LearningResource
    resource_type: str           # Matches resource_type in LearningResource
    url: str                     # Matches url in LearningResource


class LearningPathResponse(BaseModel):
    """Complete learning path response"""
    goal: str                    # Goal name for display
    steps: List[LearningStep]


# -----------------------------
# DROPDOWN MODELS
# -----------------------------

class SkillDropdown(BaseModel):
    """Simplified skill for dropdown menus"""
    skill_id: int
    skill_name: str
    category: str
    difficulty: str

    model_config = {"from_attributes": True}


class GoalOut(BaseModel):
    """Simplified goal for dropdown menus"""
    goal_id: int
    goal_name: str
    category: str
    description: str

    model_config = {"from_attributes": True}