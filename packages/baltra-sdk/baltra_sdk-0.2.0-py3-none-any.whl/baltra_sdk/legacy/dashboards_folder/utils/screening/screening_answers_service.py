from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import ScreeningAnswers, db, QuestionSets
from typing import List, Dict
from datetime import date
from .questions_service import QuestionsService

logger = logging.getLogger(__name__)

class QuestionsAnswersService:
    """Manager of area performance metrics with integrated error handling"""
    
    def __init__(self, candidate_id: int):
        if not isinstance(candidate_id, int) or candidate_id <= 0:
            raise ValueError("Invalid candidate ID")
            
        self.candidate_id = candidate_id
        
        
    def answer_to_dict(self, question: ScreeningAnswers) -> dict:
        return {
            "id": question.answer_id,
            "Candidate_id": question.candidate_id,
            "question_id": question.question_id,
            "answer_raw": question.answer_raw,
            "answer_json" : question.answer_json,
            "created_at": question.created_at
        }
        

    def get_all_questions(self) -> list:
        """Retrieves company data from the database"""
        
        try:
            questions = ScreeningAnswers.query.filter_by(
                candidate_id=self.candidate_id
            ).all()
            
            return [self.answer_to_dict(question) for question in questions] if questions else []
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching questions: {str(e)}")
            raise RuntimeError("Error retrieving questions from database")

    def transformer_questions(self, answers: list[dict]) -> list[dict]:
        """Transforms a list of answers into a list of questions"""
        questionService = QuestionsService(2)
        questions = []
        for answer in answers:
            question = questionService.get_question(answer.get("question_id"))
            if question:
                questions.append({
                    "question": question.get("question"),
                    "answer_raw": answer.get("answer_raw"),
                    "answer_json" : answer.get("answer_json"),
                    "candidate_id": answer.get("candidate_id"),
                    "answer_id": answer.get("id"),
                    "created_at": answer.get("created_at"),
                    "question_id": answer.get("question_id")
                })
        return questions
    
    
                