"""Dominio del Baltra SDK."""

from importlib import import_module

admin_dashboard = import_module(f"{__name__}.admin_dashboard")
ads_wizard = import_module(f"{__name__}.ads_wizard")
auth = import_module(f"{__name__}.auth")
document_verification = import_module(f"{__name__}.document_verification")
models = import_module(f"{__name__}.models")
onboarding = import_module(f"{__name__}.onboarding")
ports = import_module(f"{__name__}.ports")
storage = import_module(f"{__name__}.storage")
screening_catalog = import_module(f"{__name__}.screening_catalog")

__all__ = [
    "admin_dashboard",
    "ads_wizard",
    "auth",
    "document_verification",
    "models",
    "onboarding",
    "ports",
    "storage",
    "screening_catalog",
]
