from typing import List, Optional, Iterable
from sqlalchemy.orm import Session
from baltra_sdk.domain.models.company_group import CompanyGroup
from baltra_sdk.domain.models.company_screening import CompanyScreening
from baltra_sdk.domain.models.location import Location
from baltra_sdk.domain.models.role import Role
from baltra_sdk.domain.models.screening_flow import QuestionSet, ScreeningQuestion, MessageTemplate
from baltra_sdk.domain.ports.role_repository import RoleRepository
from baltra_sdk.infra.db.models import (
    CompanyGroupModel,
    CompanyScreeningModel,
    LocationModel,
    RoleModel,
    QuestionSetModel,
    ScreeningQuestionModel,
    MessageTemplateModel
)
from baltra_sdk.infra.db.mappers import (
    to_domain_company_group,
    to_model_company_group,
    to_domain_company_screening,
    to_model_company_screening,
    to_domain_location,
    to_model_location,
    to_domain_role,
    to_model_role,
    to_domain_question_set,
    to_model_question_set,
    to_domain_screening_question,
    to_model_screening_question,
    to_domain_message_template,
    to_model_message_template,
)

class SqlAlchemyCompanyGroupRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: CompanyGroup) -> CompanyGroup:
        model = to_model_company_group(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_company_group(model)

    def get(self, group_id: int) -> Optional[CompanyGroup]:
        m = self.session.get(CompanyGroupModel, group_id)
        return to_domain_company_group(m) if m else None


class SqlAlchemyCompanyScreeningRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: CompanyScreening) -> CompanyScreening:
        model = to_model_company_screening(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_company_screening(model)

    def bulk_create(self, entities: Iterable[CompanyScreening]) -> List[CompanyScreening]:
        models = [to_model_company_screening(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_company_screening(m) for m in models]

    def get(self, company_id: int) -> Optional[CompanyScreening]:
        m = self.session.get(CompanyScreeningModel, company_id)
        return to_domain_company_screening(m) if m else None


class SqlAlchemyLocationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: Location) -> Location:
        model = to_model_location(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_location(model)

    def bulk_create(self, entities: Iterable[Location]) -> List[Location]:
        models = [to_model_location(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_location(m) for m in models]

    def get(self, location_id: int) -> Optional[Location]:
        m = self.session.get(LocationModel, location_id)
        return to_domain_location(m) if m else None


class SqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: Role) -> Role:
        model = to_model_role(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_role(model)

    def bulk_create(self, entities: List[Role]) -> List[Role]:
        models = [to_model_role(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_role(m) for m in models]

    def get(self, role_id: int) -> Optional[Role]:
        m = self.session.get(RoleModel, role_id)
        return to_domain_role(m) if m else None

    def assign_set_id(self, role_id: int, set_id: int) -> None:
        model = self.session.get(RoleModel, role_id)
        if model:
            model.set_id = set_id
            self.session.flush()
            self.session.refresh(model)


class SqlAlchemyQuestionSetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: QuestionSet) -> QuestionSet:
        model = to_model_question_set(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_question_set(model)

    def bulk_create(self, entities: Iterable[QuestionSet]) -> List[QuestionSet]:
        models = [to_model_question_set(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_question_set(m) for m in models]

    def get(self, set_id: int) -> Optional[QuestionSet]:
        m = self.session.get(QuestionSetModel, set_id)
        return to_domain_question_set(m) if m else None


class SqlAlchemyScreeningQuestionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: ScreeningQuestion) -> ScreeningQuestion:
        model = to_model_screening_question(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_screening_question(model)

    def bulk_create(self, entities: Iterable[ScreeningQuestion]) -> List[ScreeningQuestion]:
        models = [to_model_screening_question(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_screening_question(m) for m in models]

    def get(self, question_id: int) -> Optional[ScreeningQuestion]:
        m = self.session.get(ScreeningQuestionModel, question_id)
        return to_domain_screening_question(m) if m else None


class SqlAlchemyMessageTemplateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: MessageTemplate) -> MessageTemplate:
        model = to_model_message_template(entity)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_message_template(model)

    def bulk_create(self, entities: Iterable[MessageTemplate]) -> List[MessageTemplate]:
        models = [to_model_message_template(e) for e in entities]
        self.session.add_all(models)
        self.session.flush()
        for m in models:
            self.session.refresh(m)
        return [to_domain_message_template(m) for m in models]

    def get(self, template_id: int) -> Optional[MessageTemplate]:
        m = self.session.get(MessageTemplateModel, template_id)
        return to_domain_message_template(m) if m else None

    def find_by_company(self, company_id: int) -> List[MessageTemplate]:
        results = (
            self.session.query(MessageTemplateModel)
            .filter(MessageTemplateModel.company_id == company_id)
            .all()
        )
        return [to_domain_message_template(r) for r in results]

    def find_by_keyword(self, company_id: int, keyword: str) -> Optional[MessageTemplate]:
        result = (
            self.session.query(MessageTemplateModel)
            .filter(
                MessageTemplateModel.company_id == company_id,
                MessageTemplateModel.keyword == keyword,
            )
            .first()
        )
        return to_domain_message_template(result) if result else None

    def find_by_keyword_or_trigger(self, keyword: str) -> Optional[MessageTemplate]:
        result = (
            self.session.query(MessageTemplateModel)
            .filter(
                (MessageTemplateModel.keyword == keyword)
                | (MessageTemplateModel.button_trigger == keyword)
            )
            .first()
        )
        return to_domain_message_template(result) if result else None

    def delete(self, template_id: int) -> None:
        self.session.query(MessageTemplateModel).filter(
            MessageTemplateModel.id == template_id
        ).delete()
        self.session.flush()
