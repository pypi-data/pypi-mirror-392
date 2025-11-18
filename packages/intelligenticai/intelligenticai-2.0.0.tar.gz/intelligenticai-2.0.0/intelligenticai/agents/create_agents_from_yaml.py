import os
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from pydantic import (
    BaseModel,
    Extra,
    Field,
    field_validator,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from intelligenticai.structs.agent import Agent
from intelligenticai.structs.agent_group_router import AgentGroupRouter
from intelligenticai.utils.types import ReturnTypes
from intelligenticai.utils.loguru_logger import initialize_logger

logger = initialize_logger(log_folder="create_agents_from_yaml")


class AgentConfig(BaseModel):
    """Configuration model for creating agents with support for custom kwargs."""

    agent_name: str
    system_prompt: str
    model_name: Optional[str] = None
    max_loops: int = Field(default=1, ge=1)
    autosave: bool = True
    dashboard: bool = False
    verbose: bool = False
    dynamic_temperature_enabled: bool = False
    saved_state_path: Optional[str] = None
    user_name: str = "default_user"
    retry_attempts: int = Field(default=3, ge=1)
    context_length: int = Field(default=100000, ge=1000)
    return_step_meta: bool = False
    output_type: str = "str"
    auto_generate_prompt: bool = False
    artifacts_on: bool = False
    artifacts_file_extension: str = ".md"
    artifacts_output_path: str = ""

    # Allow arbitrary additional fields for custom agent parameters
    class Config:
        extra = "allow"

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, v):
        """Validate that system prompt is a non-empty string."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError(
                "System prompt must be a non-empty string"
            )
        return v


class AgentGroupConfig(BaseModel):
    """Configuration model for creating agent_group routers with support for custom kwargs."""

    name: str
    description: str
    max_loops: int = Field(default=1, ge=1)
    agent_group_type: str
    task: Optional[str] = None
    flow: Optional[Dict] = None
    autosave: bool = True
    return_json: bool = False
    rules: str = ""

    # Allow arbitrary additional fields for custom agent_group parameters
    class Config:
        extra = Extra.allow


class YAMLConfig(BaseModel):
    """Main configuration model for the YAML file."""

    agents: List[AgentConfig] = Field(..., min_length=1)
    agent_group_architecture: Optional[AgentGroupConfig] = None


def load_yaml_safely(
    yaml_file: str = None, yaml_string: str = None
) -> Dict:
    """Safely load and validate YAML configuration using Pydantic."""
    try:
        if yaml_string:
            config_dict = yaml.safe_load(yaml_string)
        elif yaml_file:
            if not os.path.exists(yaml_file):
                raise FileNotFoundError(
                    f"YAML file {yaml_file} not found."
                )
            with open(yaml_file, "r") as file:
                config_dict = yaml.safe_load(file)
        else:
            raise ValueError(
                "Either yaml_file or yaml_string must be provided"
            )

        # Validate using Pydantic
        YAMLConfig(**config_dict)
        return config_dict
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error validating configuration: {str(e)}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: logger.info(
        f"Retrying after error: {retry_state.outcome.exception()}"
    ),
)
def create_agent_with_retry(agent_config: Dict) -> Agent:
    """Create an agent with retry logic for handling transient failures."""
    try:
        validated_config = AgentConfig(**agent_config)

        # Extract standard Agent parameters
        standard_params = {
            "agent_name": validated_config.agent_name,
            "system_prompt": validated_config.system_prompt,
            "max_loops": validated_config.max_loops,
            "model_name": validated_config.model_name,
            "autosave": validated_config.autosave,
            "dashboard": validated_config.dashboard,
            "verbose": validated_config.verbose,
            "dynamic_temperature_enabled": validated_config.dynamic_temperature_enabled,
            "saved_state_path": validated_config.saved_state_path,
            "user_name": validated_config.user_name,
            "retry_attempts": validated_config.retry_attempts,
            "context_length": validated_config.context_length,
            "return_step_meta": validated_config.return_step_meta,
            "output_type": validated_config.output_type,
            "auto_generate_prompt": validated_config.auto_generate_prompt,
            "artifacts_on": validated_config.artifacts_on,
            "artifacts_file_extension": validated_config.artifacts_file_extension,
            "artifacts_output_path": validated_config.artifacts_output_path,
        }

        # Extract any additional custom parameters
        custom_params = {}
        for key, value in agent_config.items():
            if key not in standard_params and key != "agent_name":
                custom_params[key] = value

        # Create agent with standard and custom parameters
        agent = Agent(**standard_params, **custom_params)
        return agent
    except Exception as e:
        logger.error(
            f"Error creating agent {agent_config.get('agent_name', 'unknown')}: {str(e)} Traceback: {traceback.format_exc()}"
        )
        raise


def create_agents_from_yaml(
    yaml_file: str = "agents.yaml",
    yaml_string: str = None,
    return_type: ReturnTypes = "auto",
) -> Union[
    AgentGroupRouter,
    Agent,
    List[Agent],
    Tuple[Union[AgentGroupRouter, Agent], List[Agent]],
    List[Dict[str, Any]],
]:
    """
    Create agents and/or AgentGroupRouter based on configurations defined in a YAML file or string.

    This function now supports custom parameters for both Agent and AgentGroupRouter creation.
    Any additional fields in your YAML configuration will be passed through as kwargs.

    Args:
        yaml_file: Path to YAML configuration file
        yaml_string: YAML configuration as a string (alternative to yaml_file)
        return_type: Type of return value ("auto", "agent_group", "agents", "both", "tasks", "run_agent_group")

    Returns:
        Depending on return_type and configuration, returns:
        - Single Agent (if only one agent and return_type in ["auto", "agent_group", "agents"])
        - List of Agents (if multiple agents and return_type in ["auto", "agent_group", "agents"])
        - AgentGroupRouter (if return_type in ["auto", "agent_group"] and agent_group_architecture defined)
        - Tuple of (AgentGroupRouter, List[Agent]) (if return_type == "both")
        - Task results (if return_type == "tasks")
        - AgentGroup execution result (if return_type == "run_agent_group")

    Example YAML with custom parameters:
        agents:
          - agent_name: "CustomAgent"
            system_prompt: "You are a helpful assistant"
            custom_param1: "value1"
            custom_param2: 42
            nested_config:
              key: "value"

        agent_group_architecture:
          name: "CustomAgentGroup"
          description: "A custom agent_group"
          agent_group_type: "SequentialWorkflow"
          custom_agent_group_param: "agent_group_value"
          another_param: 123
    """
    agents = []
    task_results = []
    agent_group_router = None

    try:
        logger.info("Starting agent creation process...")

        # Load and validate configuration
        if yaml_file:
            logger.info(f"Loading configuration from {yaml_file}")
        config = load_yaml_safely(yaml_file, yaml_string)

        if not config.get("agents"):
            raise ValueError(
                "No agents defined in the YAML configuration. "
                "Please add at least one agent under the 'agents' section."
            )

        logger.info(
            f"Found {len(config['agents'])} agent(s) to create"
        )

        # Create agents with retry logic
        for idx, agent_config in enumerate(config["agents"], 1):
            if not agent_config.get("agent_name"):
                agent_config["agent_name"] = f"Agent_{idx}"

            logger.info(
                f"Creating agent {idx}/{len(config['agents'])}: {agent_config['agent_name']}"
            )

            agent = create_agent_with_retry(agent_config)
            logger.info(
                f"Agent {agent_config['agent_name']} created successfully."
            )
            agents.append(agent)

        logger.info(f"Successfully created {len(agents)} agent(s)")

        # Create AgentGroupRouter if specified
        if "agent_group_architecture" in config:
            logger.info("Setting up agent_group architecture...")
            try:
                if not isinstance(config["agent_group_architecture"], dict):
                    raise ValueError(
                        "agent_group_architecture must be a dictionary containing agent_group configuration"
                    )

                required_fields = {
                    "name",
                    "description",
                    "agent_group_type",
                }
                missing_fields = required_fields - set(
                    config["agent_group_architecture"].keys()
                )
                if missing_fields:
                    raise ValueError(
                        f"AgentGroupRouter creation failed: Missing required fields in agent_group_architecture: {', '.join(missing_fields)}"
                    )

                agent_group_config = AgentGroupConfig(
                    **config["agent_group_architecture"]
                )

                logger.info(
                    f"Creating AgentGroupRouter with type: {agent_group_config.agent_group_type}"
                )

                # Extract standard AgentGroupRouter parameters
                standard_agent_group_params = {
                    "name": agent_group_config.name,
                    "description": agent_group_config.description,
                    "max_loops": agent_group_config.max_loops,
                    "agents": agents,
                    "agent_group_type": agent_group_config.agent_group_type,
                    "task": agent_group_config.task,
                    "flow": agent_group_config.flow,
                    "autosave": agent_group_config.autosave,
                    "return_json": agent_group_config.return_json,
                    "rules": agent_group_config.rules,
                }

                # Extract any additional custom parameters for AgentGroupRouter
                custom_agent_group_params = {}
                for key, value in config[
                    "agent_group_architecture"
                ].items():
                    if key not in standard_agent_group_params:
                        custom_agent_group_params[key] = value

                # Create AgentGroupRouter with standard and custom parameters
                agent_group_router = AgentGroupRouter(
                    **standard_agent_group_params, **custom_agent_group_params
                )

                logger.info(
                    f"AgentGroupRouter '{agent_group_config.name}' created successfully."
                )
            except Exception as e:
                logger.error(f"Error creating AgentGroupRouter: {str(e)}")
                if "agent_group_type" in str(e) and "valid_types" in str(e):
                    raise ValueError(
                        "Invalid agent_group_type. Must be one of: SequentialWorkflow, ConcurrentWorkflow, "
                        "AgentRearrange, MixtureOfAgents, or auto"
                    )
                raise ValueError(
                    f"Failed to create AgentGroupRouter: {str(e)}. Make sure your YAML file "
                    "has a valid agent_group_architecture section with required fields."
                )

        if return_type not in ReturnTypes:
            raise ValueError(
                f"Invalid return_type. Must be one of: {ReturnTypes}"
            )

        logger.info(f"Processing with return type: {return_type}")

        if return_type in ("run_agent_group", "agent_group"):
            if not agent_group_router:
                if "agent_group_architecture" not in config:
                    raise ValueError(
                        "Cannot run agent_group: No agent_group_architecture section found in YAML configuration.\n"
                        "Please add a agent_group_architecture section with:\n"
                        "  - name: your_agent_group_name\n"
                        "  - description: your_agent_group_description\n"
                        "  - agent_group_type: one of [SequentialWorkflow, ConcurrentWorkflow, AgentRearrange, MixtureOfAgents, auto]\n"
                        "  - task: your_task_description"
                    )
                raise ValueError(
                    "Cannot run agent_group: AgentGroupRouter creation failed. Check the previous error messages."
                )
            try:
                if not config["agent_group_architecture"].get("task"):
                    raise ValueError(
                        "No task specified in agent_group_architecture. Please add a 'task' field "
                        "to define what the agent_group should do."
                    )
                logger.info(
                    f"Running agent_group with task: {config['agent_group_architecture']['task']}"
                )
                return agent_group_router.run(
                    config["agent_group_architecture"]["task"]
                )
            except Exception as e:
                logger.error(f"Error running AgentGroupRouter: {str(e)}")
                raise

        # Return appropriate type based on configuration
        if return_type == "auto":
            result = (
                agent_group_router
                if agent_group_router
                else (agents[0] if len(agents) == 1 else agents)
            )
        elif return_type == "agent_group":
            result = (
                agent_group_router
                if agent_group_router
                else (agents[0] if len(agents) == 1 else agents)
            )
        elif return_type == "agents":
            result = agents[0] if len(agents) == 1 else agents
        elif return_type == "both":
            result = (
                (
                    agent_group_router
                    if agent_group_router
                    else agents[0] if len(agents) == 1 else agents
                ),
                agents,
            )
        elif return_type == "tasks":
            result = task_results

        logger.info("Process completed successfully")
        return result

    except Exception as e:
        logger.error(
            f"Critical error in create_agents_from_yaml: {str(e)}\n"
            f"Please check your YAML configuration and try again. Traceback: {traceback.format_exc()}"
        )
        raise
