from typing import Optional
from sqlalchemy.orm import Session
from baltra_sdk.infra.db.session import get_session
from baltra_sdk.infra.repositories.sqlalchemy_repositories import (
    SqlAlchemyCompanyGroupRepository,
    SqlAlchemyCompanyScreeningRepository,
    SqlAlchemyLocationRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyQuestionSetRepository,
    SqlAlchemyScreeningQuestionRepository,
    SqlAlchemyMessageTemplateRepository,
)

class SqlAlchemyUnitOfWork:
    def __init__(self, session: Optional[Session] = None) -> None:
        self.session = session or get_session()
        self.company_groups = SqlAlchemyCompanyGroupRepository(self.session)
        self.company_screenings = SqlAlchemyCompanyScreeningRepository(self.session)
        self.locations = SqlAlchemyLocationRepository(self.session)
        self.roles = SqlAlchemyRoleRepository(self.session)
        self.question_sets = SqlAlchemyQuestionSetRepository(self.session)
        self.screening_questions = SqlAlchemyScreeningQuestionRepository(self.session)
        self.message_templates = SqlAlchemyMessageTemplateRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
