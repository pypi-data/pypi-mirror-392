import os


def check_agent_groups_api_key():
    """
    Check if the AgentGroups API key is set.

    Returns:
        str: The value of the AGENT_GROUPS_API_KEY environment variable.

    Raises:
        ValueError: If the AGENT_GROUPS_API_KEY environment variable is not set.
    """
    if os.getenv("AGENT_GROUPS_API_KEY") is None:
        raise ValueError(
            "AgentGroups API key is not set. Please set the AGENT_GROUPS_API_KEY environment variable. "
            "You can get your key here: https://agent_groups.world/platform/api-keys"
        )
    return os.getenv("AGENT_GROUPS_API_KEY")
