from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import ScreeningQuestions, db, QuestionSets
from typing import List, Dict
from datetime import date

logger = logging.getLogger(__name__)

class QuestionsService:
    """Manager of area performance metrics with integrated error handling"""
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
            
        self.company_id = company_id
        # self.set_id = set_id
        
    def Questions_to_dict(self, question: ScreeningQuestions) -> dict:
        return {
            "position": question.position,
            "metadata": question.question_metadata,
            "end_interview_answer": question.end_interview_answer,
            "example_answer": question.example_answer,
            "type": question.response_type,
            "question": question.question,
            "id": question.question_id,
            "set_id": question.set_id,
            "is_blocked": question.is_blocked,
            "is_active": question.is_active
        }
        
    def sets_to_dict(self, set: QuestionSets) -> dict:
        return {
            "name": set.set_name,
            "id": set.set_id,
            "company_id": set.company_id,
            "is_active": set.is_active,
            "general_set": set.general_set
        }
        
    def clone_set_and_questions(self, set_id: int) -> int:
        """Clones a set and returns the new set ID"""
        old_questions = ScreeningQuestions.query.filter_by(set_id=set_id, is_active=True).all()  # Only clone active questions
        if not old_questions:
            raise ValueError("No active questions found in set")
          
        old_set = QuestionSets.query.filter_by(set_id=set_id, company_id=self.company_id).first()
        if not old_set:
            raise ValueError("Set not found")
        
        new_set = QuestionSets(
            company_id=self.company_id,
            set_name=old_set.set_name,
            is_active=old_set.is_active,
        )
        
                
        db.session.add(new_set)
        db.session.commit()
        
        for question in old_questions:
            new_question = ScreeningQuestions(
                set_id=new_set.set_id,
                question=question.question,
                question_metadata=question.question_metadata,
                example_answer=question.example_answer,
                end_interview_answer=question.end_interview_answer,
                response_type=question.response_type,
                position=question.position,
                is_active=True,  # Clone as active
            )
            db.session.add(new_question)
            db.session.commit()
        

        return new_set.set_id
        
    def get_all_sets(self) -> list:
        """Retrieves company data from the database"""
        
        try:
            sets = QuestionSets.query.filter_by(
                company_id=self.company_id
            ).all()
            
            return [self.sets_to_dict(set) for set in sets] if sets else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching sets: {str(e)}")
            raise RuntimeError("Error retrieving sets from database") 
          
    def create_set(self, role_name='Default', company_id=0) -> dict:
        """Creates a new question set for the company, general set is False by default"""
        try:
            new_set = QuestionSets(
                company_id=self.company_id,
                set_name=f"{company_id}-{role_name}",
                is_active=True,
                general_set=False
            )
            db.session.add(new_set)
            db.session.commit()
            return self.sets_to_dict(new_set)

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when creating set: {str(e)}")
            raise RuntimeError("Error creating question set in database")

    def get_all_questions(self, set_id: int) -> list:
        """Retrieves active questions from the database"""
        
        try:
            questions = ScreeningQuestions.query.filter_by(
                set_id=set_id,
                is_active=True  # Only get active questions
            ).order_by(ScreeningQuestions.position).all()
            
            return [self.Questions_to_dict(question) for question in questions] if questions else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching questions: {str(e)}")
            raise RuntimeError("Error retrieving questions from database")
          
    def get_question(self, question_id: int) -> dict:
        """Retrieves an active question from the database"""
        try:
            question = ScreeningQuestions.query.filter_by(
                question_id=question_id,
                is_active=True  # Only get active questions
            ).first()
            
            return self.Questions_to_dict(question) if question else None
            
        except exc.SQLAlchemyError as e:  
            logger.error(f"Database error when fetching question: {str(e)}")
            raise RuntimeError("Error retrieving question from database")
          
    def add_question(self, set_id: int, question: dict) -> bool:
        """Adds a question to the database"""
        try:
            question_obj = ScreeningQuestions(
                set_id=set_id,
                question=question.get("question"),
                question_metadata=question.get("metadata"),
                example_answer=question.get("example_answer"),
                end_interview_answer=question.get("end_interview_answer"),
                response_type=question.get("type"),
                position=question.get("position"),
                is_active=True  # New questions are active by default
            )
            db.session.add(question_obj)
            db.session.commit()
            return self.Questions_to_dict(question_obj)
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error adding question: {str(e)}")
            return ValueError("Error adding question to database")
          
    def update_questions(self, set_id: int, questions: list[dict]) -> bool:
        """Updates active questions in the database"""
        try:
            
            for question in questions:
                q = ScreeningQuestions.query.filter_by(
                      question_id=question.get("id"),
                      is_active=True  # Only update active questions
                    ).first()
                    
                if not q:
                     raise ValueError(f"Question with ID {question.get('id')} not found or not active")
                    
                q.question = question.get("question")
                q.question_metadata = question.get("metadata")
                q.example_answer = question.get("example_answer") if question.get("example_answer") else None
                q.end_interview_answer = question.get("end_interview_answer") if question.get("end_interview_answer") else None
                q.response_type = question.get("type") if question.get("type") else None
                q.position = question.get("position")
                
                 
            db.session.commit()
            final_questions = ScreeningQuestions.query.filter_by(
                    set_id=set_id,
                    is_active=True  # Only return active questions
                ).all()
                
                
            return [self.Questions_to_dict(question) for question in final_questions] if final_questions else None

        except exc.SQLAlchemyError as e:
            logger.error(f"Error updating question: {str(e)}")
            return False  # Don't return ValueError here, just return False or raise the error

    def delete_question(self, set_id: int, question_id: int) -> bool:
        """Soft deletes a question by setting is_active to False"""
        try:
            q = ScreeningQuestions.query.filter_by(
                set_id=set_id,
                question_id=question_id,
                is_active=True  # Only find active questions
            ).first()
            
            if not q:
                raise ValueError(f"Question with ID {question_id} not found or already deleted")
            
            # Soft delete by setting is_active to False
            q.is_active = False
            db.session.commit()
            return True

        except exc.SQLAlchemyError as e:
            logger.error(f"Error soft deleting question: {str(e)}")
            return False
    
    def permanently_delete_question(self, set_id: int, question_id: int) -> bool:
        """Permanently deletes a question from the database (use with caution)"""
        try:
            q = ScreeningQuestions.query.filter_by(
                set_id=set_id,
                question_id=question_id
            ).first()
            
            if not q:
                raise ValueError(f"Question with ID {question_id} not found")
            
            db.session.delete(q)
            db.session.commit()
            return True

        except exc.SQLAlchemyError as e:
            logger.error(f"Error permanently deleting question: {str(e)}")
            return False
        
    def get_general_set(self) -> dict:
        """Retrieves the general set for the company"""
        try:
            general_set = QuestionSets.query.filter_by(
                company_id=self.company_id,
                general_set=True
            ).first()
            return self.sets_to_dict(general_set) if general_set else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Error retrieving general set: {str(e)}")
            return None
        
        
        
          