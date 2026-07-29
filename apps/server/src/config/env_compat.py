"""Helpers to rename environment variables without breaking existing deployments.

Reads the canonical (new) name first; if unset, falls back to the deprecated
(old) name and logs a warning so the deploy layer can migrate at its own pace.
"""

import os
from typing import overload

from src.logger import logger


@overload
def env_with_deprecated_fallback(new_key: str, old_key: str, default: str) -> str: ...
@overload
def env_with_deprecated_fallback(new_key: str, old_key: str, default: None = None) -> str | None: ...
def env_with_deprecated_fallback(new_key: str, old_key: str, default: str | None = None) -> str | None:
    value = os.environ.get(new_key)
    if value is not None:
        return value

    old_value = os.environ.get(old_key)
    if old_value is not None:
        logger.warning("Environment variable %s is deprecated, use %s instead.", old_key, new_key)
        return old_value

    return default
