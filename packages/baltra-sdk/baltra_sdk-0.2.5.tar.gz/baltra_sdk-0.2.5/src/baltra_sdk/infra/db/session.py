# app/infrastructure/db/session.py
from typing import Optional
from sqlalchemy.orm import sessionmaker, scoped_session, Session as OrmSession
from sqlalchemy.engine import Engine
from flask import has_app_context
from baltra_sdk.infra.db.engine import create_db_engine

_session_factory: Optional[sessionmaker] = None
_scoped: Optional[scoped_session] = None

def configure_session(engine: Engine) -> None:
    global _session_factory, _scoped
    _session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    _scoped = scoped_session(_session_factory)

def _ensure_configured() -> None:
    global _scoped
    if _scoped is None:
        if not has_app_context():
            raise RuntimeError("Database session is not configured")
        engine = create_db_engine()
        configure_session(engine)

def get_session() -> OrmSession:
    _ensure_configured()
    return _scoped()

def remove_session() -> None:
    if _scoped is not None:
        _scoped.remove()
