from functools import wraps
import hashlib
import hmac
import logging
from typing import Optional

from flask import current_app, jsonify, request, g

from baltra_sdk.infra.di.container import get_auth_repository

"""
Security helpers for webhook verification and JWT-based authentication.
"""


def validate_signature(payload: str, signature: str) -> bool:
    """Validate incoming payload HMAC using META_APP_SECRET."""
    expected_signature = hmac.new(
        bytes(current_app.config["META_APP_SECRET"], "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if hmac.compare_digest(expected_signature, signature):
        logging.info("[Account: PRIMARY] Signature validation successful")
        return True

    logging.warning("[Account: PRIMARY] Signature validation failed")
    return False


def signature_required(fn):
    """Decorator enforcing Meta webhook signature validation."""

    @wraps(fn)
    def decorated_function(*args, **kwargs):
        flask_env = current_app.config.get("ENV") or current_app.config.get("FLASK_ENV")
        if (flask_env or "").lower() == "development":
            logging.debug("Skipping Meta signature validation in development environment")
            return fn(*args, **kwargs)

        signature_header = request.headers.get("X-Hub-Signature-256", "")
        signature = signature_header[7:] if signature_header.startswith("sha256=") else ""
        if not validate_signature(request.data.decode("utf-8"), signature):
            logging.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
        return fn(*args, **kwargs)

    return decorated_function


def _authenticate_request(required_role: Optional[str] = None):
    """Validate JWT from Authorization header and enforce optional role membership."""
    if not current_app.config.get("AUTH_ENABLED", True):
        logging.warning("Authentication disabled via AUTH_ENABLED=False. Bypassing security checks.")
        return None

    logging.info(
        "Auth Flow: _authenticate_request called for path %s. Required role: %s",
        request.path,
        required_role or "any authenticated user",
    )

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logging.debug("Auth Flow: Authorization header missing.")
        return jsonify({"message": "Missing Authorization Header"}), 401

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        logging.debug("Auth Flow: Invalid token format (IndexError).")
        return jsonify({"message": "Invalid token format. Expected 'Bearer <token>'"}), 401

    auth_repo = get_auth_repository()
    logging.debug("Auth Flow: Calling AuthRepository.get_user_from_token...")
    token_payload = auth_repo.get_user_from_token(token)

    if not token_payload:
        logging.debug("Auth Flow: Token validation failed or expired.")
        return jsonify({"message": "Invalid or expired token"}), 401

    g.user = token_payload
    logging.debug("Auth Flow: User data attached to g.user: %s", g.user.get("email", "N/A"))

    # Optional company scope enforcement for GET routes
    if request.method == "GET":
        company_id = (getattr(request, "view_args", None) or {}).get("company_id")
        if company_id is not None:
            companies_claim = g.user.get("custom:companies_ids")
            if isinstance(companies_claim, str):
                try:
                    companies_claim = eval(companies_claim)  # noqa: S307 - legacy payload
                except Exception:  # pragma: no cover - defensive
                    companies_claim = []
            if isinstance(companies_claim, list):
                allowed = {int(c) for c in companies_claim if str(c).isdigit()}
                if int(company_id) not in allowed:
                    logging.warning(
                        "Auth Flow: company_id %s not allowed for user %s", company_id, g.user.get("email")
                    )
                    return jsonify({"message": "Forbidden. Company access denied."}), 403

    if required_role:
        roles = g.user.get("cognito:groups") or g.user.get("custom:roles") or []
        if isinstance(roles, str):
            roles = [role.strip() for role in roles.split(",") if role.strip()]
        if required_role not in roles:
            logging.warning(
                "Auth Flow: User %s missing required role %s (roles=%s)",
                g.user.get("email"),
                required_role,
                roles,
            )
            return jsonify({"message": "Forbidden. Insufficient permissions."}), 403

    return None


def auth_required(role: Optional[str] = None):
    """Decorator enforcing JWT authentication (and optional role)."""

    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            if request.method == "OPTIONS":
                logging.debug("Auth Flow: OPTIONS request for %s returning 204 preflight.", request.path)
                return "", 204

            response = _authenticate_request(role)
            if response:
                return response
            return fn(*args, **kwargs)

        return decorated_function

    return decorator


__all__ = ["validate_signature", "signature_required", "_authenticate_request", "auth_required"]
