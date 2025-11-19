
from typing import Dict, Any, Optional
from baltra_sdk.domain.ads_wizard.ports import RoleBlueprintRepository
from baltra_sdk.infra.ads_wizard.sqlalchemy_models import RoleCampaignBlueprint

class SqlAlchemyBlueprintRepository(RoleBlueprintRepository):

    def get_blueprint_by_role_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        # Assuming RoleCampaignBlueprint is a SQLAlchemy model
        blueprint = RoleCampaignBlueprint.query.filter_by(role_id=role_id).first()
        
        if not blueprint:
            return None
            
        return {
            "role_id": blueprint.role_id,
            "name_template": blueprint.name_template,
            "objective": blueprint.objective,
            "special_ad_categories": blueprint.special_ad_categories,
            "default_targeting": blueprint.default_targeting,
            "default_creative": blueprint.default_creative,
            "default_budget_cents": blueprint.default_budget_cents,
            "placements": blueprint.placements,
        }
