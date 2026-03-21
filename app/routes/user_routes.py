from fastapi import APIRouter, HTTPException, Depends
from app.routes.auth_routes import get_current_user
from app.models.schemas import ExtractSkillsRequest, ExtractSkillsResponse, UserProfileUpdate
from app.services.skill_extraction import skill_extraction_service
from app.services.auth_service import auth_service
import logging

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger("learning_path_generator")

@router.post("/extract-skills", response_model=ExtractSkillsResponse)
def extract_skills(request: ExtractSkillsRequest, current_user_id: str = Depends(get_current_user)):
    try:
        if not request.free_text or not request.free_text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        extracted_data = skill_extraction_service.extract_and_match(current_user_id, request.free_text)
        return ExtractSkillsResponse(
            extracted_skills=extracted_data["extracted_skills"],
            desired_skills=extracted_data["desired_skills"]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in extract-skills: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/profile")
def update_profile(profile: UserProfileUpdate, current_user_id: str = Depends(get_current_user)):
    try:
        return auth_service.update_user_profile(current_user_id, profile)
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/goals")
def get_goals(current_user_id: str = Depends(get_current_user)):
    try:
        return auth_service.get_all_goals()
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
