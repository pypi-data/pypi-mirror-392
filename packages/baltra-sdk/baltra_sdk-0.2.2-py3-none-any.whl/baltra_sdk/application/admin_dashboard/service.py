from typing import List, Dict, Any, Optional

from baltra_sdk.domain.admin_dashboard.ports import AdminDashboardRepository
from baltra_sdk.domain.users.user_repository import UserRepository
from baltra_sdk.domain.users.user import User


class AdminDashboardService:
    def __init__(
        self,
        company_id: int,
        repo: AdminDashboardRepository,
        user_repo: Optional[UserRepository] = None,
    ):
        self.company_id = company_id
        self.repo = repo
        self.user_repo = user_repo

    def _serialize_last_login_user(self, user: User | None) -> Optional[Dict[str, Any]]:
        if not user:
            return None
        attributes = user.attributes or {}
        return {
            "username": user.username,
            "email": user.email,
            "status": user.status,
            "enabled": user.enabled,
            "last_login": attributes.get("custom:last_login"),
            "company_id": attributes.get("custom:company_id"),
            "is_admin": attributes.get("custom:is_admin"),
        }

    def funnel(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_funnel_buckets(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def funnel_formated(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_funnel_status_by_company_formatted(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def time_to_hire(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_time_to_hire(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def hires_by_role(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_hires_by_role(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def sources(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_sources(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def origins_evaluated(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_origins_evaluated(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def screening_questions(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_screening_questions_summary(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def rejections(self, source: str, month: Optional[str], start_date: Optional[str],
                   end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_rejections(self.company_id, source, month, start_date, end_date, company_ids, scope_all)

    def rejections_split(self, month: Optional[str], start_date: Optional[str],
                         end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict[str, List[Dict]]:
        return self.repo.get_rejections_split(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def onboarding_summary(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_onboarding_summary(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def onboarding_checklists(self, checklist: Optional[int], month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_onboarding_checklists(self.company_id, checklist, month, start_date, end_date, company_ids, scope_all)

    def onboarding_satisfaction(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_onboarding_satisfaction(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def documents_summary(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        return self.repo.get_documents_summary(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def stores_list(self, search: Optional[str], month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> Dict:
        data = self.repo.list_stores(
            self.company_id, search, month, start_date, end_date, company_ids, scope_all
        )
        if not self.user_repo:
            return data

        items = data.get("items", [])
        if not items:
            return data

        ids_to_lookup = {str(item.get("company_id")) for item in items if item.get("company_id") is not None}
        try:
            users_map = self.user_repo.get_latest_non_admin_by_companies(ids_to_lookup)
        except Exception:
            users_map = {cid: None for cid in ids_to_lookup}

        for item in items:
            cid = item.get("company_id")
            if cid is None:
                item["last_login_user"] = None
                continue
            cognito_user = users_map.get(str(cid))
            item["last_login_user"] = self._serialize_last_login_user(cognito_user)
        return data

    def toggle_store_active(self, store_id: int, is_active: bool) -> bool:
        return self.repo.toggle_store_active(self.company_id, store_id, is_active)

    def documents_by_type(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict]:
        return self.repo.get_documents_by_type(self.company_id, month, start_date, end_date, company_ids, scope_all)

    def get_question_options(self, question_id: int) -> Optional[Dict]:
        question = self.repo.find_question_by_id(question_id)
        if not question or question.get('response_type') != 'interactive':
            return None
        template = self.repo.find_template_by_keyword(question['question'], self.company_id)
        return template.get('options') if template else None

    def update_screening_question(self, question_id: int, data: Dict) -> Optional[Dict]:
        return self.repo.update_screening_question(question_id, data)

    def update_message_template(self, template_id: int, data: Dict) -> Optional[Dict]:
        return self.repo.update_message_template(template_id, data)

    def candidate_status_summary(self, month: Optional[str], start_date: Optional[str], end_date: Optional[str], company_ids: Optional[List[int]], scope_all: bool) -> List[Dict[str, Any]]:
        return self.repo.get_candidate_status_summary(self.company_id, month, start_date, end_date, company_ids, scope_all)

