
from baltra_sdk.application.ads_wizard.service import AdsWizardService
from baltra_sdk.infra.ads_wizard.meta_api_adapter import MetaApiAdapter
from baltra_sdk.infra.ads_wizard.sqlalchemy_template_repository import SqlAlchemyTemplateRepository
from baltra_sdk.infra.ads_wizard.sqlalchemy_link_repository import SqlAlchemyLinkRepository
from baltra_sdk.infra.ads_wizard.sqlalchemy_companies_repository import SqlAlchemyCompaniesRepository
from baltra_sdk.infra.ads_wizard.sqlalchemy_roles_repository import SqlAlchemyCompanyRolesRepository
from baltra_sdk.infra.ads_wizard.repositories import (
    SQLAlchemyMetaCampaignRepository,
    SQLAlchemyMetaAdSetRepository,
    SQLAlchemyMetaAdRepository,
    SQLAlchemyMetaAdAccountRepository,
)

def create_ads_wizard_service() -> AdsWizardService:
    meta_api_adapter = MetaApiAdapter()
    template_repository = SqlAlchemyTemplateRepository()
    link_repository = SqlAlchemyLinkRepository()
    companies_repository = SqlAlchemyCompaniesRepository()
    company_roles_repository = SqlAlchemyCompanyRolesRepository()
    meta_campaign_repository = SQLAlchemyMetaCampaignRepository()
    meta_ad_set_repository = SQLAlchemyMetaAdSetRepository()
    meta_ad_repository = SQLAlchemyMetaAdRepository()
    meta_ad_account_repository = SQLAlchemyMetaAdAccountRepository()

    return AdsWizardService(
        meta_ads_api=meta_api_adapter, 
        ad_templates_repository=template_repository,
        link_repository=link_repository,
        companies_repository=companies_repository,
        company_roles_repository=company_roles_repository,
        meta_campaign_repository=meta_campaign_repository,
        meta_ad_set_repository=meta_ad_set_repository,
        meta_ad_repository=meta_ad_repository,
        meta_ad_account_repository=meta_ad_account_repository,
    )
