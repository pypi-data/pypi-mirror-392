from typing import Dict, Any, Optional, List
from baltra_sdk.domain.ads_wizard.ports import (
    MetaCampaignRepository,
    MetaAdSetRepository,
    MetaAdRepository,
    MetaAdAccountRepository,
)
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.infra.ads_wizard.sqlalchemy_models import (
    MetaCampaign,
    MetaAdSet,
    MetaAd,
    MetaAdAccount,
)

def _serialize(model) -> Optional[Dict[str, Any]]:
    if model is None:
        return None
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


class SQLAlchemyMetaCampaignRepository(MetaCampaignRepository):
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        meta_campaign = MetaCampaign(**campaign_data)
        db.session.add(meta_campaign)
        db.session.commit()
        return _serialize(meta_campaign)

    def get_by_meta_id(self, meta_campaign_id: str) -> Optional[Dict[str, Any]]:
        campaign = MetaCampaign.query.filter_by(meta_campaign_id=meta_campaign_id).first()
        return _serialize(campaign)

    def list_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        campaigns = (
            MetaCampaign.query.filter_by(company_id=company_id)
            .order_by(MetaCampaign.created_at.desc())
            .all()
        )
        return [_serialize(campaign) for campaign in campaigns]

    def upsert(self, *, company_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        meta_campaign_id = payload.get("meta_campaign_id")
        if not meta_campaign_id:
            raise ValueError("meta_campaign_id is required to upsert a campaign.")

        campaign = MetaCampaign.query.filter_by(meta_campaign_id=meta_campaign_id).first()
        if campaign is None:
            campaign = MetaCampaign(meta_campaign_id=meta_campaign_id, company_id=company_id)
            db.session.add(campaign)

        campaign.company_id = company_id
        if "name" in payload:
            campaign.name = payload.get("name")
        if "objective" in payload:
            campaign.objective = payload.get("objective")
        if "status" in payload:
            campaign.status = payload.get("status")
        if "special_ad_categories" in payload:
            campaign.special_ad_categories = payload.get("special_ad_categories")
        if payload.get("created_at") is not None:
            campaign.created_at = payload.get("created_at")
        if payload.get("updated_at") is not None:
            campaign.updated_at = payload.get("updated_at")

        db.session.commit()
        return _serialize(campaign)

class SQLAlchemyMetaAdSetRepository(MetaAdSetRepository):

    def create_ad_set(self, ad_set_data: Dict[str, Any]) -> Dict[str, Any]:
        meta_ad_set = MetaAdSet(**ad_set_data)
        db.session.add(meta_ad_set)
        db.session.commit()
        return _serialize(meta_ad_set)

    def get_by_meta_id(self, meta_ad_set_id: str) -> Optional[Dict[str, Any]]:
        ad_set = MetaAdSet.query.filter_by(meta_ad_set_id=meta_ad_set_id).first()
        return _serialize(ad_set)

    def list_by_campaign_internal_id(self, campaign_internal_id: int) -> List[Dict[str, Any]]:
        ad_sets = (
            MetaAdSet.query.filter_by(campaign_id=campaign_internal_id)
            .order_by(MetaAdSet.created_at.desc())
            .all()
        )
        return [_serialize(ad_set) for ad_set in ad_sets]

    def upsert(self, *, campaign_internal_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        meta_ad_set_id = payload.get("meta_ad_set_id")
        if not meta_ad_set_id:
            raise ValueError("meta_ad_set_id is required to upsert an ad set.")

        ad_set = MetaAdSet.query.filter_by(meta_ad_set_id=meta_ad_set_id).first()
        if ad_set is None:
            ad_set = MetaAdSet(meta_ad_set_id=meta_ad_set_id, campaign_id=campaign_internal_id)
            db.session.add(ad_set)

        ad_set.campaign_id = campaign_internal_id
        if "name" in payload:
            ad_set.name = payload.get("name")
        if "status" in payload:
            ad_set.status = payload.get("status")
        if "daily_budget_cents" in payload:
            ad_set.daily_budget_cents = payload.get("daily_budget_cents")
        if "targeting" in payload:
            ad_set.targeting = payload.get("targeting")
        if payload.get("created_at") is not None:
            ad_set.created_at = payload.get("created_at")
        if payload.get("updated_at") is not None:
            ad_set.updated_at = payload.get("updated_at")

        db.session.commit()
        return _serialize(ad_set)

class SQLAlchemyMetaAdRepository(MetaAdRepository):
    
    def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        meta_ad = MetaAd(**ad_data)
        db.session.add(meta_ad)
        db.session.commit()
        return _serialize(meta_ad)

    def get_by_meta_id(self, meta_ad_id: str) -> Optional[Dict[str, Any]]:
        ad = MetaAd.query.filter_by(meta_ad_id=meta_ad_id).first()
        return _serialize(ad)

    def list_by_ad_set_internal_id(self, ad_set_internal_id: int) -> List[Dict[str, Any]]:
        ads = (
            MetaAd.query.filter_by(ad_set_id=ad_set_internal_id)
            .order_by(MetaAd.created_at.desc())
            .all()
        )
        return [_serialize(ad) for ad in ads]

    def upsert(self, *, ad_set_internal_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        meta_ad_id = payload.get("meta_ad_id")
        if not meta_ad_id:
            raise ValueError("meta_ad_id is required to upsert an ad.")

        ad = MetaAd.query.filter_by(meta_ad_id=meta_ad_id).first()
        if ad is None:
            ad = MetaAd(meta_ad_id=meta_ad_id, ad_set_id=ad_set_internal_id)
            db.session.add(ad)

        ad.ad_set_id = ad_set_internal_id
        if "creative_id" in payload:
            ad.creative_id = payload.get("creative_id")
        if "status" in payload:
            ad.status = payload.get("status")
        if payload.get("created_at") is not None:
            ad.created_at = payload.get("created_at")
        if payload.get("updated_at") is not None:
            ad.updated_at = payload.get("updated_at")

        db.session.commit()
        return _serialize(ad)

class SQLAlchemyMetaAdAccountRepository(MetaAdAccountRepository):

    def upsert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        account_id = payload.get("fb_ad_account_id")
        if not account_id:
            raise ValueError("fb_ad_account_id is required to upsert an ad account")

        record = MetaAdAccount.query.filter_by(fb_ad_account_id=account_id).first()
        if record is None:
            record = MetaAdAccount(fb_ad_account_id=account_id)
            db.session.add(record)

        if "name" in payload:
            record.name = payload.get("name")
        if "currency" in payload:
            record.currency = payload.get("currency")
        if "timezone_name" in payload:
            record.timezone_name = payload.get("timezone_name")
        if "business_id" in payload:
            record.business_id = payload.get("business_id")
        if "amount_spent" in payload:
            record.amount_spent = payload.get("amount_spent")
        if "balance" in payload:
            record.balance = payload.get("balance")
        if "raw" in payload:
            record.raw = payload.get("raw")

        db.session.commit()
        return _serialize(record)
