"""
Dataset Loader Script
Loads all CSV data into the PostgreSQL database.
Run once: python scripts/load_dataset.py
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
# This ensures we can import from backend
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from backend.database import SessionLocal
from backend import models


def load_skills(db):
    """Load skills from skills.csv"""
    try:
        # Use absolute path for dataset files
        dataset_path = os.path.join(project_root, "dataset", "skills.csv")
        df = pd.read_csv(dataset_path)
        print(f"📖 Loading {len(df)} skills...")

        for _, row in df.iterrows():
            skill = models.Skill(
                skill_id=row["skill_id"],
                skill_name=row["skill_name"],
                category=row["category"],
                difficulty=row["difficulty"],
                estimated_learning_hours=row["estimated_learning_hours"],
                description=row["description"] if pd.notna(row["description"]) else None
            )
            db.add(skill)

        db.commit()
        print(f"✅ {len(df)} skills loaded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading skills: {e}")
        raise


def load_goals(db):
    """Load learning goals from goals.csv"""
    try:
        dataset_path = os.path.join(project_root, "dataset", "goals.csv")
        df = pd.read_csv(dataset_path)
        print(f"📖 Loading {len(df)} learning goals...")

        for _, row in df.iterrows():
            goal = models.LearningGoal(
                goal_id=row["goal_id"],
                goal_name=row["goal_name"],
                category=row["category"],
                description=row["description"] if pd.notna(row["description"]) else None,
                target_skills=row["target_skills"],
                estimated_total_hours=row["estimated_total_hours"]
            )
            db.add(goal)

        db.commit()
        print(f"✅ {len(df)} learning goals loaded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading goals: {e}")
        raise


def load_dependencies(db):
    """Load skill dependencies from skill_dependencies.csv"""
    try:
        dataset_path = os.path.join(project_root, "dataset", "skill_dependencies.csv")
        df = pd.read_csv(dataset_path)
        print(f"📖 Loading {len(df)} skill dependencies...")

        for _, row in df.iterrows():
            # Convert numpy types to Python native types
            dep = models.SkillDependency(
                skill_id=int(row["skill_id"]),  # Convert to Python int
                prerequisite_skill_id=int(row["prerequisite_skill_id"]),  # Convert to Python int
                dependency_strength=float(row["dependency_strength"])  # Convert to Python float
            )
            db.add(dep)

        db.commit()
        print(f"✅ {len(df)} skill dependencies loaded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading dependencies: {e}")
        raise


def load_resources(db):
    """Load learning resources from resources.csv"""
    try:
        dataset_path = os.path.join(project_root, "dataset", "resources.csv")
        
        # Read CSV and keep only the columns we need (drop unnamed columns)
        df = pd.read_csv(dataset_path)
        df = df[['resource_id', 'skill_id', 'resource_type', 'resource_title', 
                 'difficulty', 'estimated_time', 'url']]
        
        print(f"📖 Loading {len(df)} learning resources...")

        for _, row in df.iterrows():
            resource = models.LearningResource(
                resource_id=int(row["resource_id"]),
                skill_id=int(row["skill_id"]),
                resource_type=str(row["resource_type"]),
                resource_title=str(row["resource_title"]),
                difficulty=str(row["difficulty"]),
                estimated_time=int(row["estimated_time"]),
                url=str(row["url"])
            )
            db.add(resource)

        db.commit()
        print(f"✅ {len(df)} learning resources loaded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading resources: {e}")
        raise


def load_similarities(db):
    """Load skill similarities from skill_similarity.csv"""
    try:
        dataset_path = os.path.join(project_root, "dataset", "skill_similarity.csv")
        df = pd.read_csv(dataset_path)
        print(f"📖 Loading {len(df)} skill similarities...")

        for _, row in df.iterrows():
            sim = models.SkillSimilarity(
                skill_1=str(row["skill_1"]),
                skill_2=str(row["skill_2"]),
                similarity_score=float(row["similarity_score"])  # Convert to Python float
            )
            db.add(sim)

        db.commit()
        print(f"✅ {len(df)} skill similarities loaded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading similarities: {e}")
        raise


def clear_tables(db):
    """Clear all tables before loading (optional)"""
    try:
        print("🧹 Clearing existing data...")
        db.query(models.SkillSimilarity).delete()
        db.query(models.LearningResource).delete()
        db.query(models.SkillDependency).delete()
        db.query(models.LearningGoal).delete()
        db.query(models.Skill).delete()
        db.commit()
        print("✅ All tables cleared.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing tables: {e}")
        raise


def verify_counts(db):
    """Verify the counts after loading"""
    print("\n📊 Final Counts:")
    print(f"Skills: {db.query(models.Skill).count()} rows")
    print(f"Learning Goals: {db.query(models.LearningGoal).count()} rows")
    print(f"Skill Dependencies: {db.query(models.SkillDependency).count()} rows")
    print(f"Learning Resources: {db.query(models.LearningResource).count()} rows")
    print(f"Skill Similarities: {db.query(models.SkillSimilarity).count()} rows")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Dataset Loader")
    print("=" * 50)
    print(f"📁 Project Root: {project_root}")
    print(f"📁 Dataset Path: {os.path.join(project_root, 'dataset')}")
    print("=" * 50)

    # Create database session
    db = SessionLocal()

    try:
        # Optional: Clear existing data first
        # Uncomment the next line if you want to clear tables before loading
        clear_tables(db)
        
        # Load all data
        load_skills(db)
        load_goals(db)
        load_dependencies(db)
        load_resources(db)
        load_similarities(db)

        # Verify final counts
        verify_counts(db)

        print("\n" + "=" * 50)
        print("✅ Dataset successfully loaded into PostgreSQL!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Dataset loading failed: {e}")

    finally:
        db.close()
        print("🔒 Database connection closed.")