from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy import func

from baltra_sdk.domain.ads_wizard.ports import CompaniesRepository
from baltra_sdk.legacy.dashboards_folder.models import CompaniesScreening, db
from baltra_sdk.infra.ads_wizard.sqlalchemy_models import CompanyMetaLink


class SqlAlchemyCompaniesRepository(CompaniesRepository):

    def _serialize_company(self, company: CompaniesScreening, link: Optional[CompanyMetaLink]) -> Dict[str, Any]:
        return {
            "company_id": company.company_id,
            "name": company.name,
            "phone": company.phone,
            "wa_id": company.wa_id,
            "has_meta_link": link is not None,
        }

    def list_companies(
        self,
        *,
        search: Optional[str],
        limit: int,
        offset: int,
        company_ids: Optional[List[int]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = (
            db.session.query(CompaniesScreening, CompanyMetaLink)
            .join(
                CompanyMetaLink,
                CompanyMetaLink.company_id == CompaniesScreening.company_id,
            )
        )

        if company_ids:
            query = query.filter(CompaniesScreening.company_id.in_(company_ids))

        normalized_search = (search or "").strip()
        if normalized_search:
            pattern = f"%{normalized_search.lower()}%"
            query = query.filter(
                func.lower(CompaniesScreening.name).like(pattern)
            )

        total = query.count()

        rows = (
            query.order_by(func.lower(CompaniesScreening.name))
            .offset(offset)
            .limit(limit)
            .all()
        )

        companies: List[Dict[str, Any]] = []
        for company, link in rows:
            company_dict: Dict[str, Any] = {
                "companyId": company.company_id,
                "name": company.name,
                "groupId": company.group_id,
                "waId": company.wa_id,
                "phone": company.phone,
                "hasMetaLink": link is not None,
                "hasSystemUserToken": bool(link.system_user_token) if link else False,
            }

            if link:
                company_dict["metaLink"] = {
                    "businessId": link.business_id,
                    "adAccountId": link.ad_account_id,
                    "pageId": link.page_id,
                    "waNumberId": link.wa_number_id,
                }
            else:
                company_dict["metaLink"] = None

            companies.append(company_dict)

        return companies, total

    def find_candidates_by_whatsapp(
        self,
        *,
        wa_number_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        base_query = (
            db.session.query(CompaniesScreening, CompanyMetaLink)
            .outerjoin(
                CompanyMetaLink,
                CompanyMetaLink.company_id == CompaniesScreening.company_id,
            )
        )

        seen: Dict[int, Dict[str, Any]] = {}

        def _collect(rows: List[Tuple[CompaniesScreening, Optional[CompanyMetaLink]]]) -> None:
            for company, link in rows:
                if company.company_id not in seen:
                    seen[company.company_id] = self._serialize_company(company, link)

        if wa_number_id:
            direct_matches = (
                base_query.filter(CompaniesScreening.wa_id == wa_number_id).all()
            )
            _collect(direct_matches)

        return list(seen.values())
