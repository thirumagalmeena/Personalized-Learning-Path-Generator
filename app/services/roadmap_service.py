from app.services.gap_analysis import gap_analysis_service
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.auth_service import auth_service
from app.utils.config import settings
from app.utils.csv_handler import csv_handler
import os
import json

class RoadmapService:
    def generate_personalized_roadmap(self, user_id: str):
        # 1. Load user profile
        user_profile = auth_service.get_user_by_id(user_id)
        if not user_profile:
            raise ValueError("User not found")
            
        # 1.5 Check Cache
        goal_id = str(user_profile.get("goal_id", "default"))
        cache_file = os.path.join(settings.APP_DATA_DIR, f"{user_id}_{goal_id}_roadmap.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
            
        # 2. Identify missing skills
        missing_skills = gap_analysis_service.identify_missing_skills(user_id)
        
        # 2.5 Identify possessed skills for LLM acknowledgement
        user_skills_df = csv_handler.read_csv("user_skills.csv")
        possessed_skill_ids = []
        if not user_skills_df.empty:
            possessed_skill_ids = user_skills_df[user_skills_df['user_id'] == str(user_id)]['skill_id'].tolist()
            
        skills_df = csv_handler.read_csv("skills.csv")
        possessed_skills = []
        if not skills_df.empty:
            for sid in possessed_skill_ids:
                matches = skills_df[skills_df['skill_id'].astype(str) == str(sid)]
                if not matches.empty:
                    possessed_skills.append(matches.iloc[0]['skill_name'])
        
        # 3. Retrieve RAG context
        rag_context = rag_service.retrieve_context(missing_skills)
        
        # 4. Construct Context for LLM
        context = {
            "experience_level": user_profile.get("experience_level"),
            "available_hours_per_week": user_profile.get("available_hours_per_week"),
            "learning_style": user_profile.get("learning_style"),
            "missing_skills": missing_skills,
            "possessed_skills": possessed_skills,
            "resources": rag_context.get("resources", []),
            "projects": rag_context.get("projects", [])
        }
        
        # 5. Generate Roadmap via LLM
        roadmap_dict = llm_service.generate_roadmap(context)
        
        # 6. Save to Cache
        if roadmap_dict and roadmap_dict.get("phases"):
            try:
                with open(cache_file, "w") as f:
                    json.dump(roadmap_dict, f)
            except Exception:
                pass
        
        return roadmap_dict

roadmap_service = RoadmapService()
