
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

class MetaAdsApi(ABC):

    # ... (existing MetaAdsApi methods) ...

    @abstractmethod
    def create_campaign(self, ad_account_id: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_ad_set(self, ad_account_id: str, ad_set_payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_ad_image(self, ad_account_id: str, asset: Any, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_ad_creative(self, ad_account_id: str, creative_payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_ad(self, ad_account_id: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_campaign_draft(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_campaigns(self, ad_account_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_ad_sets(self, campaign_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_ads_for_ad_set(self, ad_set_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_whatsapp_business_account(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_user_businesses(self, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_campaign_status(self, campaign_id: str, status: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_ad_set_status(self, ad_set_id: str, status: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_user_businesses(self, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_owned_whatsapp_business_accounts(self, business_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_client_whatsapp_business_accounts(self, business_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_phone_numbers(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        pass


class AdTemplatesRepository(ABC):

    @abstractmethod
    def create_template(self, kind: str, key: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class CompaniesRepository(ABC):

    @abstractmethod
    def list_companies(
        self,
        *,
        search: Optional[str],
        limit: int,
        offset: int,
        company_ids: Optional[List[int]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return companies along with total count."""
        pass

    @abstractmethod
    def find_candidates_by_whatsapp(
        self,
        *,
        wa_number_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return possible company matches for the given WhatsApp identifiers."""
        pass

class CompanyMetaLinkRepository(ABC):
    
    @abstractmethod
    def get_link_by_company_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_link_by_ad_account_id(self, ad_account_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def link_company_ad_account(self, company_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_links(self) -> List[Dict[str, Any]]:
        pass

class CompanyRolesRepository(ABC):

    @abstractmethod
    def list_roles_for_company(self, company_id: int) -> List[Dict[str, Any]]:
        pass


class RoleBlueprintRepository(ABC):

    @abstractmethod
    def get_blueprint_by_role_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        pass

class MetaCampaignRepository(ABC):

    @abstractmethod
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_by_meta_id(self, meta_campaign_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def upsert(self, *, company_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class MetaAdSetRepository(ABC):

    @abstractmethod
    def create_ad_set(self, ad_set_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_by_meta_id(self, meta_ad_set_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_by_campaign_internal_id(self, campaign_internal_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def upsert(self, *, campaign_internal_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class MetaAdRepository(ABC):

    @abstractmethod
    def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_by_meta_id(self, meta_ad_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_by_ad_set_internal_id(self, ad_set_internal_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def upsert(self, *, ad_set_internal_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class MetaAdAccountRepository(ABC):

    @abstractmethod
    def upsert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
