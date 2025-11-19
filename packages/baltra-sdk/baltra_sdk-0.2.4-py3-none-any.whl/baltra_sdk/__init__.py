"""Paquete agregador del Baltra SDK."""

from importlib import import_module as _import_module

__version__ = "0.1.0"

domain = _import_module("baltra_sdk.domain")
infra = _import_module("baltra_sdk.infra")
interfaces = _import_module("baltra_sdk.interfaces")
shared = _import_module("baltra_sdk.shared")
legacy = _import_module("baltra_sdk.legacy")

__all__ = ["domain", "infra", "interfaces", "shared", "legacy", "__version__"]
