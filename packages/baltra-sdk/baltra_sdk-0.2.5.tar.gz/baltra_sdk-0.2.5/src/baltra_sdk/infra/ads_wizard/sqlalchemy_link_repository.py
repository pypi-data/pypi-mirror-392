from typing import Dict, Any, Optional, List
from baltra_sdk.domain.ads_wizard.ports import CompanyMetaLinkRepository
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.infra.ads_wizard.sqlalchemy_models import CompanyMetaLink, MetaPage

class SqlAlchemyLinkRepository(CompanyMetaLinkRepository):

    @staticmethod
    def _default_page_info() -> Optional[Dict[str, Any]]:
        default_page = MetaPage.query.filter_by(is_default=True).first()
        if not default_page:
            return None
        return {
            "id": default_page.page_id,
            "name": default_page.name,
        }

    def get_link_by_company_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        link = CompanyMetaLink.query.filter_by(company_id=company_id).first()
        if not link:
            return None

        page_id = link.page_id
        page_name: Optional[str] = None
        default_page = self._default_page_info()
        if not page_id and default_page:
            page_id = default_page["id"]
            page_name = default_page.get("name")
        elif page_id and default_page and page_id == default_page["id"]:
            page_name = default_page.get("name")

        return {
            "company_id": link.company_id,
            "business_id": link.business_id,
            "ad_account_id": link.ad_account_id,
            "page_id": page_id,
            "page_name": page_name,
            "wa_number_id": link.wa_number_id,
            "system_user_token": link.system_user_token,
            "defaults": link.defaults or {},
        }

    def get_link_by_ad_account_id(self, ad_account_id: str) -> Optional[Dict[str, Any]]:
        normalized = ad_account_id.replace("act_", "")
        link = CompanyMetaLink.query.filter_by(ad_account_id=normalized).first()
        if not link:
            return None

        page_id = link.page_id
        page_name: Optional[str] = None
        default_page = self._default_page_info()
        if not page_id and default_page:
            page_id = default_page["id"]
            page_name = default_page.get("name")
        elif page_id and default_page and page_id == default_page["id"]:
            page_name = default_page.get("name")

        return {
            "company_id": link.company_id,
            "business_id": link.business_id,
            "ad_account_id": link.ad_account_id,
            "page_id": page_id,
            "page_name": page_name,
            "wa_number_id": link.wa_number_id,
            "system_user_token": link.system_user_token,
            "defaults": link.defaults or {},
        }

    def link_company_ad_account(self, company_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        link = CompanyMetaLink.query.filter_by(company_id=company_id).first()
        if not link:
            link = CompanyMetaLink(company_id=company_id)

        if "ad_account_id" in payload and payload["ad_account_id"] is not None:
            payload["ad_account_id"] = str(payload["ad_account_id"]).replace("act_", "")

        for key, value in payload.items():
            setattr(link, key, value)

        db.session.add(link)
        db.session.commit()

        return self.get_link_by_company_id(company_id)

    def list_links(self) -> List[Dict[str, Any]]:
        records = CompanyMetaLink.query.order_by(CompanyMetaLink.company_id.asc()).all()
        default_page_info = self._default_page_info()
        results: List[Dict[str, Any]] = []
        for link in records:
            page_id: Optional[str] = link.page_id
            page_name: Optional[str] = None
            if not page_id and default_page_info:
                page_id = default_page_info["id"]
                page_name = default_page_info.get("name")
            elif page_id and default_page_info and page_id == default_page_info["id"]:
                page_name = default_page_info.get("name")

            results.append(
                {
                    "company_id": link.company_id,
                    "business_id": link.business_id,
                    "ad_account_id": link.ad_account_id,
                    "page_id": page_id,
                    "page_name": page_name,
                    "wa_number_id": link.wa_number_id,
                    "system_user_token": link.system_user_token,
                    "defaults": link.defaults or {},
                }
            )
        return results
