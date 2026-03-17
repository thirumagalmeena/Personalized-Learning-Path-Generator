from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))
    difficulty = Column(String(50))
    estimated_learning_hours = Column(Integer)
    description = Column(String)

class LearningGoal(Base):
    __tablename__ = "learning_goals"

    goal_id = Column(Integer, primary_key=True, index=True)
    goal_name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))
    description = Column(String)
    target_skills = Column(String)  # comma separated for now
    estimated_total_hours = Column(Integer)

class SkillDependency(Base):
    __tablename__ = "skill_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    prerequisite_skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    dependency_strength = Column(Float)

class LearningResource(Base):
    __tablename__ = "learning_resources"

    resource_id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))

    resource_type = Column(String(50))
    resource_title = Column(String(255))
    difficulty = Column(String(50))
    estimated_time = Column(Integer)
    url = Column(String)

class SkillSimilarity(Base):
    __tablename__ = "skill_similarities"

    id = Column(Integer, primary_key=True, index=True)
    skill_1 = Column(String(255))
    skill_2 = Column(String(255))
    similarity_score = Column(Float)