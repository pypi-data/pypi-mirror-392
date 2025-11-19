from __future__ import annotations
import hmac
import hashlib
import logging
from typing import Callable
from flask import request, jsonify, current_app


def require_webhook_secret(secret_config_key: str = "TI_WEBHOOK_SECRET"):
    """Middleware decorator that enforces a shared secret or HMAC signature.

    Accepts either of these headers:
      - X-Webhook-Secret: exact match with baltra_sdk.shared.config[secret_config_key]
      - X-Signature: hex-encoded HMAC-SHA256 computed over raw body with the secret
    """

    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            try:
                secret = (current_app.config.get(secret_config_key) or "").strip()
            except Exception:
                secret = ""

            provided = (request.headers.get("X-Webhook-Secret") or "").strip()
            signature = (request.headers.get("X-Signature") or "").strip()

            # Compute HMAC if signature present
            body = request.get_data() or b""
            expected_sig = (
                hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest() if secret else None
            )

            if not secret:
                logging.warning("Webhook secret not configured; rejecting for safety")
                return jsonify({"completed": False, "error": "Webhook not configured"}), 401

            if provided and hmac.compare_digest(provided, secret):
                return fn(*args, **kwargs)

            if signature and expected_sig and hmac.compare_digest(signature, expected_sig):
                return fn(*args, **kwargs)

            logging.warning("Invalid or missing webhook authentication headers")
            return jsonify({"completed": False, "error": "Unauthorized"}), 401

        # Preserve function identity for Flask
        wrapper.__name__ = getattr(fn, "__name__", "wrapped_webhook")
        return wrapper

    return decorator

