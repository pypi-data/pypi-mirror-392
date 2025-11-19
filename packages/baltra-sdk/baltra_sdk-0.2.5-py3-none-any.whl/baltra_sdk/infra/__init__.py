"""Infraestructura del Baltra SDK."""

from importlib import import_module

admin_dashboard = import_module(f"{__name__}.admin_dashboard")
ads_wizard = import_module(f"{__name__}.ads_wizard")
auth = import_module(f"{__name__}.auth")
aws = import_module(f"{__name__}.aws")
db = import_module(f"{__name__}.db")
di = import_module(f"{__name__}.di")
document_verification = import_module(f"{__name__}.document_verification")
onboarding = import_module(f"{__name__}.onboarding")
repositories = import_module(f"{__name__}.repositories")
uow = import_module(f"{__name__}.uow")
webhooks = import_module(f"{__name__}.webhooks")

__all__ = [
    "admin_dashboard",
    "ads_wizard",
    "auth",
    "aws",
    "db",
    "di",
    "document_verification",
    "onboarding",
    "repositories",
    "uow",
    "webhooks",
]
