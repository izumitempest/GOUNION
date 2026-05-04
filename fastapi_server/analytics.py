import os
from posthog import Posthog
from typing import Optional, Dict, Any

POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

# Initialize Posthog lazily
posthog = None
if POSTHOG_API_KEY:
    posthog = Posthog(POSTHOG_API_KEY, host=POSTHOG_HOST)

def track_event(user_id: str, event_name: str, properties: Optional[Dict[str, Any]] = None):
    """
    Sends an event to PostHog for product analytics.
    """
    if posthog:
        try:
            posthog.capture(user_id, event_name, properties or {})
        except Exception as e:
            # We don't want analytics to crash the main app
            print(f"[analytics] Failed to track event {event_name}: {e}")

def identify_user(user_id: str, properties: Dict[str, Any]):
    """
    Identifies a user with specific traits (e.g. university, role).
    """
    if posthog:
        try:
            posthog.identify(user_id, properties)
        except Exception as e:
            print(f"[analytics] Failed to identify user {user_id}: {e}")
