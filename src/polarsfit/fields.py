"""
FIT Protocol field mappings using the official Garmin FIT SDK.

This module provides field mapping functionality using the official Garmin FIT SDK
instead of manual field definitions. This ensures that field mappings stay up-to-date
with the official FIT protocol specification.
"""

from enum import Enum
from typing import Dict, List

try:
    from garmin_fit_sdk import Profile
except ImportError as exc:
    raise ImportError(
        "The garmin-fit-sdk package is required but not installed. "
        "Install it with: pip install garmin-fit-sdk"
    ) from exc


class MessageType(str, Enum):
    """Enumeration of FIT message types."""

    RECORD = "record"
    SESSION = "session"
    LAP = "lap"
    ACTIVITY = "activity"
    FILE_ID = "file_id"
    EVENT = "event"
    DEVICE_INFO = "device_info"
    HRV = "hrv"


# Create a mapping from message type names to mesg_num values from the SDK
MESSAGE_TYPE_MAP = {
    MessageType.RECORD: Profile["mesg_num"]["RECORD"],
    MessageType.SESSION: Profile["mesg_num"]["SESSION"],
    MessageType.LAP: Profile["mesg_num"]["LAP"],
    MessageType.ACTIVITY: Profile["mesg_num"]["ACTIVITY"],
    MessageType.FILE_ID: Profile["mesg_num"]["FILE_ID"],
    MessageType.EVENT: Profile["mesg_num"]["EVENT"],
    MessageType.DEVICE_INFO: Profile["mesg_num"]["DEVICE_INFO"],
    MessageType.HRV: Profile["mesg_num"]["HRV"],
}


def get_field_mapping(message_type: MessageType) -> Dict[int, str]:
    """
    Get field mapping for a specific message type using the official Garmin FIT SDK.

    Parameters
    ----------
    message_type : MessageType
        The message type to get field mappings for

    Returns
    -------
    Dict[int, str]
        Dictionary mapping field numbers to field names

    Raises
    ------
    ValueError
        If the message type is not supported
    """
    if message_type not in MESSAGE_TYPE_MAP:
        raise ValueError(f"Unsupported message type: {message_type}")

    mesg_num = MESSAGE_TYPE_MAP[message_type]

    # Get the message definition from the SDK Profile
    try:
        messages = Profile["messages"]
        if mesg_num not in messages:
            return {}

        message_def = messages[mesg_num]
        if "fields" not in message_def:
            return {}

        # Extract field mappings
        field_mapping = {}
        for field_num, field_info in message_def["fields"].items():
            if isinstance(field_info, dict) and "name" in field_info:
                field_mapping[int(field_num)] = field_info["name"]

        return field_mapping

    except (KeyError, TypeError, ValueError):
        # Return empty dict if there's any issue accessing the SDK data
        return {}


def get_available_message_types() -> List[str]:
    """
    Get list of all available message types.

    Returns
    -------
    List[str]
        List of message type names
    """
    return [msg_type.value for msg_type in MessageType]


# Cache for legacy field mappings to avoid repeated SDK lookups
_cached_legacy_fields: Dict[MessageType, Dict[str, str]] = {}


def _get_cached_legacy_fields(message_type: MessageType) -> Dict[str, str]:
    """Get cached legacy field mapping for a message type."""
    if message_type not in _cached_legacy_fields:
        field_mapping = get_field_mapping(message_type)
        # Convert to legacy format: field_number -> field_name
        legacy_mapping = {f"field_{k}": v for k, v in field_mapping.items()}
        _cached_legacy_fields[message_type] = legacy_mapping

    return _cached_legacy_fields[message_type]


# Legacy field mappings for backward compatibility
def get_record_fields() -> Dict[str, str]:
    """Get RECORD field mappings in legacy format."""
    return _get_cached_legacy_fields(MessageType.RECORD)


def get_session_fields() -> Dict[str, str]:
    """Get SESSION field mappings in legacy format."""
    return _get_cached_legacy_fields(MessageType.SESSION)


def get_lap_fields() -> Dict[str, str]:
    """Get LAP field mappings in legacy format."""
    return _get_cached_legacy_fields(MessageType.LAP)


def get_activity_fields() -> Dict[str, str]:
    """Get ACTIVITY field mappings in legacy format."""
    return _get_cached_legacy_fields(MessageType.ACTIVITY)


# Create the legacy field mappings as module-level constants for backward compatibility
try:
    RECORD_FIELDS = get_record_fields()
    SESSION_FIELDS = get_session_fields()
    LAP_FIELDS = get_lap_fields()
    ACTIVITY_FIELDS = get_activity_fields()
except Exception:
    # Fallback to empty dicts if SDK not available at import time
    RECORD_FIELDS = {}
    SESSION_FIELDS = {}
    LAP_FIELDS = {}
    ACTIVITY_FIELDS = {}
