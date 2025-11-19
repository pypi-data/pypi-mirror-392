from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import MessageTemplates, db
from typing import List, Dict
from datetime import date
from baltra_sdk.shared.utils.screening.google_maps import LocationService

logger = logging.getLogger(__name__)

class MessageTemplatesService:
    """Manager of area performance metrics with integrated error handling"""
    
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
            
        self.company_id = company_id
        
        
    def message_to_dict(self, message: MessageTemplates) -> dict:
        return {
            "id": message.id,
            "keyword": message.keyword,
            "button_trigger": message.button_trigger,
            "type": message.type,
            "text": message.text,
            "interactive_type": message.interactive_type,
            "button_keys": message.button_keys,
            "footer_text": message.footer_text,
            "header_type": message.header_type,
            "header_content": message.header_content,
            "parameters": message.parameters,
            "template": message.template,
            "variables": message.variables,
            "url_keys": message.url_keys,
            "header_base": message.header_base,
            "flow_keys": message.flow_keys,
            "flow_action_data": message.flow_action_data,
            "document_link": message.document_link,
            "filename": message.filename,
            "flow_name": message.flow_name,
            "flow_cta": message.flow_cta,
            "list_options": message.list_options,
            "list_section_title": message.list_section_title,  
            "display_name": message.display_name
        }
        
        
    def get_all_messages(self) -> list:
        """Retrieves messages templates from the database"""
        
        companies = [self.company_id, 9999]
        
        try:
            messages = MessageTemplates.query.filter(MessageTemplates.company_id.in_(companies)).all()
            
            return [self.message_to_dict(message) for message in messages] if messages else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching messages: {str(e)}")
            raise RuntimeError("Error retrieving messages from database")