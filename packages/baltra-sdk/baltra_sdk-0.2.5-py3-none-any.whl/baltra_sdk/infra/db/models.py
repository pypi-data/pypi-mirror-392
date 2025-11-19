# app/infrastructure/db/models.py
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    JSON,
    ForeignKey,
    CheckConstraint,
    Index,
    Boolean,
    DateTime,
    text,
    UniqueConstraint,
    SmallInteger,
    BigInteger,
)
from sqlalchemy.ext.mutable import MutableList
from baltra_sdk.infra.db.base import Base

class CompanyGroupModel(Base):
    __tablename__ = "company_groups"
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    wa_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    companies: Mapped[List["CompanyScreeningModel"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    question_sets: Mapped[List["QuestionSetModel"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    __table_args__ = (Index("idx_company_groups_name", "name"),)

class CompanyScreeningModel(Base):
    __tablename__ = "companies_screening"
    company_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interview_excluded_dates: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    interview_days: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    interview_hours: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefits: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    general_faq: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    wa_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    classifier_assistant_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    general_purpose_assistant_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    maps_link_json: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    interview_address_json: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    ad_trigger_phrase: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reminder_schedule: Mapped[Dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    hr_contact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company_groups.group_id", ondelete="SET NULL"), nullable=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    additional_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    group: Mapped[Optional[CompanyGroupModel]] = relationship(back_populates="companies")
    question_sets: Mapped[List["QuestionSetModel"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    max_interviews_per_slot: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    __table_args__ = (CheckConstraint("char_length(description) <= 250", name="description_length_check"),)

class LocationModel(Base):
    __tablename__ = "locations"
    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="check_valid_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="check_valid_longitude"),
        Index("idx_locations_company", "company_id"),
    )

class RoleModel(Base):
    __tablename__ = "roles"
    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=False)
    role_name: Mapped[str] = mapped_column(Text, nullable=False)
    role_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    set_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eligibility_criteria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    default_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shift: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)
    __table_args__ = (
        CheckConstraint("char_length(role_name) <= 24", name="role_name_length_check"),
        CheckConstraint("char_length(shift) <= 72", name="shift_length_check"),
    )

class QuestionSetModel(Base):
    __tablename__ = "question_sets"
    set_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=True)
    set_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    general_set: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("company_groups.group_id", ondelete="CASCADE"), nullable=True)

    company: Mapped[Optional[CompanyScreeningModel]] = relationship(back_populates="question_sets")
    group: Mapped[Optional[CompanyGroupModel]] = relationship(back_populates="question_sets")
    screening_questions: Mapped[List["ScreeningQuestionModel"]] = relationship(back_populates="question_set", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            "one_general_set_per_company",
            "company_id", "group_id",
            unique=True,
            postgresql_where=text("general_set IS TRUE")
        ),
        CheckConstraint(
            "(company_id IS NOT NULL AND group_id IS NULL) OR "
            "(company_id IS NULL AND group_id IS NOT NULL)",
            name="company_or_group"
        ),
    )

class ScreeningQuestionModel(Base):
    __tablename__ = "screening_questions"
    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    set_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_sets.set_id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    response_type: Mapped[str] = mapped_column(Text, nullable=False)
    question_metadata: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    end_interview_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    eligibility_question: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    question_set: Mapped["QuestionSetModel"] = relationship(back_populates="screening_questions")

    __table_args__ = (
        UniqueConstraint("set_id", "position", name="screening_questions_set_id_position_key"),
        Index("idx_questions_set_pos", "set_id", "position"),
    )


class MessageTemplateModel(Base):
    __tablename__ = "message_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    button_trigger: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interactive_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    button_keys: Mapped[Optional[Dict[str, object] | List[object]]] = mapped_column(JSON, nullable=True)
    footer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    header_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    header_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    variables: Mapped[Optional[Dict[str, object] | List[object]]] = mapped_column(JSON, nullable=True)
    url_keys: Mapped[Optional[Dict[str, object] | List[object]]] = mapped_column(JSON, nullable=True)
    header_base: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flow_keys: Mapped[Optional[Dict[str, object] | List[object]]] = mapped_column(JSON, nullable=True)
    flow_action_data: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    document_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flow_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flow_cta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    list_options: Mapped[Optional[List[Dict[str, object]] | List[object]]] = mapped_column(JSON, nullable=True)
    list_section_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    company_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("companies_screening.company_id", ondelete="CASCADE"),
        nullable=True,
    )
    company: Mapped[Optional["CompanyScreeningModel"]] = relationship(backref="message_templates")

    __table_args__ = (
        Index("idx_message_templates_company", "company_id"),
        Index("idx_message_templates_keyword", "keyword"),
    )


class ScreeningConversationStatusModel(Base):
    __tablename__ = "screening_conversation_status"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    conversations: Mapped[List["ScreeningConversationModel"]] = relationship(back_populates="status")


class ScreeningConversationModel(Base):
    __tablename__ = "screening_conversation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    wa_phone_id: Mapped[str] = mapped_column(String(32), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    status_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("screening_conversation_status.id", ondelete="RESTRICT"),
        nullable=False,
        server_default=text("1"),
    )
    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    last_webhook_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    active_run_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    active_thread_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    active_run_priority: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    status: Mapped["ScreeningConversationStatusModel"] = relationship(back_populates="conversations")
    temp_messages: Mapped[List["TempMessageModel"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("wa_phone_id", "user_phone", name="uq_screening_conversation_wa_phone_user_phone"),
        Index("idx_screening_conversation_status_changed", "status_id", "status_changed_at"),
        Index("idx_screening_conversation_last_webhook", "last_webhook_at"),
    )


class TempMessageModel(Base):
    __tablename__ = "temp_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("screening_conversation.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    wa_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    processing: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    # Optional denormalized type info for compatibility and easier ingest
    wa_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    wa_interactive_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    # Normalized type references
    wa_type_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("wa_message_type.id", ondelete="RESTRICT"), nullable=True
    )
    wa_interactive_type_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("wa_interactive_type.id", ondelete="RESTRICT"), nullable=True
    )
    openai_message_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    conversation: Mapped[Optional["ScreeningConversationModel"]] = relationship(back_populates="temp_messages")

    __table_args__ = (
        Index("idx_temp_messages_conversation_processing", "conversation_id", "processing"),
    )


class WaMessageTypeModel(Base):
    __tablename__ = "wa_message_type"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)


class WaInteractiveTypeModel(Base):
    __tablename__ = "wa_interactive_type"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
