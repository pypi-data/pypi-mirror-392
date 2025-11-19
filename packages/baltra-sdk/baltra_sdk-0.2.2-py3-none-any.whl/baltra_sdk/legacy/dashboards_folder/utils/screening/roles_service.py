from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import Roles, db, QuestionSets
from typing import List, Dict
from datetime import date
from .questions_service import QuestionsService
from typing import Optional

logger = logging.getLogger(__name__)

class RolesService:
    """Manager of area performance metrics with integrated error handling"""
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
            
        self.company_id = company_id
        
        
    def role_to_dict(self, role: Roles) -> dict:
        print(role.role_info)
        return {
            "name": role.role_name,
            "company_id": role.company_id,
            "active": role.active,
            "id": role.role_id,
            "set_id": role.set_id,
            "info": self.parse_role_info(role.role_info),
            "eligibility_criteria": role.eligibility_criteria,
        }

    def get_all_roles(self) -> list:
        """Retrieves company data from the database"""
        
        try:
            roles = Roles.query.filter_by(
                company_id=self.company_id,
                is_deleted=False
            ).order_by(Roles.role_name).all()
            
            for  role in roles:
                if role.set_id is None:
                    role.set_id = self.create_set(role.role_name)
                    
            db.session.commit()
            
            return [self.role_to_dict(role) for role in roles] if roles else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching roles: {str(e)}")
            raise RuntimeError("Error retrieving roles from database")
    
    def change_role(self, role_id: int, new_name: Optional[str] = None, criteria: Optional[dict] = None, active: Optional[bool] = None) -> bool:
        try:
            questions_service = QuestionsService(self.company_id)

            role = Roles.query.filter_by(role_id=role_id, company_id=self.company_id).first()
            if not role:
                raise ValueError("Role not found")
            
            if new_name:
                """Changes the name of a role"""
                if not new_name or not isinstance(new_name, str):
                    raise ValueError("Invalid role name")  
                role.role_name = new_name
                
            if criteria is not None:
              if not isinstance(criteria, dict):
                raise ValueError("Invalid eligibility criteria")
              role.eligibility_criteria = criteria
                  
            if active is not None:
                """Changes the active status of a role"""
                if not isinstance(active, bool):
                    raise ValueError("Active status must be a boolean value")
                role.active = active
                
            db.session.commit()
            return True
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when changing role: {str(e)}")
            raise RuntimeError("Error updating role in database")
        except ValueError as ve:
            logger.error(str(ve))
            raise ve
          
    
    def clone_role(self, role_id: int) -> int:
        """Clones a role and returns the new role ID"""
        role = Roles.query.filter_by(role_id=role_id, company_id=self.company_id).first()
        if not role:
                raise ValueError("Role not found")
              
              
        questions_service = QuestionsService(self.company_id)
        
        new_set_id = questions_service.clone_set_and_questions(role.set_id)
        
        if not new_set_id:
            raise RuntimeError("Failed to clone question set")

        new_role_name = role.role_name + " (Copia)"
        
        new_role = Roles(
                company_id=self.company_id,
                role_name=new_role_name,
                set_id=new_set_id,
                role_info=role.role_info.copy() if role.role_info else None,
        )
            
        db.session.add(new_role)
        db.session.commit()
        return self.role_to_dict(new_role)
          
    
    def create_set(self, role_name) -> int:
        """Creates a new question set for the company"""
        questions_service = QuestionsService(self.company_id)
        try:
            new_set = questions_service.create_set(role_name=role_name, company_id=self.company_id)
            
            set_id = new_set.get("id")
            
            questions_service.add_question(set_id, {
                "question": "Cuéntanos un poco sobre tu **experiencia relacionada con esta vacante**: ¿Cuántos años has trabajado, en qué roles y haciendo qué actividades?\n\nPor favor, sé lo más detallado posible por texto o **nota de voz**.",
                "type": "text",
                "end_interview_answer":  None,
                "example_answer":  "No tengo experiencia previa; Trabajé en Mcdonald's por 3 años como cajero y en la empresa Brinco por dos años como ayudante",
                "position": 1,
                "metadata": None
            })   
                     
            questions_service.add_question(set_id, {
                "question": "ask_location",
                "type": "location",
                "end_interview_answer":  None,
                "example_answer":  "Av Patito 123, Miguel Hidalgo, Ciudad de México; colonia juarez; Latitud 20, Longitud 20",
                "position": 2,
                "metadata": None
            })

            questions_service.add_question(set_id, {
                "question": "Me puedes dar el numero de referencia de un jefe o supervisor con el que hayas trabajado?",
                "type": "phone_reference",
                "end_interview_answer": None,
                "example_answer": "5543235678; no; no quiero dar una referencia; no tengo referencia;",
                "position": 3,
                "metadata": None
            })
            
            questions_service.add_question(set_id, {
                "question": "appointment_booking",
                "type": "interactive",
                "end_interview_answer": None,
                "example_answer":  '{"fecha":"2025-07-24","hora":"10:00","flow_token":"{"flow_type": "appointment_booking", "expiration_date": "2025-07-25T00:28:08.243936"}"}',
                "position": 4,
                "metadata": None
            })
            
            return set_id
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when creating set: {str(e)}")
            raise RuntimeError("Error creating question set in database")
    
    def add_role(self, role_name: str) -> int:
        """Agrega un nuevo rol a la compañía"""
        
        try:

            role = Roles(
                company_id=self.company_id,
                role_name=role_name,
                set_id=self.create_set(role_name),
            )
            
            db.session.add(role)
            db.session.commit()
            return role.role_id
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when adding role: {str(e)}")            
            raise RuntimeError("Error adding role to database")
          
    
    def delete_role(self, role_id: int) -> bool:
        """Elimina un rol de la compañía"""
        
        try:
            role = Roles.query.filter_by(
                role_id=role_id,
                company_id=self.company_id
            ).first()
            
            if not role:
                raise ValueError("Role not found")
                
            role.active = False  # Mark as inactive instead of deleting
            role.is_deleted = True
            db.session.commit()
            return True
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when deleting role: {str(e)}")
            raise RuntimeError("Error deleting role from database")
        except ValueError as ve:
            logger.error(str(ve))
            raise ve
    
    @staticmethod
    def parse_role_info(info_json: dict) -> List[Dict[str, str]]:
        """
        Transforma un JSON de role_info en una lista de objetos {question, answer}.
        """
        if not isinstance(info_json, dict):
            return []

        faqs = []
        q_keys = sorted([k for k in info_json if k.startswith("Q")], key=lambda x: int(x[1:]))
        for q_key in q_keys:
            index = q_key[1:]
            a_key = f"A{index}"
            question = info_json.get(q_key)
            answer = info_json.get(a_key)
            if question is not None and answer is not None:
                faqs.append({
                    "question": question,
                    "answer": answer,
                    "index": index
                })
        return faqs

    def add_faq(self, role_id: int, question: str, answer: str):
        """Agrega una nueva pregunta y respuesta al role_info"""
        role = Roles.query.filter_by(role_id=role_id, company_id=self.company_id).first()
        if not role:
            raise ValueError("Role not found")

        info = role.role_info or {}
        count = len([k for k in info if k.startswith("Q")]) + 1

        info[f"Q{count}"] = question
        info[f"A{count}"] = answer

        role.role_info = info
        db.session.commit()

    def edit_faq(self, role_id: int, index: int, question: str, answer: str):
        """Edita una pregunta y respuesta específica"""
        role = Roles.query.filter_by(role_id=role_id, company_id=self.company_id).first()
        if not role:
            raise ValueError("Role not found")

        info = role.role_info or {}

        q_key = f"Q{index}"
        a_key = f"A{index}"

        if q_key in info and a_key in info:
            info[q_key] = question
            info[a_key] = answer
            role.role_info = info
            db.session.commit()
        else:
            raise KeyError("FAQ index not found")

    def delete_faq(self, role_id: int, index: int):
        """Elimina una pregunta/respuesta y reordena los índices"""
        role = Roles.query.filter_by(role_id=role_id, company_id=self.company_id).first()
        if not role:
            raise ValueError("Role not found")

        info = role.role_info or {}
        q_key = f"Q{index}"
        a_key = f"A{index}"

        if q_key not in info or a_key not in info:
            raise KeyError("FAQ index not found")

        # Eliminar la pregunta y respuesta
        del info[q_key]
        del info[a_key]

        # Reorganizar los índices
        faqs = self.parse_role_info(info)
        reordered = {}
        for i, faq in enumerate(faqs, 1):
            reordered[f"Q{i}"] = faq["question"]
            reordered[f"A{i}"] = faq["answer"]

        role.role_info = reordered
        db.session.commit()

    def overwrite_faqs(self, role_id: int, faqs: List[Dict[str, str]]) -> None:
        """
        Reemplaza completamente las FAQs actuales de un rol.
        """
        role = Roles.query.filter_by(company_id=self.company_id, role_id=role_id).first()
        if not role:
            raise ValueError("Role not found")

        # Construir nuevo role_info con Q1/A1, Q2/A2...
        new_info = {}
        for i, faq in enumerate(faqs, start=1):
            new_info[f"Q{i}"] = faq["question"]
            new_info[f"A{i}"] = faq["answer"]

        role.role_info = new_info
        db.session.commit()
