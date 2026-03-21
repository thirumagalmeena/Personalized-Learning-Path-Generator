from fastapi import APIRouter, HTTPException, Depends
from app.routes.auth_routes import get_current_user
from app.models.schemas import RoadmapResponse, FeedbackRequest
from app.services.roadmap_service import roadmap_service
from app.services.feedback_service import feedback_service
import logging

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])
logger = logging.getLogger("learning_path_generator")

@router.post("/generate-roadmap", response_model=RoadmapResponse)
def generate_roadmap(current_user_id: str = Depends(get_current_user)):
    try:
        roadmap_dict = roadmap_service.generate_personalized_roadmap(current_user_id)
        if not roadmap_dict or not roadmap_dict.get("phases"):
            raise HTTPException(status_code=500, detail="Failed to generate roadmap content")
            
        # Pydantic will validate the dict directly into RoadmapResponse format because of the return type
        return roadmap_dict 
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest, current_user_id: str = Depends(get_current_user)):
    try:
        return feedback_service.process_feedback(current_user_id, request)
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
