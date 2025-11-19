from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass(frozen=True, slots=True)
class CompanyScreening:
    company_id: Optional[int] = None
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    interview_excluded_dates: List[str] = field(default_factory=list)
    interview_days: List[str] = field(default_factory=list)
    interview_hours: List[str] = field(default_factory=list)
    description: Optional[str] = None
    website: Optional[str] = None
    benefits: List[str] = field(default_factory=list)
    general_faq: Optional[Dict[str, object]] = None
    wa_id: Optional[str] = None
    classifier_assistant_id: Optional[str] = None
    general_purpose_assistant_id: Optional[str] = None
    phone: Optional[str] = None
    maps_link_json: Optional[Dict[str, object]] = None
    interview_address_json: Optional[Dict[str, object]] = None
    ad_trigger_phrase: Optional[str] = None
    reminder_schedule: Dict[str, object] = field(default_factory=dict)
    hr_contact: Optional[str] = None
    group_id: Optional[int] = None
    customer_id: Optional[str] = None
    additional_info: Optional[str] = None
