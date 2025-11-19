
from typing import Dict, Any
from baltra_sdk.domain.ads_wizard.ports import AdTemplatesRepository
from baltra_sdk.legacy.dashboards_folder.models import db, AdTemplate

class SqlAlchemyTemplateRepository(AdTemplatesRepository):

    def create_template(self, kind: str, key: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        ad_template = AdTemplate(kind=kind, key=key, json_data=json_data)
        db.session.add(ad_template)
        db.session.commit()
        return {
            "id": ad_template.id,
            "kind": ad_template.kind,
            "key": ad_template.key,
            "json": ad_template.json_data,
            "created_at": ad_template.created_at.isoformat()
        }
