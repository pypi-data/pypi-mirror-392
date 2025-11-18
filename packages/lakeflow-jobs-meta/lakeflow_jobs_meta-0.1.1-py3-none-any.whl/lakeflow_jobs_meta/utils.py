"""Utility functions for the Lakeflow Jobs Meta framework"""

import re
from typing import Optional, Dict, Any


def sanitize_task_key(task_key: str) -> str:
    """Sanitize task_key to create a valid task key.

    Args:
        task_key: The task identifier

    Returns:
        Sanitized task key safe for use in Databricks job definitions
    """
    original = str(task_key)
    # Check if original starts with non-alphanumeric and non-underscore
    starts_with_invalid = original and not original[0].isalnum() and original[0] != "_"
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", original)
    # Remove consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Ensure it doesn't start or end with underscore
    sanitized = sanitized.strip("_")
    
    # If original started with invalid char (not underscore), prepend "task_"
    if starts_with_invalid and sanitized:
        sanitized = "task_" + sanitized
    
    return sanitized


def validate_notebook_path(notebook_path: str) -> bool:
    """Validate notebook path format (non-blocking validation).

    This is a lightweight validation that checks path format.
    Does not verify actual file existence to avoid blocking execution.

    Args:
        notebook_path: Path to the notebook

    Returns:
        True if validation passes (always returns True - non-blocking)
    """
    if notebook_path and not notebook_path.startswith(("/pipelines/", "/frameworks/", "/Workspace/")):
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Using custom notebook path: {notebook_path}")
    return True
