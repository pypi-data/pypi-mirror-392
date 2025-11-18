"""
Type definitions for the agent_groups package.

This module contains common type definitions used across the agent_groups package
to avoid circular import issues.
"""

from typing import Literal

# Return types for agent creation functions
ReturnTypes = Literal[
    "auto", "agent_group", "agents", "both", "tasks", "run_agent_group"
]
