"""
SQLAlchemy ORM models dedicated to the Ads Wizard integration.

These models live in the infrastructure layer because they are persistence
details (db tables) that implement domain ports. They intentionally rely on
the shared SQLAlchemy instance defined in ``app.dashboards_folder.models``.
"""

from baltra_sdk.legacy.dashboards_folder.models import db


class CompanyMetaLink(db.Model):
    __tablename__ = "company_meta_link"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies_screening.company_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    business_id = db.Column(db.Text, nullable=False)
    ad_account_id = db.Column(db.Text, nullable=False)
    page_id = db.Column(db.Text, nullable=True)
    wa_number_id = db.Column(db.Text, nullable=True)
    system_user_token = db.Column(db.Text, nullable=True)
    defaults = db.Column(db.JSON, nullable=False, default=dict)

    company = db.relationship("CompaniesScreening", backref="meta_link", uselist=False)

    def __repr__(self) -> str:
        return f"<CompanyMetaLink company_id={self.company_id} ad_account_id={self.ad_account_id}>"


class RoleCampaignBlueprint(db.Model):
    __tablename__ = "role_campaign_blueprint"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.role_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name_template = db.Column(db.Text, nullable=True)
    objective = db.Column(db.Text, nullable=True)
    special_ad_categories = db.Column(db.JSON, nullable=True)
    default_targeting = db.Column(db.JSON, nullable=True)
    default_creative = db.Column(db.JSON, nullable=True)
    default_budget_cents = db.Column(db.Integer, nullable=True)
    placements = db.Column(db.JSON, nullable=True)

    role = db.relationship("Roles", backref="campaign_blueprint", uselist=False)

    def __repr__(self) -> str:
        return f"<RoleCampaignBlueprint role_id={self.role_id}>"


class MetaPage(db.Model):
    __tablename__ = "meta_pages"

    page_id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    owner_type = db.Column(db.Text, nullable=False)
    business_id = db.Column(db.Text, nullable=True)
    permitted_tasks = db.Column(db.ARRAY(db.Text), nullable=True)
    is_default = db.Column(
        db.Boolean, nullable=False, server_default=db.text("false")
    )
    synced_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
    )

    __table_args__ = (
        db.CheckConstraint(
            "owner_type IN ('OWNED','CLIENT')", name="ck_meta_pages_owner_type"
        ),
    )

    def __repr__(self) -> str:
        return f"<MetaPage {self.page_id} owner={self.owner_type}>"


class MetaAdAccount(db.Model):
    __tablename__ = "meta_ad_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_ad_account_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    name = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, nullable=False)
    timezone_name = db.Column(db.Text, nullable=True)
    business_id = db.Column(db.Text, nullable=True)
    amount_spent = db.Column(db.Text, nullable=True)
    balance = db.Column(db.Text, nullable=True)
    raw = db.Column(db.JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<MetaAdAccount {self.fb_ad_account_id} {self.name}>"

    def __repr__(self) -> str:
        return f"<MetaAdAccount {self.fb_ad_account_id} {self.name}>"


class MetaCampaign(db.Model):
    __tablename__ = "meta_campaign"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_campaign_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies_screening.company_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.Text, nullable=False)
    objective = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    special_ad_categories = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
        onupdate=db.text("now()"),
    )

    company = db.relationship("CompaniesScreening", backref="meta_campaigns")

    def __repr__(self) -> str:
        return f"<MetaCampaign {self.id} {self.name}>"


class MetaAdSet(db.Model):
    __tablename__ = "meta_ad_set"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_ad_set_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("meta_campaign.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=True)
    daily_budget_cents = db.Column(db.Integer, nullable=True)
    targeting = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
        onupdate=db.text("now()"),
    )

    campaign = db.relationship("MetaCampaign", backref="meta_ad_sets")

    def __repr__(self) -> str:
        return f"<MetaAdSet {self.id} {self.name}>"


class MetaAd(db.Model):
    __tablename__ = "meta_ad"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_ad_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    ad_set_id = db.Column(
        db.Integer,
        db.ForeignKey("meta_ad_set.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    creative_id = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.text("now()"),
        onupdate=db.text("now()"),
    )

    ad_set = db.relationship("MetaAdSet", backref="meta_ads")

    def __repr__(self) -> str:
        return f"<MetaAd {self.id}>"


__all__ = [
    "CompanyMetaLink",
    "RoleCampaignBlueprint",
    "MetaPage",
    "MetaAdAccount",
    "MetaCampaign",
    "MetaAdSet",
    "MetaAd",
]
