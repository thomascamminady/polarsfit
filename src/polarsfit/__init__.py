"""
.. include:: ../../README.md

   :start-line: 1
"""

import polars as pl

from polarsfit._internal import get_message_types as _get_message_types
from polarsfit._internal import read_data as _read_data
from polarsfit._internal import read_recordmesgs as _read_recordmesgs
from polarsfit.fields import (
    MessageType,
    get_available_message_types,
    get_field_mapping,
)


def read_recordmesgs(
    file_path: str,
    field_mapping: dict[str, str] | None = None,
    *,
    apply_default_mapping: bool = True,
) -> pl.DataFrame:
    """
    Read record messages from a FIT file.

    Parameters
    ----------
    file_path : str
        Path to the FIT file.
    field_mapping : dict[str, str] | None, optional
        Custom mapping from field numbers to field names.
        Format: {"field_123": "custom_name"}
    apply_default_mapping : bool, default True
        Whether to apply the default FIT protocol field mapping.

    Returns
    -------
    polars.DataFrame
        DataFrame containing the record messages with mapped field names.

    Examples
    --------
    >>> # Read with default field mapping
    >>> df = polarsfit.read_recordmesgs("workout.fit")
    >>>
    >>> # Read with custom field mapping
    >>> custom_mapping = {"field_123": "my_custom_field"}
    >>> df = polarsfit.read_recordmesgs("workout.fit", field_mapping=custom_mapping)
    >>>
    >>> # Read without any field mapping (raw field numbers)
    >>> df = polarsfit.read_recordmesgs("workout.fit", apply_default_mapping=False)
    """
    # Get raw data from Rust (with field_X column names)
    df = _read_recordmesgs(file_path)

    # Apply field mapping by renaming columns
    if apply_default_mapping or field_mapping:
        # Build field mapping
        final_mapping = {}

        if apply_default_mapping:
            # Apply default RECORD field mapping (lazy import to avoid circular import)
            from polarsfit.fields import RECORD_FIELDS

            # RECORD_FIELDS already has keys in format field_X -> field_name
            final_mapping.update(RECORD_FIELDS)

        if field_mapping:
            # Apply custom mapping (overrides default)
            final_mapping.update(field_mapping)

        # Rename columns that have mappings
        if final_mapping:
            # Only rename columns that exist in the DataFrame
            existing_columns = set(df.columns)
            rename_mapping = {
                col: new_name
                for col, new_name in final_mapping.items()
                if col in existing_columns
            }
            if rename_mapping:
                df = df.rename(rename_mapping)

    return df


def get_message_types(file_path: str) -> list[str]:
    """
    Get all message types available in a FIT file.

    Parameters
    ----------
    file_path : str
        Path to the FIT file.

    Returns
    -------
    list[str]
        List of message type names found in the file.

    Examples
    --------
    >>> message_types = polarsfit.get_message_types("workout.fit")
    >>> print(message_types)
    ['record', 'session', 'lap', 'file_id', 'event']
    """
    return _get_message_types(file_path)


def read_data(
    file_path: str,
    message_type: str,
    field_mapping: dict[str, str] | None = None,
    *,
    apply_default_mapping: bool = True,
) -> pl.DataFrame:
    """
    Read messages of a specific type from a FIT file.

    Parameters
    ----------
    file_path : str
        Path to the FIT file.
    message_type : str
        Type of messages to read (e.g., 'record', 'session', 'lap').
    field_mapping : dict[str, str] | None, optional
        Custom mapping from field numbers to field names.
        Format: {"field_123": "custom_name"}
    apply_default_mapping : bool, default True
        Whether to apply the default FIT protocol field mapping for this message type.

    Returns
    -------
    polars.DataFrame
        DataFrame containing the specified message type with mapped field names.

    Examples
    --------
    >>> # Read session data with default mapping
    >>> sessions = polarsfit.read_data("workout.fit", "session")
    >>>
    >>> # Read lap data with custom mapping
    >>> custom_mapping = {"field_123": "my_custom_field"}
    >>> laps = polarsfit.read_data("workout.fit", "lap", field_mapping=custom_mapping)
    >>>
    >>> # Get available message types first
    >>> types = polarsfit.get_message_types("workout.fit")
    >>> for msg_type in types:
    ...     data = polarsfit.read_data("workout.fit", msg_type)
    ...     print(f"{msg_type}: {data.shape}")
    """
    # Build field mapping
    final_mapping = {}

    if apply_default_mapping:
        # Try to get default mapping for this message type
        try:
            msg_type_enum = getattr(MessageType, message_type.upper())
            default_fields = get_field_mapping(msg_type_enum)
            default_mapping = {
                f"field_{k}": v for k, v in default_fields.items()
            }
            final_mapping.update(default_mapping)
        except (AttributeError, KeyError):
            # No default mapping available for this message type
            pass

    if field_mapping:
        # Apply custom mapping (overrides default)
        final_mapping.update(field_mapping)

    # Convert to format expected by Rust, or pass None if empty
    rust_mapping = final_mapping if final_mapping else None

    return _read_data(file_path, message_type, rust_mapping)


def scan_recordmesgs(
    file_path: str,
    field_mapping: dict[str, str] | None = None,
) -> pl.LazyFrame:
    """
    Create a lazy scanner for record messages from a FIT file.

    This function returns a LazyFrame that defers file reading until operations
    are actually executed. The file is only read when you call .collect(), .head(),
    or other materializing operations.

    Args:
        file_path: Path to the FIT file
        field_mapping: Optional mapping of field names to rename columns

    Returns
    -------
        A Polars LazyFrame that will read the record messages when materialized

    Example:
        >>> lf = scan_recordmesgs("activity.fit")
        >>> # No file reading has occurred yet
        >>> result = lf.filter(pl.col("heart_rate") > 150).collect()  # File read here
    """
    return _create_lazy_scanner(file_path, "record", field_mapping)


def scan_data(
    file_path: str,
    message_type: str,
    field_mapping: dict[str, str] | None = None,
) -> pl.LazyFrame:
    """
    Create a lazy scanner for specific message type data from a FIT file.

    This function returns a LazyFrame that defers file reading until operations
    are actually executed. The file is only read when you call .collect(), .head(),
    or other materializing operations.

    Args:
        file_path: Path to the FIT file
        message_type: Type of message to scan (e.g., "record", "session", "lap")
        field_mapping: Optional mapping of field names to rename columns

    Returns
    -------
        A Polars LazyFrame that will read the specified message type data when materialized

    Example:
        >>> lf = scan_data("activity.fit", "record")
        >>> # No file reading has occurred yet
        >>> result = lf.select(["timestamp", "heart_rate", "power"]).collect()  # File read here
    """
    return _create_lazy_scanner(file_path, message_type, field_mapping)


def _create_lazy_scanner(file_path: str, message_type: str, field_mapping: dict[str, str] | None = None) -> pl.LazyFrame:
    """
    Create a truly lazy scanner that defers file reading until materialization.

    This works by creating a LazyFrame from a function that reads the data only when called.
    """
    # We create a function that will be called when the LazyFrame is materialized
    def read_fit_data():
        if message_type == "record":
            return read_recordmesgs(file_path, field_mapping)
        else:
            return read_data(file_path, message_type, field_mapping)

    # Create a small dummy DataFrame to start the lazy chain
    # The actual reading happens in the map operation
    dummy_df = pl.DataFrame({"_temp": [1]})

    return dummy_df.lazy().map_batches(
        lambda _: read_fit_data()
    )


__all__ = [
    "read_recordmesgs",
    "get_message_types",
    "read_data",
    "scan_recordmesgs",
    "scan_data",
    "MessageType",
    "get_field_mapping",
    "get_available_message_types",
]


def __getattr__(name: str):
    """Lazy import for RECORD_FIELDS and other field constants to avoid circular imports."""
    if name == "RECORD_FIELDS":
        from polarsfit.fields import RECORD_FIELDS

        return RECORD_FIELDS
    elif name == "SESSION_FIELDS":
        from polarsfit.fields import SESSION_FIELDS

        return SESSION_FIELDS
    elif name == "LAP_FIELDS":
        from polarsfit.fields import LAP_FIELDS

        return LAP_FIELDS
    elif name == "ACTIVITY_FIELDS":
        from polarsfit.fields import ACTIVITY_FIELDS

        return ACTIVITY_FIELDS
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
