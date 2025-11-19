from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass(frozen=True, slots=True)
class CompanyGroup:
    group_id: Optional[int]
    name: str
    description: Optional[str]
    website: Optional[str]
    wa_id: Optional[str]
    phone: Optional[str]

@dataclass(frozen=True, slots=True)
class QuestionSet:
    set_id: Optional[int]
    company_id: Optional[int]
    set_name: str
    is_active: bool
    created_at: datetime
    general_set: bool
    group_id: Optional[int]

@dataclass(frozen=True, slots=True)
class ScreeningQuestion:
    question_id: Optional[int]
    set_id: int
    position: int
    question: str
    response_type: str
    question_metadata: Optional[Dict[str, Any]]
    end_interview_answer: Optional[str]
    example_answer: Optional[str]
    is_blocked: bool
    eligibility_question: bool
    is_active: bool

@dataclass(frozen=True, slots=True)
class MessageTemplate:
    id: Optional[int]
    keyword: str
    button_trigger: Optional[str]
    type: str
    text: Optional[str]
    interactive_type: Optional[str]
    button_keys: Optional[Dict[str, Any]]
    footer_text: Optional[str]
    header_type: Optional[str]
    header_content: Optional[str]
    parameters: Optional[Dict[str, Any]]
    template: Optional[str]
    variables: Optional[Dict[str, Any]]
    url_keys: Optional[Dict[str, Any]]
    header_base: Optional[str]
    flow_keys: Optional[Dict[str, Any]]
    flow_action_data: Optional[Dict[str, Any]]
    document_link: Optional[str]
    filename: Optional[str]
    flow_name: Optional[str]
    flow_cta: Optional[str]
    list_options: Optional[List[Dict[str, Any]]]
    list_section_title: Optional[str]
    display_name: Optional[str]
    company_id: Optional[int]
