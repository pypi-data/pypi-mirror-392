import os
import sys
from dataclasses import dataclass
import logging
from urllib.parse import urlparse, parse_qs
try:
    from authlib.integrations.flask_client import OAuth
except ImportError as _authlib_exc:  # pragma: no cover - runtime fallback
    OAuth = None  # type: ignore
    _AUTHLIB_IMPORT_ERROR = _authlib_exc
else:
    _AUTHLIB_IMPORT_ERROR = None

try:
    from flask_session import Session
except ImportError as _session_exc:  # pragma: no cover - runtime fallback
    Session = None  # type: ignore
    _SESSION_IMPORT_ERROR = _session_exc
else:
    _SESSION_IMPORT_ERROR = None

try:
    from dotenv import load_dotenv as _load_dotenv, find_dotenv as _find_dotenv
except ImportError:  # pragma: no cover - runtime fallback
    logging.warning("python-dotenv not installed; environment variables will not be loaded from .env")

    def _load_dotenv(*args, **kwargs):  # type: ignore
        return False

    def _find_dotenv(*args, **kwargs):  # type: ignore
        return ""

_ENV_INITIALIZED = False
_DATABASE_URL_KEYS = (
    "DATABASE_URL",
    "DB_CONNECTION_URL",
    "POSTGRES_URL",
    "POSTGRESQL_URL",
)


def _load_project_environment() -> None:
    """Load environment variables from the host project (once)."""
    global _ENV_INITIALIZED
    if _ENV_INITIALIZED:
        return

    dotenv_path: str | None = os.getenv("BALTRA_SDK_DOTENV_FILE")
    if not dotenv_path:
        candidate = _find_dotenv(usecwd=True)
        dotenv_path = candidate or None

    override = os.getenv("BALTRA_SDK_DOTENV_OVERRIDE", "false").lower() in {"1", "true", "yes"}
    if dotenv_path:
        loaded = _load_dotenv(dotenv_path, override=override)
        if loaded:
            logging.debug("Loaded environment variables from %s (override=%s)", dotenv_path, override)
        else:
            logging.debug("No environment variables loaded from %s", dotenv_path)
    else:
        logging.debug("No .env file found for Baltra SDK environment bootstrap")

    _ENV_INITIALIZED = True


"""
This module loads environment variables and configuration settings for various services and integrations,
including WhatsApp, OpenAI, PostgreSQL, Auth0, and Mixpanel. It also sets up session management
and configures logging for the application.
"""

# Prime environment variables early so Settings sees dotenv values
_load_project_environment()


@dataclass(frozen=True)
class Settings:
    META_GRAPH_VERSION: str = os.getenv("META_GRAPH_VERSION", "v23.0")
    META_BUSINESS_ID: str = os.getenv("META_BUSINESS_ID", "")
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    META_SYSTEM_USER_TOKEN_DEFAULT: str = os.getenv("META_SYSTEM_USER_TOKEN_DEFAULT", "")


settings = Settings()


#Loads all configs required in the application
def load_configurations(app):
    if _AUTHLIB_IMPORT_ERROR is not None or _SESSION_IMPORT_ERROR is not None:
        missing = []
        if _AUTHLIB_IMPORT_ERROR is not None:
            missing.append("authlib")
        if _SESSION_IMPORT_ERROR is not None:
            missing.append("flask-session")
        raise RuntimeError(
            "Missing optional dependencies required for configuration: "
            + ", ".join(missing)
        ) from (_AUTHLIB_IMPORT_ERROR or _SESSION_IMPORT_ERROR)

    _load_project_environment()
    ##Load whatsapp/meta related configs
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["META_APP_SECRET"] = os.getenv("META_APP_SECRET")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["wa_id_ID_employee"] = os.getenv("wa_id_ID_employee")
    app.config["wa_id_ID_owner"] = os.getenv("wa_id_ID_owner")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")

    ##Load OpenAI related configs
    app.config["OPENAI_KEY"] = os.getenv("OPENAI_KEY")
    app.config["OPENAI_KEY_SCREENING"] = os.getenv("OPENAI_KEY_SCREENING")
    
    ##Load VAPI related configs
    app.config["VAPI_PRIVATE_KEY"] = os.getenv("VAPI_PRIVATE_KEY")
    app.config["VAPI_PUBLIC_KEY"] = os.getenv("VAPI_PUBLIC_KEY")
    app.config["VAPI_WEBHOOK_SECRET"] = os.getenv("VAPI_WEBHOOK_SECRET")
    app.config["VAPI_BASE_URL"] = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
    app.config["ELEGIBILITY_ASSISTANT_ID"] = "asst_z2NOTEq3ejCLRFHqwDYyZlh5"
    app.config["REFERENCE_ASSISTANT_ID"] = "asst_1aBo4PksWd6r86RgHiZZNRqq"
    app.config["REFERENCE_CLASSIFIER_ASSISTANT_ID"] = "asst_tkCgZC6MxI2SaPrjIwxPQ1id"
    app.config["POST_SCREENING_ASSISTANT_ID"] = "asst_XxAoptaPYfx6s0yVknvMf7V4"
    app.config["UPDATE_DB_ASSISTANT_ID"] = "asst_LYc1U0ANwkqgmZ7tJcc3nxt5"
    app.config["CANDIDATE_GRADING_ASSISTANT_ID"] = "asst_rDguQlmyOHUtyp2fC74AlCaL"
    app.config["POST_SCREENING_REJECTED_ASSISTANT_ID"] = "asst_LBpXj4Hlg9KMEQvHpqK7tcFS"
    app.config["POST_SCREENING_VERIFIED_ASSISTANT_ID"] = "asst_u110CAf2f3iuW9ySVqv8FBIF"
    app.config["OPENAI_MAX_RUN_DURATION"] = 180 #Max run time allowed in seconds prior to killing a run

    ##Load Postgres related configs
    db_settings = {
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
    }

    database_url = next((os.getenv(key) for key in _DATABASE_URL_KEYS if os.getenv(key)), None)
    if database_url:
        url_settings = _extract_db_config_from_url(database_url)
        db_settings.update({k: v for k, v in url_settings.items() if k.startswith("DB_")})
        if "DATABASE_URL" in url_settings:
            app.config.setdefault("DATABASE_URL", url_settings["DATABASE_URL"])

    for key, value in db_settings.items():
        if value is not None:
            app.config[key] = value

    # Default port if still missing
    app.config.setdefault("DB_PORT", 5432)

    ##Load SQLAlchemy related configs
    sqlalchemy_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if sqlalchemy_uri:
        sqlalchemy_uri = _normalize_database_url(sqlalchemy_uri)
    resolved_sqlalchemy_uri = sqlalchemy_uri or app.config.get("DATABASE_URL")
    if resolved_sqlalchemy_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = resolved_sqlalchemy_uri
        app.config.setdefault("DATABASE_URL", resolved_sqlalchemy_uri)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = None
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    
    # SQLAlchemy Engine Options for connection pooling
    # Based on DB analysis: max_connections=81, superuser_reserved=3, available=78
    # Current usage: ~25 connections, leaving ~53 available
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,           # Conservative persistent connections
        "max_overflow": 15,       # Reasonable burst capacity (total: 23)
        "pool_timeout": 30,       # Standard timeout
        "pool_recycle": 1800,     # 30 minutes (less aggressive than 280s)
        "pool_pre_ping": True,    # Essential for connection health
    }

    ##Load Authentication related configs
    app.config["AUTH_ENABLED"] = os.getenv("AUTH_ENABLED", "True").lower() in ("true", "1", "t")
    app.config["BETTER_AUTH_SECRET"] = os.getenv("BETTER_AUTH_SECRET")
    app.config["NEXT_PUBLIC_BASE_URL"] = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000")
    # Admin dashboard UI base URL for building redirect links
    app.config["ADMIN_DASHBOARD_UI_BASE"] = os.getenv("ADMIN_DASHBOARD_UI_BASE", os.getenv("DASHBOARD_BASE_URL", "https://dashboards.baltra.ai"))
    
    # Ensure SECRET_KEY is properly loaded for JWT tokens
    if not app.secret_key:
        app.secret_key = os.getenv("SECRET_KEY")
        if not app.secret_key:
            raise RuntimeError("SECRET_KEY environment variable is required for authentication")

    ##Load configs related to time thresholds used in the app
    app.config["OLD_MESSAGE_CUTOFF"] = 1440  #Threshold in minutes to determine if a message is too old and should not be answered (fixes random message sending bug). Should be equal to 1440 mins = 1 day. used in app/utils/whatsapp_utils.py
    app.config["REWARDS_CUTOFF"] = 1     #Threshold (in weeks) to trucate the data from the rewards table that is pulled from the database and fed to openAI assistants. used in app/utils/employee_data.py
    app.config["REDEMPTIONS_CUTOFF"] = 60     #Threshold (in days) to trucate the data from the redemptions table that is pulled from the database and fed to openAI assistants. used in app/utils/employee_data.py
    
    #Load configs related to time thresholds used in screening
    app.config["SCREENING_EXPIRATION_DAYS"] = 21 #After how many days a candidate that has a previous interaction is considered a new candidate
    app.config["USE_NEW_SCREENING_FLOW"] = str(os.getenv("USE_NEW_SCREENING_FLOW", "false")).lower() in ("1", "true", "yes")

    ##Load response lag configurations for different types of WhatsApp conversations
    app.config['RESPONSE_LAG'] = 7     #Default response lag for whatsapp conversations (in seconds). Used for screening flow numbers. used in app/views.py
    app.config['FAST_RESPONSE_LAG'] = 0.1  #Fast response lag for employee, owner, and demo numbers (in seconds). used in app/views.py
    app.config['SCREENING_DEMO_WA_ID'] = "723429407513324"     #Demo wa_id number that should have reduced response lag
    # Note: Response lag branches in app/views.py:
    # - wa_id_ID_employee (430838266777981) and wa_id_ID_owner (412795338592474): 0.1 seconds
    # - Demo number (691522037378440): 0.1 seconds  
    # - All other numbers (screening flow): 7 seconds

    #Load credentials for remote connections
    app.config["SERVER_FANTASIAS"] = os.getenv("SERVER_FANTASIAS")
    app.config["UID_FANTASIAS"] = os.getenv("UID_FANTASIAS")
    app.config["PWD_FANTASIAS"] = os.getenv("PWD_FANTASIAS")
    app.config["API_URL_MTWA"] = os.getenv("API_URL_MTWA")
    app.config["USERNAME_MTWA"] = os.getenv("USERNAME_MTWA")
    app.config["PASSWORD_MTWA"] = os.getenv("PASSWORD_MTWA")
    # Tu Identidad NSS webhook secret (used by middleware)
    app.config["TI_WEBHOOK_SECRET"] = os.getenv("TI_WEBHOOK_SECRET")

    ##Load response to Whatsapp processing issue
    app.config["RESPONSE_TO_WHATSAPP_ISSUE"] = "Disculpa tuvimos un problema al procesar tu mensaje. Por favor mandalo de nuevo."
    ##Load environment (for staging it will load staging, for main it will load production)
    app.config["FLASK_ENV"] = os.getenv("FLASK_ENV") #This line makes sure that schedulers only run in production and not in staging. The .env of staging and production have different values for this field

    ##Load Auth0 related configurations. Ensure session configuration is set before OAuth setup
    app.config["AUTH0_DOMAIN"] = os.getenv("AUTH0_DOMAIN")
    app.config["AUTH0_CLIENT_ID"] = os.getenv("AUTH0_CLIENT_ID")
    app.config["AUTH0_CLIENT_SECRET"] = os.getenv("AUTH0_CLIENT_SECRET")
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    Session(app)
    oauth = OAuth(app)
    try:
        auth0 = oauth.register(
            "auth0",
            client_id=app.config["AUTH0_CLIENT_ID"],
            client_secret=app.config["AUTH0_CLIENT_SECRET"],
            api_base_url=f"https://{app.config['AUTH0_DOMAIN']}",
            access_token_url=f"https://{app.config['AUTH0_DOMAIN']}/oauth/token",
            authorize_url=f"https://{app.config['AUTH0_DOMAIN']}/authorize",
            client_kwargs={
                'scope': 'openid profile email',
                'response_type': 'code'
            },
            server_metadata_url = f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration"
        )
        app.config["AUTH0"] = auth0
        logging.info("Auth0 registration successful")
    except Exception as e:
        logging.error(f"Failed to register Auth0: {str(e)}")
        raise

    ## Load Secret key and other Auth0 Configurations
    app.secret_key = os.getenv("SECRET_KEY")
    if not app.secret_key:
        raise RuntimeError("SECRET_KEY is not set. Application cannot start without it.")
    app.config["SESSION_TYPE"] = "filesystem"  # Use "redis" for production
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    
    #Load Mixpanel related configurations
    app.config["MIXPANEL_TOKEN"] = os.getenv("MIXPANEL_TOKEN")

    # Messaging safety: allow routing all outbound WA to a single test number
    app.config["SINGLE_TEST_WA_ID"] = os.getenv("SINGLE_TEST_WA_ID")
    # Scheduler toggle
    app.config["DISABLE_SCHEDULER"] = str(os.getenv("DISABLE_SCHEDULER", "0")).lower() in ("1", "true", "yes")
    
    ##Load AWS S3 related configurations (using IAM roles for authentication)
    app.config["AWS_REGION"] = os.getenv("AWS_REGION", "us-east-2")
    app.config["S3_BUCKET_REPORTS"] = os.getenv("S3_BUCKET_REPORTS", "baltrabucket")
    app.config["S3_BUCKET_SCREENING"] = os.getenv("S3_BUCKET_SCREENING", "screeningbucket")
    
    Session(app)

    # Log WhatsApp configuration
    logging.info("WhatsApp configuration loaded successfully")
    logging.info(f"Employee wa_id: {app.config.get('wa_id_ID_employee')}")
    logging.info(f"Owner wa_id: {app.config.get('wa_id_ID_owner')} (legacy - now used for screening)")
    logging.info("All other wa_id numbers will be routed to screening flow")

def configure_logging():
    """
    Configures logging for the application with multiple handlers, each having different log levels.

    - **Console Handler**:
        Logs messages to `stdout` (the console) with a level of INFO and above. This means only INFO, WARNING, ERROR, and CRITICAL messages will be displayed on the console.

    - **App Log Handler**:
        Logs messages to the file `/home/ec2-user/Amigo_Chamba/app.log` with a level of DEBUG and above. This captures all log messages from DEBUG to CRITICAL, providing a detailed record of application activity.

    - **Error Log Handler**:
        Logs messages to the file `/home/ec2-user/Amigo_Chamba/error.log` with a level of WARNING and above. This ensures that only WARNING, ERROR, and CRITICAL messages are stored here, allowing for focused monitoring of significant issues.

    - **Formatter**:
        All handlers use a consistent log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`. This format includes the timestamp, logger name, log level, and the log message itself.

    - **Root Logger**:
        The root logger is set to capture all logs at the DEBUG level and above, ensuring that all log messages are processed by the handlers. The root logger distributes the logs to the appropriate handler based on the log level.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Root logger captures DEBUG and above

    # Remove existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console handler for INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Console logs INFO and above

    # File handler for app.log (DEBUG and above)
    app_log_handler = logging.FileHandler("app.log")
    app_log_handler.setLevel(logging.DEBUG)  # app.log logs DEBUG and above

    # File handler for error.log (WARNING and ERROR only)
    error_log_handler = logging.FileHandler("error.log")
    error_log_handler.setLevel(logging.WARNING)  # error.log logs WARNING and ERROR only

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Apply the formatter to all handlers
    console_handler.setFormatter(formatter)
    app_log_handler.setFormatter(formatter)
    error_log_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_log_handler)
    root_logger.addHandler(error_log_handler)
def _normalize_database_url(url: str) -> str:
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if scheme.startswith("postgres"):
        base_scheme = scheme.split("+", 1)[0]
        if base_scheme not in {"postgres", "postgresql"}:
            return url
        return f"{base_scheme}://{rest}"
    return url


def _extract_db_config_from_url(database_url: str) -> dict[str, str]:
    normalized_url = _normalize_database_url(database_url)
    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        return {}

    config: dict[str, str] = {}
    if parsed.path:
        config["DB_NAME"] = parsed.path.lstrip("/")
    if parsed.username:
        config["DB_USER"] = parsed.username
    if parsed.password:
        config["DB_PASSWORD"] = parsed.password
    if parsed.hostname:
        config["DB_HOST"] = parsed.hostname
    if parsed.port is not None:
        config["DB_PORT"] = str(parsed.port)

    # Preserve additional query parameters (e.g., sslmode) for later use
    if parsed.query:
        config["DB_OPTIONS"] = parsed.query

    config["DATABASE_URL"] = normalized_url
    return config
