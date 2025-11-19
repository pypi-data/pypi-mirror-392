"""Backward compatibility module for parsers.

This module provides backward compatibility for the old parsers.py module.
The actual implementations have been moved to pobapi.parsers package.
"""

import warnings

# Re-export for backward compatibility
from pobapi.parsers import (
    BuildInfoParser,
    DefaultBuildParser,
    ItemsParser,
    SkillsParser,
    TreesParser,
)

warnings.warn(
    "pobapi.parsers_compat is deprecated. Import from pobapi.parsers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BuildInfoParser",
    "DefaultBuildParser",
    "ItemsParser",
    "SkillsParser",
    "TreesParser",
]
