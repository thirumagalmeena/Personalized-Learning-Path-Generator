from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Optional

from backend import models
from backend import schemas
from backend import auth
from backend.database import Base,engine, get_db

from backend.services.learning_path import generate_learning_path

# Auto-create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Learning Path Generator API",
    description="Authentication API for the Learning Path Generator app.",
    version="1.0.0",
)

# Allow requests from the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Learning Path Generator API is running."}


@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Email must be unique.
    - Password is hashed with bcrypt before storing.
    """
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed_pw = auth.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    return new_user


@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Log in with email and password.
    Returns a JWT access token on success.
    """
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.create_access_token(data={"sub": user.email, "user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }

# get all skills
@app.get("/skills", response_model=List[schemas.SkillOut], tags=["Skills"])
def get_skills(db: Session = Depends(get_db)):
    skills = db.query(models.Skill).all()
    return skills

# get all goals
@app.get("/goals", response_model=List[schemas.GoalOut], tags=["Goals"])
def get_goals(db: Session = Depends(get_db)):
    goals = db.query(models.LearningGoal).all()
    return goals


# get distinct categories from skills table
@app.get("/categories", response_model=List[str], tags=["Skills"])
def get_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Skill.category)
        .distinct()
        .order_by(models.Skill.category)
        .all()
    )
    return [r[0] for r in rows if r[0]]


# get skills filtered by category and/or difficulty
@app.get("/skills/filter", response_model=List[schemas.SkillDropdown], tags=["Skills"])
def filter_skills(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Skill)
    if category:
        query = query.filter(models.Skill.category == category)
    if difficulty:
        query = query.filter(models.Skill.difficulty == difficulty)
    return query.order_by(models.Skill.skill_name).all()

# generate learning path endpoints
"""
@app.post("/generate-learning-path", tags=["Learning Path"])
def generate_path(data: schemas.LearningPathRequest, db: Session = Depends(get_db)):
    try:
        ordered_skills = generate_learning_path(
            user_skills=data.current_skills,
            goal_name=data.goal,
            db=db
        )

        return {
            "goal": data.goal,
            "learning_path": ordered_skills,
            "count": len(ordered_skills)
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating learning path: {str(e)}"
        )
"""
@app.post("/generate-learning-path", tags=["Learning Path"])
def generate_path(data: schemas.LearningPathRequest, db: Session = Depends(get_db)):
    """
    Generate a personalized learning path with resources based on user's current skills and target goal.
    Uses prerequisite-aware topological sorting to order skills correctly.
    """
    try:
        steps = generate_learning_path(
            user_skills=data.current_skills,
            goal_name=data.goal,
            db=db
        )
        
        return {
            "goal": data.goal,
            "total_steps": len(steps),
            "learning_path": steps
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating learning path: {str(e)}"
        )
