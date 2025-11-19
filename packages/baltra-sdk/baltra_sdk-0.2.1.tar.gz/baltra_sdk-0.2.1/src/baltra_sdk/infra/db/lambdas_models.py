from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, DateTime, Boolean,
    SmallInteger, Float, ForeignKey, Index, CheckConstraint, UniqueConstraint,
    PrimaryKeyConstraint, text, Enum, JSON, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC
from sqlalchemy.ext.mutable import MutableList


Base = declarative_base()


def build_db_url_from_settings(settings) -> str:
    return (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


class DBShim:
    def __init__(self, db_url: str):
        self.engine = create_engine(
            db_url,
            poolclass=NullPool,
            future=True,
        )
        self._SessionFactory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
        self.Session = scoped_session(self._SessionFactory)

    @classmethod
    def from_settings(cls, settings) -> "DBShim":
        return cls(build_db_url_from_settings(settings))

    @property
    def session(self):
        return self.Session()

    def remove_session(self):
        self.Session.remove()


ResponseTypeEnum = Enum(
    "text",
    "location",
    "voice",
    "phone_reference",
    "interactive",
    "name",
    "location_critical",
    name="response_type_enum",
    create_type=False,
)


class Candidates(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"))
    phone = Column(String(30), nullable=False)
    name = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    interview_date_time = Column(DateTime(timezone=True))
    funnel_state = Column(Text)
    grade = Column(Integer)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="SET NULL"))
    travel_time_minutes = Column(Integer, server_default=text("0"))
    age = Column(Integer)
    gender = Column(Text)
    interview_reminder_sent = Column(Boolean, nullable=False, default=False)
    application_reminder_sent = Column(Boolean, default=False)
    flow_state = Column(String(50), nullable=False, default="respuesta")
    start_date = Column(Date)
    interview_address = Column(Text)
    interview_map_link = Column(Text)
    eligible_roles = Column(JSONB)
    reschedule_sent = Column(Boolean, default=False)
    rejected_reason = Column(Text)
    screening_rejected_reason = Column(Text)
    end_flow_rejected = Column(Boolean, nullable=False, default=False)
    education_level = Column(Text)
    source = Column(Text)
    interview_confirmed = Column(Boolean, default=None)
    worked_here = Column(Boolean, nullable=True)
    company_group_id = Column(Integer, ForeignKey("company_groups.group_id"), nullable=True)
    eligible_companies = Column(JSONB, nullable=True)

    company = relationship("CompaniesScreening", backref="candidates")
    role = relationship("Roles", foreign_keys=[role_id], backref="candidates")
    screening_answers = relationship("ScreeningAnswers", backref="candidate", cascade="all, delete-orphan")
    funnel_logs = relationship("CandidateFunnelLog", backref="candidate", cascade="all, delete-orphan")
    screening_messages = relationship("ScreeningMessages", backref="candidate")

    __table_args__ = (
        PrimaryKeyConstraint("candidate_id", name="candidates_pkey1"),
        Index("idx_candidates_company", "company_id"),
        Index("idx_candidates_company_name", "company_id", "name"),
    )


class CompaniesScreening(Base):
    __tablename__ = "companies_screening"

    company_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    interview_excluded_dates = Column(MutableList.as_mutable(JSONB), default=list)
    interview_days = Column(MutableList.as_mutable(JSONB), default=list)
    interview_hours = Column(MutableList.as_mutable(JSONB), default=list)
    description = Column(Text)
    website = Column(Text)
    benefits = Column(MutableList.as_mutable(JSONB), default=list)
    general_faq = Column(JSONB)
    wa_id = Column(String)
    classifier_assistant_id = Column(String)
    general_purpose_assistant_id = Column(String)
    phone = Column(String)
    maps_link_json = Column(JSONB)
    interview_address_json = Column(JSONB)
    ad_trigger_phrase = Column(Text)
    reminder_schedule = Column(JSONB, nullable=False, default=dict)
    hr_contact = Column(Text)
    group_id = Column(Integer, ForeignKey("company_groups.group_id", ondelete="SET NULL"))
    customer_id = Column(String(50))
    additional_info = Column(Text)
    max_interviews_per_slot = Column(Integer, nullable=True)
    company_is_verified_by_meta = Column(Boolean, nullable=False, server_default=text("true"), default=True)
    timezone = Column(String(50), nullable=False, server_default=text("'America/Mexico_City'"), default="America/Mexico_City")

    __table_args__ = (
        CheckConstraint("char_length(description) <= 250", name="description_length_check"),
    )


class MessageTemplates(Base):
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True)
    keyword = Column(Text, nullable=False)
    button_trigger = Column(Text)
    type = Column(Text, nullable=False)
    text = Column(Text)
    interactive_type = Column(Text)
    button_keys = Column(JSONB)
    footer_text = Column(Text)
    header_type = Column(Text)
    header_content = Column(Text)
    parameters = Column(JSONB)
    template = Column(Text)
    variables = Column(JSONB)
    url_keys = Column(JSONB)
    header_base = Column(Text)
    flow_keys = Column(JSONB)
    flow_action_data = Column(JSONB)
    document_link = Column(Text)
    filename = Column(Text)
    flow_name = Column(Text)
    flow_cta = Column(Text)
    list_options = Column(JSONB)
    list_section_title = Column(Text)
    display_name = Column(Text)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"))

    company = relationship("CompaniesScreening", backref="message_templates")


class CandidateFunnelLog(Base):
    __tablename__ = "candidate_funnel_logs"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    previous_funnel_state = Column(Text)
    new_funnel_state = Column(Text, nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index("candidate_funnel_candidate_id_idx", "candidate_id"),
        Index("candidate_funnel_new_funnel_state_idx", "new_funnel_state"),
    )


class ScreeningMessages(Base):
    __tablename__ = "screening_messages"

    message_serial = Column(Integer, primary_key=True)
    wa_id = Column(String(50))
    company_id = Column(Integer, ForeignKey("companies_screening.company_id"))
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    message_id = Column(String(50))
    thread_id = Column(String(50))
    time_stamp = Column(DateTime)
    sent_by = Column(String(50))
    message_body = Column(Text)
    conversation_type = Column(String(10))
    whatsapp_msg_id = Column(String(100))
    set_id = Column(Integer, ForeignKey("question_sets.set_id"))
    question_id = Column(Integer, ForeignKey("screening_questions.question_id"))

    company = relationship("CompaniesScreening", backref="screening_messages")
    question = relationship("ScreeningQuestions", backref="screening_messages")


class ScreeningQuestions(Base):
    __tablename__ = "screening_questions"

    question_id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("question_sets.set_id", ondelete="CASCADE"), nullable=False)
    position = Column(SmallInteger, nullable=False)
    question = Column(Text, nullable=False)
    response_type = Column(ResponseTypeEnum, nullable=False)
    question_metadata = Column(JSONB)
    end_interview_answer = Column(Text)
    example_answer = Column(Text)
    is_blocked = Column(Boolean, default=False)
    eligibility_question = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    screening_answers = relationship("ScreeningAnswers", backref="question", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("set_id", "position", name="screening_questions_set_id_position_key"),
        Index("idx_questions_set_pos", "set_id", "position"),
    )


class QuestionSets(Base):
    __tablename__ = "question_sets"

    set_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=True)
    set_name = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    general_set = Column(Boolean, nullable=False, default=False)
    group_id = Column(Integer, ForeignKey("company_groups.group_id", ondelete="CASCADE"), nullable=True)

    company = relationship("CompaniesScreening", backref="question_sets")
    group = relationship("CompanyGroups", backref="question_sets")

    __table_args__ = (
        Index(
            "one_general_set_per_company",
            "company_id",
            "group_id",
            unique=True,
            postgresql_where=text("general_set IS TRUE"),
        ),
        CheckConstraint(
            "(company_id IS NOT NULL AND group_id IS NULL) OR "
            "(company_id IS NULL AND group_id IS NOT NULL)",
            name="company_or_group",
        ),
    )


class Roles(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=False)
    role_name = Column(Text, nullable=False)
    role_info = Column(JSONB)
    active = Column(Boolean, default=True)
    set_id = Column(Integer, ForeignKey("question_sets.set_id", ondelete="SET NULL"))
    eligibility_criteria = Column(JSONB)
    default_role = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    shift = Column(Text)
    location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="SET NULL"))

    __table_args__ = (
        CheckConstraint("char_length(role_name) <= 24", name="role_name_length_check"),
        CheckConstraint("char_length(shift) <= 72", name="shift_length_check"),
    )


class CompanyGroups(Base):
    __tablename__ = "company_groups"

    group_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    website = Column(Text)
    wa_id = Column(String(50))
    phone = Column(String(50))

    companies = relationship("CompaniesScreening", backref="group", cascade="all")

    __table_args__ = (
        Index("idx_company_groups_name", "name"),
    )


class ResponseTiming(Base):
    __tablename__ = "response_timings"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    company_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    time_delta = Column(NUMERIC, nullable=False)
    assistant_id = Column(String(50))
    model = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)


class ScreeningAnswers(Base):
    __tablename__ = "screening_answers"

    answer_id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("screening_questions.question_id", ondelete="CASCADE"), nullable=False)
    answer_raw = Column(Text)
    answer_json = JSONB
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        UniqueConstraint("candidate_id", "question_id", name="screening_answers_candidate_id_question_id_key"),
        Index("idx_answers_candidate", "candidate_id"),
        Index("idx_answers_question", "question_id"),
    )


class Locations(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    url = Column(Text)
    address = Column(Text)

    company = relationship("CompaniesScreening", backref="locations")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="check_valid_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="check_valid_longitude"),
        Index("idx_locations_company", "company_id"),
    )


class PhoneInterviewQuestions(Base):
    __tablename__ = "phone_interview_questions"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies_screening.company_id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="SET NULL"))
    question_text = Column(Text, nullable=False)
    position = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    company = relationship("CompaniesScreening", backref="phone_interview_questions")
    role = relationship("Roles", backref="phone_interview_questions")

    __table_args__ = (
        Index("idx_phone_q_company_role_pos", "company_id", "role_id", "position"),
        Index("idx_phone_q_company", "company_id"),
    )


class Companies(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    employee_assistant_id = Column(String)
    owner_assistant_id = Column(String)
    employee_vector_id = Column(String)
    owner_vector_id = Column(String)
    additional_info = Column(JSON)


class Employees(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    wa_id = Column(String(50))
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    area = Column(String(50))
    role = Column(String(50))
    context = Column(Text)
    weekly_path = Column(String)
    daily_path = Column(String)
    monthly_path = Column(String)
    rewards_path = Column(String)
    active = Column(Boolean, default=True)
    shift = Column(String(50))
    left_company = Column(Boolean, default=False)
    start_date = Column(Date)
    end_date = Column(Date)
    customer_key = Column(String(255))
    birth_date = Column(Date)
    sub_area = Column(String(50))
    latest_prizes = Column(JSON)

    company = relationship("Companies", backref="employees")


class Rewards(Base):
    __tablename__ = 'rewards'
    rewards_id = Column(BigInteger, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    date = Column(Date)
    week = Column(Integer)
    metric = Column(String)
    score = Column(String)
    weekday = Column(Integer)
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    customer_key = Column(String)

    employee = relationship("Employees", backref="rewards")
    company = relationship("Companies", backref="rewards")


class Points(Base):
    __tablename__ = 'points'
    points_id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer)
    week = Column(Integer)
    transaction = Column(String)
    points = Column(BigInteger)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    date = Column(Date, server_default=text('CURRENT_DATE'))
    area = Column(Text)
    metric = Column(Text)
    levels = Column(Integer)
    sub_points = Column(Integer)

    employee = relationship("Employees", backref="points")


class CompanyAreas(Base):
    __tablename__ = 'company_areas'
    area_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.company_id', ondelete="CASCADE"), nullable=False)
    area_name = Column(Text, nullable=False)
    rewards_description = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('company_id', 'area_name', name='company_areas_company_id_area_name_key'),
    )

    company = relationship("Companies", backref="areas")


class Prizes(Base):
    __tablename__ = "prizes"
    prize_id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    nombre = Column(Text)
    puntos = Column(Integer)
    precio = Column(Integer)
    link = Column(Text)
    active = Column(Boolean, default=True)
    description = Column(Text)
    min_days_in_company = Column(Integer, nullable=False, default=0)

    company = relationship("Companies", backref="prizes")


class Messages(Base):
    __tablename__ = 'messages'
    message_serial = Column(Integer, primary_key=True)
    wa_id = Column(String(50))
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    company_id = Column(Integer)
    message_id = Column(String(100))
    thread_id = Column(String(100))
    time_stamp = Column(DateTime)
    sent_by = Column(String(50))
    message_body = Column(Text)
    conversation_type = Column(String(10))
    whatsapp_msg_id = Column(String(100))

    employee = relationship("Employees", backref="messages")


class Redemptions(Base):
    __tablename__ = "redemptions"
    redemption_id = Column(Integer, primary_key=True)
    points_id = Column(BigInteger, ForeignKey("points.points_id"), nullable=False)
    prize_id = Column(BigInteger, ForeignKey("prizes.prize_id"), nullable=False)
    estimated_delivery_date = Column(Date)
    delivery_date_to_company = Column(Date)
    delivered_to_company = Column(Boolean, nullable=False, default=False)
    delivery_date_to_employee = Column(Date)
    delivered_to_employee = Column(Boolean, nullable=False, default=False)
    date_requested = Column(Date, server_default=text("CURRENT_DATE"))
    # FK corregido: Integer para empatar con Employees.employee_id
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    prize_url = Column(Text)

    points = relationship("Points", backref="redemptions")
    prize = relationship("Prizes", backref="redemptions")
    employee = relationship("Employees", backref="redemptions")
    company = relationship("Companies", backref="redemptions")
