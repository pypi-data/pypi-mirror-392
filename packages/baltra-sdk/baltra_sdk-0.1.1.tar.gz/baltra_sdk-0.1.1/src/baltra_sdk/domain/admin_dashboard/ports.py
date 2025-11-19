from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AdminDashboardRepository(ABC):
    @abstractmethod
    def get_funnel_buckets(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_funnel_status_by_company_formatted(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_time_to_hire(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_hires_by_role(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_sources(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_origins_evaluated(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_screening_questions_summary(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_rejections(self, company_id: int, source: str,
                       month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None,
                       company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def get_rejections_split(self, company_id: int,
                             month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None,
                             company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict[str, List[Dict]]:
        pass
    @abstractmethod
    def get_onboarding_summary(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_onboarding_checklists(self, company_id: int, checklist: Optional[int], month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_onboarding_satisfaction(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_documents_summary(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def list_stores(self, company_id: int, search: Optional[str] = None, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> Dict:
        pass

    @abstractmethod
    def toggle_store_active(self, company_id: int, store_id: int, is_active: bool) -> bool:
        pass

    @abstractmethod
    def get_documents_by_type(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def find_question_by_id(self, question_id: int) -> Optional[Dict]:
        pass

    @abstractmethod
    def find_template_by_id(self, template_id: int) -> Optional[Dict]:
        pass

    @abstractmethod
    def find_template_by_keyword(self, keyword: str, company_id: int) -> Optional[Dict]:
        pass

    @abstractmethod
    def update_screening_question(self, question_id: int, data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def update_message_template(self, template_id: int, data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_candidate_status_summary(self, company_id: int, month: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, company_ids: Optional[List[int]] = None, scope_all: bool = False) -> List[Dict]:
        pass
