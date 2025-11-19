"""Componentes legacy expuestos temporalmente por el Baltra SDK."""

import warnings

from . import dashboards_folder  # noqa: F401

warnings.warn(
    "Importando componentes legacy desde baltra_sdk.legacy. "
    "PLAN: refactorizarlos hacia módulos domain/infra antes de la versión 1.0.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["dashboards_folder"]
