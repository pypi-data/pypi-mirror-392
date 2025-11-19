from flask import current_app, session, request
from mixpanel import Mixpanel
import logging
from functools import wraps

"""
Mixpanel integration for tracking events in the application.

This module provides functions to initialize and interact with Mixpanel, including:
- `get_mixpanel`: Initializes and returns the Mixpanel client using the Flask app configuration.
- `track_event`: Tracks an event in Mixpanel.
"""

def get_mixpanel():
    """
    Initialize and return the Mixpanel client using the Flask app config.
    """
    project_token = current_app.config.get("MIXPANEL_TOKEN")
    if not project_token:
        raise ValueError("Mixpanel token is missing in the configuration.")
    logging.info("Successfully connected to Mixpanel")
    return Mixpanel(project_token)

def track_event(distinct_id, event_name, properties=None):
    """
    Track an event in Mixpanel using the SDK.
    """
    mp = get_mixpanel()
    properties = properties or {}
    mp.track(distinct_id, event_name, properties)
    logging.info(f"Event '{event_name}' tracked successfully")



