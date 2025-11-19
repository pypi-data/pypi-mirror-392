from openai import OpenAI
from .assistant_configs import BASE_CONFIG, ROLE_INSTRUCTIONS, COMPANY_PARAMETERS, AssistantType
from flask import current_app
import logging
from datetime import datetime
from baltra_sdk.legacy.dashboards_folder.models import Companies, db


"""
This module defines the AssistantManager class for managing the creation and updating of OpenAI-powered assistants for different companies. 
It integrates with OpenAI's API to handle the construction of assistant instructions, incorporating company-specific configurations such as language, 
tone, and formality. The module also facilitates updating the company's record with the newly created assistant's ID. 
The configurations for the assistants and their functionality are imported from the assistant_configs module.
"""


class AssistantManager:
    """
    The AssistantManager class is responsible for managing the lifecycle of OpenAI assistants within the application. 
    It handles the creation of assistants with company-specific parameters, such as language preferences and formal tone, 
    and it updates the company records in the database with the appropriate assistant ID. T
    he class supports both the creation of new assistants and the updating of existing ones.
    """

    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI(api_key=current_app.config["OPENAI_KEY"])
    
    def _build_instructions(self, company_id: int, assistant_type: AssistantType) -> str:
        """Builds complete instructions by combining parameters and company specific configs"""
        company_params = COMPANY_PARAMETERS.get(str(company_id), COMPANY_PARAMETERS["default"])
        
        # Combine role + all_instructions
        instructions = f"""
            {ROLE_INSTRUCTIONS[assistant_type.value]}

            {company_params["all_instructions"]}

            Language: {company_params['language']}
            Tone: {company_params['tone']}
            Formality: {company_params['formality_level']}
            """.strip()
        
        return instructions
    
    def create_or_update_assistant(self, company_id: int, assistant_type: AssistantType) -> str:
        try:
            company = Companies.query.get(company_id)
            if not company:
                raise ValueError(f"Company {company_id} not found")

            # Retrieve the correct vector ID based on assistant type
            vector_store_id = company.employee_vector_id if assistant_type == AssistantType.EMPLOYEE else company.owner_vector_id

            # Build assistant instructions
            instructions = self._build_instructions(company_id, assistant_type)

            # Construct assistant creation parameters
            create_params = {
                "name": f"{assistant_type.value.title()} Assistant - Company {company_id}",
                "instructions": instructions,
                "model": BASE_CONFIG["model"],
                "temperature": 0.3,  # Set temperature to 0.3 for more consistent responses
            }

            # Include tool_resources only if vector_store_id is present
            if vector_store_id:
                create_params["tools"]= [{"type": "file_search"}]
                create_params["tool_resources"] = {"file_search": {"vector_store_ids": [vector_store_id]}}

            # Create new assistant using OpenAI standard format
            assistant = self.client.beta.assistants.create(**create_params)

            # Update company record with new assistant ID
            self._update_company_assistant_id(company_id, assistant.id, assistant_type)

            logging.info(f"Created new assistant for company {company_id}, type: {assistant_type.value}")
            return assistant.id

        except Exception as e:
            logging.error(f"Error creating assistant: {e}")
            raise

    
    def modify_assistant(self, company_id: int, assistant_type: AssistantType) -> str:
        logging.info(f'Assistant Type: {assistant_type}')
        try:
            company = Companies.query.get(company_id)
            if not company:
                raise ValueError(f"Company {company_id} not found")
            
            # Retrieve the correct assistant ID and vector ID based on assistant type
            if assistant_type == AssistantType.EMPLOYEE:
                assistant_id = company.employee_assistant_id
                vector_store_id = company.employee_vector_id
            else:
                assistant_id = company.owner_assistant_id
                vector_store_id = company.owner_vector_id

            if not assistant_id:
                raise ValueError(f"No assistant found for company {company_id}, type {assistant_type.value}")

            # Build new instructions
            instructions = self._build_instructions(company_id, assistant_type)

            # Construct the update parameters
            update_params = {
                "assistant_id": assistant_id,
                "name": f"{assistant_type.value.title()} Assistant - Company {company_id}",
                "instructions": instructions,
                "model": BASE_CONFIG["model"],
                "temperature": 0.3,
            }

            # Include tool_resources only if vector_store_id is present
            if vector_store_id:
                update_params["tools"]= [{"type": "file_search"}]
                update_params["tool_resources"] = {"file_search": {"vector_store_ids": [vector_store_id]}}

            # Update the assistant
            assistant = self.client.beta.assistants.update(**update_params)

            logging.info(f"Modified assistant for company {company_id}, type: {assistant_type.value}")
            return assistant.id

        except Exception as e:
            logging.error(f"Error modifying assistant: {e}")
            raise

    def _update_company_assistant_id(self, company_id: int, assistant_id: str, assistant_type: AssistantType):
        """Updates the company record with the new assistant ID"""
        
        try:
            company = Companies.query.get(company_id)
            if not company:
                raise ValueError(f"Company {company_id} not found")
            
            if assistant_type == AssistantType.EMPLOYEE:
                company.employee_assistant_id = assistant_id
            else:
                company.owner_assistant_id = assistant_id
                
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating company assistant ID: {e}")
            raise