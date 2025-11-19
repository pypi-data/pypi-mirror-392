from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import json

def build_db_uri() -> str:
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    if uri:
        return uri
    user = current_app.config["DB_USER"]
    password = current_app.config["DB_PASSWORD"]
    host = current_app.config["DB_HOST"]
    port = str(current_app.config.get("DB_PORT", 5432))
    name = current_app.config["DB_NAME"]
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

def create_db_engine() -> Engine:
    return create_engine(
        build_db_uri(),
        pool_pre_ping=True,
        future=True,
        json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
        json_deserializer=lambda s: json.loads(s),
    )
