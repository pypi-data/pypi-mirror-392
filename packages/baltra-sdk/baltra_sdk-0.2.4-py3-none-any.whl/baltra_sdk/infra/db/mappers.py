from baltra_sdk.domain.models.company_group import CompanyGroup
from baltra_sdk.domain.models.company_screening import CompanyScreening
from baltra_sdk.domain.models.location import Location
from baltra_sdk.domain.models.role import Role
from baltra_sdk.domain.models.screening_flow import QuestionSet, ScreeningQuestion
from baltra_sdk.domain.models.screening_conversation import (
    ScreeningConversationStatus,
    ScreeningConversation,
    TempMessage,
    status_from_id,
)

from baltra_sdk.infra.db.models import (
    CompanyGroupModel,
    CompanyScreeningModel,
    LocationModel,
    RoleModel,
    QuestionSetModel,
    ScreeningQuestionModel,
    ScreeningConversationStatusModel,
    ScreeningConversationModel,
    TempMessageModel,
    WaMessageTypeModel,
    WaInteractiveTypeModel,
)
from datetime import datetime

from baltra_sdk.domain.models.screening_flow import MessageTemplate
from baltra_sdk.infra.db.models import MessageTemplateModel


def to_domain_company_group(m: CompanyGroupModel) -> CompanyGroup:
    return CompanyGroup(group_id=m.group_id, name=m.name, description=m.description, website=m.website, wa_id=m.wa_id, phone=m.phone)

def to_model_company_group(e: CompanyGroup) -> CompanyGroupModel:
    m = CompanyGroupModel()
    m.group_id = e.group_id
    m.name = e.name
    m.description = e.description
    m.website = e.website
    m.wa_id = e.wa_id
    m.phone = e.phone
    return m

def to_domain_company_screening(m: CompanyScreeningModel) -> CompanyScreening:
    return CompanyScreening(
        company_id=m.company_id,
        name=m.name,
        latitude=m.latitude,
        longitude=m.longitude,
        address=m.address,
        interview_excluded_dates=list(m.interview_excluded_dates or []),
        interview_days=list(m.interview_days or []),
        interview_hours=list(m.interview_hours or []),
        description=m.description,
        website=m.website,
        benefits=list(m.benefits or []),
        general_faq=m.general_faq,
        wa_id=m.wa_id,
        classifier_assistant_id=m.classifier_assistant_id,
        general_purpose_assistant_id=m.general_purpose_assistant_id,
        phone=m.phone,
        maps_link_json=m.maps_link_json,
        interview_address_json=m.interview_address_json,
        ad_trigger_phrase=m.ad_trigger_phrase,
        reminder_schedule=dict(m.reminder_schedule or {}),
        hr_contact=m.hr_contact,
        group_id=m.group_id,
        customer_id=m.customer_id,
        additional_info=m.additional_info,
    )

def to_model_company_screening(e: CompanyScreening) -> CompanyScreeningModel:
    m = CompanyScreeningModel()
    if e.company_id is not None:
        m.company_id = e.company_id
    m.name = e.name
    m.latitude = e.latitude
    m.longitude = e.longitude
    m.address = e.address
    m.interview_excluded_dates = list(e.interview_excluded_dates)
    m.interview_days = list(e.interview_days)
    m.interview_hours = list(e.interview_hours)
    m.description = e.description
    m.website = e.website
    m.benefits = [b for b in e.benefits if b and b != "__other__"]
    m.general_faq = e.general_faq
    m.wa_id = e.wa_id
    m.classifier_assistant_id = e.classifier_assistant_id or "asst_iBUlpF7FISkh3oY8Pr3bmVUb"
    m.general_purpose_assistant_id = e.general_purpose_assistant_id or "asst_drleBzh2ufZ79J7MHeocfp5X"
    m.phone = e.phone
    m.maps_link_json = e.maps_link_json
    m.interview_address_json = e.interview_address_json
    m.ad_trigger_phrase = e.ad_trigger_phrase
    m.reminder_schedule = dict(e.reminder_schedule)
    m.hr_contact = e.hr_contact
    m.group_id = e.group_id
    m.customer_id = e.customer_id
    m.additional_info = e.additional_info
    return m

def to_domain_location(m: LocationModel) -> Location:
    return Location(location_id=m.location_id, company_id=m.company_id, latitude=m.latitude, longitude=m.longitude, url=m.url, address=m.address)

def to_model_location(e: Location) -> LocationModel:
    m = LocationModel()
    if e.location_id is not None:
        m.location_id = e.location_id
    m.company_id = e.company_id
    m.latitude = e.latitude
    m.longitude = e.longitude
    m.url = e.url
    m.address = e.address
    return m

def to_domain_role(m: RoleModel) -> Role:
    return Role(
        role_id=m.role_id,
        company_id=m.company_id,
        role_name=m.role_name,
        role_info=m.role_info,
        active=m.active,
        set_id=m.set_id,
        eligibility_criteria=m.eligibility_criteria,
        default_role=m.default_role,
        is_deleted=m.is_deleted,
        shift=m.shift,
        location_id=m.location_id,
    )

def to_model_role(e: Role) -> RoleModel:
    m = RoleModel()
    if e.role_id is not None:
        m.role_id = e.role_id
    m.company_id = e.company_id
    m.role_name = e.role_name
    m.role_info = e.role_info
    m.active = e.active
    m.set_id = e.set_id
    m.eligibility_criteria = e.eligibility_criteria
    m.default_role = e.default_role
    m.is_deleted = e.is_deleted
    m.shift = e.shift
    m.location_id = e.location_id
    return m

def to_domain_question_set(m: QuestionSetModel) -> QuestionSet:
    return QuestionSet(
        set_id=m.set_id,
        company_id=m.company_id,
        set_name=m.set_name,
        is_active=m.is_active,
        created_at=m.created_at,
        general_set=m.general_set,
        group_id=m.group_id,
    )

def to_model_question_set(e: QuestionSet) -> QuestionSetModel:
    m = QuestionSetModel()
    if e.set_id is not None:
        m.set_id = e.set_id
    m.company_id = e.company_id
    m.set_name = e.set_name
    m.is_active = e.is_active
    m.created_at = e.created_at if isinstance(e.created_at, datetime) else datetime.utcnow()
    m.general_set = e.general_set
    m.group_id = e.group_id
    return m

def to_domain_screening_question(m: ScreeningQuestionModel) -> ScreeningQuestion:
    return ScreeningQuestion(
        question_id=m.question_id,
        set_id=m.set_id,
        position=m.position,
        question=m.question,
        response_type=m.response_type,
        question_metadata=dict(m.question_metadata or {}) if m.question_metadata is not None else None,
        end_interview_answer=m.end_interview_answer,
        example_answer=m.example_answer,
        is_blocked=m.is_blocked,
        eligibility_question=m.eligibility_question,
        is_active=m.is_active,
    )

def to_model_screening_question(e: ScreeningQuestion) -> ScreeningQuestionModel:
    m = ScreeningQuestionModel()
    if e.question_id is not None:
        m.question_id = e.question_id
    m.set_id = e.set_id
    m.position = e.position
    m.question = e.question
    m.response_type = e.response_type
    m.question_metadata = dict(e.question_metadata) if e.question_metadata is not None else None
    m.end_interview_answer = e.end_interview_answer
    m.example_answer = e.example_answer
    m.is_blocked = e.is_blocked
    m.eligibility_question = e.eligibility_question
    m.is_active = e.is_active
    return m


# NUEVAS FUNCIONES DE MAPEO

def to_domain_message_template(m: MessageTemplateModel) -> MessageTemplate:
    return MessageTemplate(
        id=m.id,
        keyword=m.keyword,
        button_trigger=m.button_trigger,
        type=m.type,
        text=m.text,
        interactive_type=m.interactive_type,
        button_keys=m.button_keys,
        footer_text=m.footer_text,
        header_type=m.header_type,
        header_content=m.header_content,
        parameters=m.parameters,
        template=m.template,
        variables=m.variables,
        url_keys=m.url_keys,
        header_base=m.header_base,
        flow_keys=m.flow_keys,
        flow_action_data=m.flow_action_data,
        document_link=m.document_link,
        filename=m.filename,
        flow_name=m.flow_name,
        flow_cta=m.flow_cta,
        list_options=m.list_options,
        list_section_title=m.list_section_title,
        display_name=m.display_name,
        company_id=m.company_id,
    )


def to_model_message_template(e: MessageTemplate) -> MessageTemplateModel:
    m = MessageTemplateModel()
    if e.id is not None:
        m.id = e.id
    m.keyword = e.keyword
    m.button_trigger = e.button_trigger
    m.type = e.type
    m.text = e.text
    m.interactive_type = e.interactive_type
    m.button_keys = e.button_keys
    m.footer_text = e.footer_text
    m.header_type = e.header_type
    m.header_content = e.header_content
    m.parameters = e.parameters
    m.template = e.template
    m.variables = e.variables
    m.url_keys = e.url_keys
    m.header_base = e.header_base
    m.flow_keys = e.flow_keys
    m.flow_action_data = e.flow_action_data
    m.document_link = e.document_link
    m.filename = e.filename
    m.flow_name = e.flow_name
    m.flow_cta = e.flow_cta
    m.list_options = e.list_options
    m.list_section_title = e.list_section_title
    m.display_name = e.display_name
    m.company_id = e.company_id
    return m


def to_domain_screening_conversation_status(
    m: ScreeningConversationStatusModel,
) -> ScreeningConversationStatus:
    return ScreeningConversationStatus(id=m.id, code=m.code, description=m.description)


def to_model_screening_conversation_status(
    e: ScreeningConversationStatus,
) -> ScreeningConversationStatusModel:
    model = ScreeningConversationStatusModel()
    model.id = e.id
    model.code = e.code
    model.description = e.description
    return model


def to_domain_screening_conversation(m: ScreeningConversationModel) -> ScreeningConversation:
    status = (
        to_domain_screening_conversation_status(m.status)
        if m.status is not None
        else status_from_id(m.status_id)
    )
    return ScreeningConversation(
        id=m.id,
        wa_phone_id=m.wa_phone_id,
        user_phone=m.user_phone,
        status=status,
        status_changed_at=m.status_changed_at,
        last_webhook_at=m.last_webhook_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model_screening_conversation(e: ScreeningConversation) -> ScreeningConversationModel:
    model = ScreeningConversationModel()
    if e.id is not None:
        model.id = e.id
    model.wa_phone_id = e.wa_phone_id
    model.user_phone = e.user_phone
    model.status_id = e.status.id
    if e.status_changed_at is not None:
        model.status_changed_at = e.status_changed_at
    if e.last_webhook_at is not None:
        model.last_webhook_at = e.last_webhook_at
    if e.created_at is not None:
        model.created_at = e.created_at
    if e.updated_at is not None:
        model.updated_at = e.updated_at
    return model


def to_domain_temp_message(m: TempMessageModel) -> TempMessage:
    return TempMessage(
        id=m.id,
        conversation_id=m.conversation_id,
        message_id=m.message_id,
        wa_id=m.wa_id,
        body=m.body,
        received_at=m.received_at,
        processing=m.processing,
        wa_type=m.wa_type,
        wa_interactive_type=m.wa_interactive_type,
        wa_type_id=m.wa_type_id,
        wa_interactive_type_id=m.wa_interactive_type_id,
    )


def to_model_temp_message(e: TempMessage) -> TempMessageModel:
    model = TempMessageModel()
    if e.id is not None:
        model.id = e.id
    model.conversation_id = e.conversation_id
    model.message_id = e.message_id
    model.wa_id = e.wa_id
    if isinstance(e.body, dict):
        model.body = dict(e.body)
    else:
        model.body = e.body
    if e.received_at is not None:
        model.received_at = e.received_at
    model.processing = e.processing
    model.wa_type = e.wa_type
    model.wa_interactive_type = e.wa_interactive_type
    model.wa_type_id = e.wa_type_id
    model.wa_interactive_type_id = e.wa_interactive_type_id
    return model
