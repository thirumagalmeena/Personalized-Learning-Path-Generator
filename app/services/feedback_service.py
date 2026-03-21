import uuid
from app.utils.csv_handler import csv_handler
from app.models.schemas import FeedbackRequest

class FeedbackService:
    def process_feedback(self, user_id: str, feedback: FeedbackRequest):
        feedback_id = str(uuid.uuid4())
        
        new_feedback = {
            "feedback_id": feedback_id,
            "user_id": user_id,
            "content_id": feedback.content_id,
            "content_type": feedback.content_type,
            "rating": feedback.rating,
            "comments": feedback.comments or ""
        }
        
        csv_handler.append_row("user_feedback.csv", new_feedback)
        
        return {"status": "success", "message": "Feedback recorded."}

feedback_service = FeedbackService()
