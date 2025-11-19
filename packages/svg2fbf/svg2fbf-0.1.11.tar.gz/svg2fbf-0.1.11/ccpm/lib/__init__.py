"""
CCPM Library Module

Core library functions for project configuration and utilities.
"""

from .project_config import get_config, get_project_name, get_repo_owner

__all__ = [
    "get_config",
    "get_project_name",
    "get_repo_owner",
]
