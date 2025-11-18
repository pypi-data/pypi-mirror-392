import concurrent.futures
import json
import os
import traceback
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from intelligenticai.prompts.multi_agent_collab_prompt import (
    MULTI_AGENT_COLLAB_PROMPT_TWO,
)
from intelligenticai.structs.agent import Agent
from intelligenticai.structs.agent_rearrange import AgentRearrange
from intelligenticai.structs.batched_grid_workflow import BatchedGridWorkflow
from intelligenticai.structs.concurrent_workflow import ConcurrentWorkflow
from intelligenticai.structs.council_as_judge import CouncilAsAJudge
from intelligenticai.structs.groupchat import GroupChat
from intelligenticai.structs.heavy_agent_group import HeavyAgentGroup
from intelligenticai.structs.hiearchical_agent_group import HierarchicalAgentGroup
from intelligenticai.structs.interactive_groupchat import InteractiveGroupChat
from intelligenticai.structs.ma_utils import list_all_agents
from intelligenticai.structs.majority_voting import MajorityVoting
from intelligenticai.structs.malt import MALT
from intelligenticai.structs.mixture_of_agents import MixtureOfAgents
from intelligenticai.structs.multi_agent_router import MultiAgentRouter
from intelligenticai.structs.sequential_workflow import SequentialWorkflow
from intelligenticai.telemetry.log_executions import log_execution
from intelligenticai.utils.generate_keys import generate_api_key
from intelligenticai.utils.loguru_logger import initialize_logger
from intelligenticai.utils.output_types import OutputType

logger = initialize_logger(log_folder="agent_group_router")

AgentGroupType = Literal[
    "AgentRearrange",
    "MixtureOfAgents",
    "SequentialWorkflow",
    "ConcurrentWorkflow",
    "GroupChat",
    "MultiAgentRouter",
    "AutoAgentGroupBuilder",
    "HiearchicalAgentGroup",
    "auto",
    "MajorityVoting",
    "MALT",
    "CouncilAsAJudge",
    "InteractiveGroupChat",
    "HeavyAgentGroup",
]


class Document(BaseModel):
    file_path: str
    data: str


class AgentGroupRouterConfig(BaseModel):
    """Configuration model for AgentGroupRouter."""

    name: str = Field(
        description="Name identifier for the AgentGroupRouter instance",
    )
    description: str = Field(
        description="Description of the AgentGroupRouter's purpose",
    )
    # max_loops: int = Field(
    #     description="Maximum number of execution loops"
    # )
    agent_group_type: AgentGroupType = Field(
        description="Type of agent_group to use",
    )
    rearrange_flow: Optional[str] = Field(
        description="Flow configuration string"
    )
    rules: Optional[str] = Field(
        description="Rules to inject into every agent"
    )
    multi_agent_collab_prompt: bool = Field(
        description="Whether to enable multi-agent collaboration prompts",
    )
    task: str = Field(
        description="The task to be executed by the agent_group",
    )

    class Config:
        arbitrary_types_allowed = True


class AgentGroupRouterRunError(Exception):
    """Exception raised when an error occurs during task execution."""

    pass


class AgentGroupRouterConfigError(Exception):
    """Exception raised when an error occurs during task execution."""

    pass


class AgentGroupRouter:
    """
    A class that dynamically routes tasks to different agent_group types based on user selection or automatic matching.

    The AgentGroupRouter enables flexible task execution by either using a specified agent_group type or automatically determining
    the most suitable agent_group type for a given task. It handles task execution while managing logging, type validation,
    and metadata capture.

    Args:
        name (str, optional): Name identifier for the AgentGroupRouter instance. Defaults to "agent_group-router".
        description (str, optional): Description of the AgentGroupRouter's purpose. Defaults to "Routes your task to the desired agent_group".
        max_loops (int, optional): Maximum number of execution loops. Defaults to 1.
        agents (List[Union[Agent, Callable]], optional): List of Agent objects or callables to use. Defaults to empty list.
        agent_group_type (AgentGroupType, optional): Type of agent_group to use. Defaults to "SequentialWorkflow".
        autosave (bool, optional): Whether to enable autosaving. Defaults to False.
        flow (str, optional): Flow configuration string. Defaults to None.
        return_json (bool, optional): Whether to return results as JSON. Defaults to False.
        auto_generate_prompts (bool, optional): Whether to auto-generate agent prompts. Defaults to False.
        shared_memory_system (Any, optional): Shared memory system for agents. Defaults to None.
        rules (str, optional): Rules to inject into every agent. Defaults to None.
        documents (List[str], optional): List of document file paths to use. Defaults to empty list.
        output_type (str, optional): Output format type. Defaults to "string". Supported: 'str', 'string', 'list', 'json', 'dict', 'yaml', 'xml'.

    Attributes:
        name (str): Name identifier for the AgentGroupRouter instance
        description (str): Description of the AgentGroupRouter's purpose
        max_loops (int): Maximum number of execution loops
        agents (List[Union[Agent, Callable]]): List of Agent objects or callables
        agent_group_type (AgentGroupType): Type of agent_group being used
        autosave (bool): Whether autosaving is enabled
        flow (str): Flow configuration string
        return_json (bool): Whether results are returned as JSON
        auto_generate_prompts (bool): Whether prompt auto-generation is enabled
        shared_memory_system (Any): Shared memory system for agents
        rules (str): Rules injected into every agent
        documents (List[str]): List of document file paths
        output_type (str): Output format type. Supported: 'str', 'string', 'list', 'json', 'dict', 'yaml', 'xml'.
        logs (List[AgentGroupLog]): List of execution logs
        agent_group: The instantiated agent_group object

    Available AgentGroup Types:
        - AgentRearrange: Optimizes agent arrangement for task execution
        - MixtureOfAgents: Combines multiple agent types for diverse tasks
        - SequentialWorkflow: Executes tasks sequentially
        - ConcurrentWorkflow: Executes tasks in parallel
        - "auto": Automatically selects best agent_group type via embedding search

    Methods:
        run(task: str, device: str = "cpu", all_cores: bool = False, all_gpus: bool = False, *args, **kwargs) -> Any:
            Executes a task using the configured agent_group

        batch_run(tasks: List[str], *args, **kwargs) -> List[Any]:
            Executes multiple tasks in sequence

        threaded_run(task: str, *args, **kwargs) -> Any:
            Executes a task in a separate thread

        async_run(task: str, *args, **kwargs) -> Any:
            Executes a task asynchronously

        concurrent_run(task: str, *args, **kwargs) -> Any:
            Executes a task using concurrent execution

        concurrent_batch_run(tasks: List[str], *args, **kwargs) -> List[Any]:
            Executes multiple tasks concurrently

    """

    def __init__(
        self,
        id: str = generate_api_key(prefix="agent_group-router"),
        name: str = "agent_group-router",
        description: str = "Routes your task to the desired agent_group",
        max_loops: int = 1,
        agents: List[Union[Agent, Callable]] = [],
        agent_group_type: AgentGroupType = "SequentialWorkflow",  # "ConcurrentWorkflow" # "auto"
        autosave: bool = False,
        rearrange_flow: str = None,
        return_json: bool = False,
        auto_generate_prompts: bool = False,
        shared_memory_system: Any = None,
        rules: str = None,
        documents: List[str] = [],  # A list of docs file paths
        output_type: OutputType = "dict-all-except-first",
        speaker_fn: callable = None,
        load_agents_from_csv: bool = False,
        csv_file_path: str = None,
        return_entire_history: bool = True,
        multi_agent_collab_prompt: bool = True,
        list_all_agents: bool = False,
        conversation: Any = None,
        agents_config: Optional[Dict[Any, Any]] = None,
        speaker_function: str = None,
        heavy_agent_group_loops_per_agent: int = 1,
        heavy_agent_group_question_agent_model_name: str = "gpt-4.1",
        heavy_agent_group_worker_model_name: str = "gpt-4.1",
        heavy_agent_group_agent_group_show_output: bool = True,
        telemetry_enabled: bool = False,
        council_judge_model_name: str = "gpt-4o-mini",  # Add missing model_name attribute
        verbose: bool = False,
        worker_tools: List[Callable] = None,
        aggregation_strategy: str = "synthesis",
        *args,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.max_loops = max_loops
        self.agents = agents
        self.agent_group_type = agent_group_type
        self.autosave = autosave
        self.rearrange_flow = rearrange_flow
        self.return_json = return_json
        self.auto_generate_prompts = auto_generate_prompts
        self.shared_memory_system = shared_memory_system
        self.rules = rules
        self.documents = documents
        self.output_type = output_type
        self.speaker_fn = speaker_fn
        self.logs = []
        self.load_agents_from_csv = load_agents_from_csv
        self.csv_file_path = csv_file_path
        self.return_entire_history = return_entire_history
        self.multi_agent_collab_prompt = multi_agent_collab_prompt
        self.list_all_agents = list_all_agents
        self.conversation = conversation
        self.agents_config = agents_config
        self.speaker_function = speaker_function
        self.heavy_agent_group_loops_per_agent = heavy_agent_group_loops_per_agent
        self.heavy_agent_group_question_agent_model_name = (
            heavy_agent_group_question_agent_model_name
        )
        self.heavy_agent_group_worker_model_name = (
            heavy_agent_group_worker_model_name
        )
        self.telemetry_enabled = telemetry_enabled
        self.council_judge_model_name = council_judge_model_name  # Add missing model_name attribute
        self.verbose = verbose
        self.worker_tools = worker_tools
        self.aggregation_strategy = aggregation_strategy
        self.heavy_agent_group_agent_group_show_output = (
            heavy_agent_group_agent_group_show_output
        )

        # Initialize agent_group factory for O(1) lookup performance
        self._agent_group_factory = self._initialize_agent_group_factory()
        self._agent_group_cache = {}  # Cache for created agent_groups

        # Reliability check
        self.reliability_check()

    def reliability_check(self):
        """Perform reliability checks on agent_group configuration.

        Validates essential agent_group parameters and configuration before execution.
        Handles special case for CouncilAsAJudge which may not require agents.
        """
        try:

            if self.verbose:
                logger.info(
                    f"[AgentGroupRouter Reliability Check] Initializing AgentGroupRouter '{self.name}'. "
                    "Validating required parameters for robust operation.\n"
                    "For detailed documentation on AgentGroupRouter configuration, usage, and available agent_group types, "
                    "please visit: https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_group_router/"
                )

            # Check agent_group type first since it affects other validations
            if self.agent_group_type is None:
                raise AgentGroupRouterConfigError(
                    "AgentGroupRouter: AgentGroup type cannot be 'none'. Check the docs for all the agent_group types available. https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_group_router/"
                )

            if (
                self.agent_group_type != "HeavyAgentGroup"
                and self.agents is None
            ):
                raise AgentGroupRouterConfigError(
                    "AgentGroupRouter: No agents provided for the agent_group. Check the docs to learn of required parameters. https://docs.agent_groups.world/en/latest/agent_groups/structs/agent/"
                )

            if (
                self.agent_group_type == "AgentRearrange"
                and self.rearrange_flow is None
            ):
                raise AgentGroupRouterConfigError(
                    "AgentGroupRouter: rearrange_flow cannot be 'none' when using AgentRearrange. Check the AgentGroupRouter docs to learn of required parameters. https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_rearrange/"
                )

            # Validate max_loops
            if self.max_loops == 0:
                raise AgentGroupRouterConfigError(
                    "AgentGroupRouter: max_loops cannot be 0. Check the docs for all the max_loops available. https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_group_router/"
                )

            self.setup()

            if self.telemetry_enabled:
                self.agent_config = self.agent_config()

        except AgentGroupRouterConfigError as e:
            logger.error(
                f"AgentGroupRouterConfigError: {str(e)} Full Traceback: {traceback.format_exc()}"
            )
            raise e

    def setup(self):
        if self.auto_generate_prompts is True:
            self.activate_ape()

        # Handle shared memory
        if self.shared_memory_system is not None:
            self.activate_shared_memory()

        # Handle rules
        if self.rules is not None:
            self.handle_rules()

        if self.multi_agent_collab_prompt is True:
            self.update_system_prompt_for_agent_in_agent_group()

        if self.list_all_agents is True:
            self.list_agents_to_eachother()

    def fetch_message_history_as_string(self):
        try:
            return (
                self.agent_group.conversation.return_all_except_first_string()
            )
        except Exception as e:
            logger.error(
                f"Error fetching message history as string: {str(e)}"
            )
            return None

    def activate_shared_memory(self):
        logger.info("Activating shared memory with all agents ")

        for agent in self.agents:
            agent.long_term_memory = self.shared_memory_system

        logger.info("All agents now have the same memory system")

    def handle_rules(self):
        logger.info("Injecting rules to every agent!")

        for agent in self.agents:
            agent.system_prompt += f"### AgentGroup Rules ### {self.rules}"

        logger.info("Finished injecting rules")

    def activate_ape(self):
        """Activate automatic prompt engineering for agents that support it"""
        try:
            logger.info("Activating automatic prompt engineering...")
            activated_count = 0
            for agent in self.agents:
                if hasattr(agent, "auto_generate_prompt"):
                    agent.auto_generate_prompt = (
                        self.auto_generate_prompts
                    )
                    activated_count += 1
                    logger.debug(
                        f"Activated APE for agent: {agent.name if hasattr(agent, 'name') else 'unnamed'}"
                    )

            logger.info(
                f"Successfully activated APE for {activated_count} agents"
            )

        except Exception as e:
            error_msg = f"Error activating automatic prompt engineering: {str(e)}"
            logger.error(
                f"Error activating automatic prompt engineering in AgentGroupRouter: {str(e)}"
            )
            raise RuntimeError(error_msg) from e

    def _initialize_agent_group_factory(self) -> Dict[str, Callable]:
        """
        Initialize the agent_group factory with O(1) lookup performance.

        Returns:
            Dict[str, Callable]: Dictionary mapping agent_group types to their factory functions.
        """
        return {
            "HeavyAgentGroup": self._create_heavy_agent_group,
            "AgentRearrange": self._create_agent_rearrange,
            "MALT": self._create_malt,
            "CouncilAsAJudge": self._create_council_as_judge,
            "InteractiveGroupChat": self._create_interactive_group_chat,
            "HiearchicalAgentGroup": self._create_hierarchical_agent_group,
            "MixtureOfAgents": self._create_mixture_of_agents,
            "MajorityVoting": self._create_majority_voting,
            "GroupChat": self._create_group_chat,
            "MultiAgentRouter": self._create_multi_agent_router,
            "SequentialWorkflow": self._create_sequential_workflow,
            "ConcurrentWorkflow": self._create_concurrent_workflow,
            "BatchedGridWorkflow": self._create_batched_grid_workflow,
        }

    def _create_heavy_agent_group(self, *args, **kwargs):
        """Factory function for HeavyAgentGroup."""
        return HeavyAgentGroup(
            name=self.name,
            description=self.description,
            output_type=self.output_type,
            loops_per_agent=self.heavy_agent_group_loops_per_agent,
            question_agent_model_name=self.heavy_agent_group_question_agent_model_name,
            worker_model_name=self.heavy_agent_group_worker_model_name,
            agent_prints_on=self.heavy_agent_group_agent_group_show_output,
            worker_tools=self.worker_tools,
            aggregation_strategy=self.aggregation_strategy,
            show_dashboard=False,
        )

    def _create_agent_rearrange(self, *args, **kwargs):
        """Factory function for AgentRearrange."""
        return AgentRearrange(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            flow=self.rearrange_flow,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_batched_grid_workflow(self, *args, **kwargs):
        """Factory function for BatchedGridWorkflow."""
        return BatchedGridWorkflow(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
        )

    def _create_malt(self, *args, **kwargs):
        """Factory function for MALT."""
        return MALT(
            name=self.name,
            description=self.description,
            max_loops=self.max_loops,
            return_dict=True,
            preset_agents=True,
        )

    def _create_council_as_judge(self, *args, **kwargs):
        """Factory function for CouncilAsAJudge."""
        return CouncilAsAJudge(
            name=self.name,
            description=self.description,
            model_name=self.council_judge_model_name,
            output_type=self.output_type,
        )

    def _create_interactive_group_chat(self, *args, **kwargs):
        """Factory function for InteractiveGroupChat."""
        return InteractiveGroupChat(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            output_type=self.output_type,
            speaker_function=self.speaker_function,
        )

    def _create_hierarchical_agent_group(self, *args, **kwargs):
        """Factory function for HierarchicalAgentGroup."""
        return HierarchicalAgentGroup(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_mixture_of_agents(self, *args, **kwargs):
        """Factory function for MixtureOfAgents."""
        return MixtureOfAgents(
            name=self.name,
            description=self.description,
            agents=self.agents,
            aggregator_agent=self.agents[-1],
            layers=self.max_loops,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_majority_voting(self, *args, **kwargs):
        """Factory function for MajorityVoting."""
        return MajorityVoting(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_group_chat(self, *args, **kwargs):
        """Factory function for GroupChat."""
        return GroupChat(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            speaker_fn=self.speaker_fn,
            *args,
            **kwargs,
        )

    def _create_multi_agent_router(self, *args, **kwargs):
        """Factory function for MultiAgentRouter."""
        return MultiAgentRouter(
            name=self.name,
            description=self.description,
            agents=self.agents,
            shared_memory_system=self.shared_memory_system,
            output_type=self.output_type,
        )

    def _create_sequential_workflow(self, *args, **kwargs):
        """Factory function for SequentialWorkflow."""
        return SequentialWorkflow(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            shared_memory_system=self.shared_memory_system,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_concurrent_workflow(self, *args, **kwargs):
        """Factory function for ConcurrentWorkflow."""
        return ConcurrentWorkflow(
            name=self.name,
            description=self.description,
            agents=self.agents,
            max_loops=self.max_loops,
            output_type=self.output_type,
            *args,
            **kwargs,
        )

    def _create_agent_group(self, task: str = None, *args, **kwargs):
        """
        Dynamically create and return the specified agent_group type with O(1) lookup performance.
        Uses factory pattern with caching for optimal performance.

        Args:
            task (str, optional): The task to be executed by the agent_group. Defaults to None.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[AgentRearrange, MixtureOfAgents, SequentialWorkflow, ConcurrentWorkflow]:
                The instantiated agent_group object.

        Raises:
            ValueError: If an invalid agent_group type is provided.
        """

        # Check cache first for better performance
        cache_key = (
            f"{self.agent_group_type}_{hash(str(args) + str(kwargs))}"
        )
        if cache_key in self._agent_group_cache:
            logger.debug(f"Using cached agent_group: {self.agent_group_type}")
            return self._agent_group_cache[cache_key]

        # Use factory pattern for O(1) lookup
        factory_func = self._agent_group_factory.get(self.agent_group_type)
        if factory_func is None:
            valid_types = list(self._agent_group_factory.keys())
            raise ValueError(
                f"Invalid agent_group type: {self.agent_group_type}. "
                f"Valid types are: {', '.join(valid_types)}"
            )

        # Create the agent_group using the factory function
        try:
            agent_group = factory_func(*args, **kwargs)

            # Cache the created agent_group for future use
            self._agent_group_cache[cache_key] = agent_group

            logger.info(
                f"Successfully created agent_group: {self.agent_group_type}"
            )
            return agent_group

        except Exception as e:
            logger.error(
                f"Failed to create agent_group {self.agent_group_type}: {str(e)}"
            )
            raise RuntimeError(
                f"Failed to create agent_group {self.agent_group_type}: {str(e)}"
            ) from e

    def update_system_prompt_for_agent_in_agent_group(self):
        # Use list comprehension for faster iteration
        for agent in self.agents:
            if agent.system_prompt is None:
                agent.system_prompt = ""
            agent.system_prompt += MULTI_AGENT_COLLAB_PROMPT_TWO

    def agent_config(self):
        agent_config = {}
        for agent in self.agents:
            agent_config[agent.agent_name] = agent.to_dict()

        return agent_config

    def list_agents_to_eachother(self):
        if self.agent_group_type == "SequentialWorkflow":
            self.conversation = (
                self.agent_group.agent_rearrange.conversation
            )
        else:
            self.conversation = self.agent_group.conversation

        if self.list_all_agents is True:
            list_all_agents(
                agents=self.agents,
                conversation=self.agent_group.conversation,
                name=self.name,
                description=self.description,
                add_collaboration_prompt=True,
                add_to_conversation=True,
            )

    def _run(
        self,
        task: Optional[str] = None,
        tasks: Optional[List[str]] = None,
        img: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Dynamically run the specified task on the selected or matched agent_group type.

        Args:
            task (str): The task to be executed by the agent_group.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the agent_group's execution.

        Raises:
            Exception: If an error occurs during task execution.
        """
        self.agent_group = self._create_agent_group(task, *args, **kwargs)

        log_execution(
            agent_group_id=self.id,
            status="start",
            agent_group_config=self.to_dict(),
            agent_group_architecture="agent_group_router",
            enabled_on=self.telemetry_enabled,
        )

        args = {}

        if tasks is not None:
            args["tasks"] = tasks
        else:
            args["task"] = task

        if img is not None:
            args["img"] = img

        try:
            if self.agent_group_type == "BatchedGridWorkflow":
                result = self.agent_group.run(**args, **kwargs)
            else:
                result = self.agent_group.run(**args, **kwargs)

            log_execution(
                agent_group_id=self.id,
                status="completion",
                agent_group_config=self.to_dict(),
                agent_group_architecture="agent_group_router",
                enabled_on=self.telemetry_enabled,
            )

            return result
        except AgentGroupRouterRunError as e:
            logger.error(
                f"\n[AgentGroupRouter ERROR] '{self.name}' failed to execute the task on the selected agent_group.\n"
                f"Reason: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}\n\n"
                "Troubleshooting steps:\n"
                "  - Double-check your AgentGroupRouter configuration (agent_group_type, agents, parameters).\n"
                "  - Ensure all individual agents are properly configured and initialized.\n"
                "  - Review the error message and traceback above for clues.\n\n"
                "For detailed documentation on AgentGroupRouter configuration, usage, and available agent_group types, please visit:\n"
                "  https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_group_router/\n"
            )
            raise e

    def run(
        self,
        task: Optional[str] = None,
        img: Optional[str] = None,
        tasks: Optional[List[str]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a task on the selected agent_group type with specified compute resources.

        Args:
            task (str): The task to be executed by the agent_group.
            device (str, optional): Device to run on - "cpu" or "gpu". Defaults to "cpu".
            all_cores (bool, optional): Whether to use all CPU cores. Defaults to True.
            all_gpus (bool, optional): Whether to use all available GPUs. Defaults to False.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the agent_group's execution.

        Raises:
            Exception: If an error occurs during task execution.
        """
        try:
            return self._run(
                task=task,
                img=img,
                tasks=tasks,
                *args,
                **kwargs,
            )
        except AgentGroupRouterRunError as e:
            logger.error(
                f"\n[AgentGroupRouter ERROR] '{self.name}' failed to execute the task on the selected agent_group.\n"
                f"Reason: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}\n\n"
                "Troubleshooting steps:\n"
                "  - Double-check your AgentGroupRouter configuration (agent_group_type, agents, parameters).\n"
                "  - Ensure all individual agents are properly configured and initialized.\n"
                "  - Review the error message and traceback above for clues.\n\n"
                "For detailed documentation on AgentGroupRouter configuration, usage, and available agent_group types, please visit:\n"
                "  https://docs.agent_groups.world/en/latest/agent_groups/structs/agent_group_router/\n"
            )
            raise e

    def __call__(
        self,
        task: str,
        img: Optional[str] = None,
        imgs: Optional[List[str]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Make the AgentGroupRouter instance callable.

        Args:
            task (str): The task to be executed by the agent_group.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the agent_group's execution.
        """
        return self.run(
            task=task, img=img, imgs=imgs, *args, **kwargs
        )

    def batch_run(
        self,
        tasks: List[str],
        img: Optional[str] = None,
        imgs: Optional[List[str]] = None,
        *args,
        **kwargs,
    ) -> List[Any]:
        """
        Execute a batch of tasks on the selected or matched agent_group type.

        Args:
            tasks (List[str]): A list of tasks to be executed by the agent_group.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            List[Any]: A list of results from the agent_group's execution.

        Raises:
            Exception: If an error occurs during task execution.
        """
        results = []
        for task in tasks:
            try:
                result = self.run(
                    task, img=img, imgs=imgs, *args, **kwargs
                )
                results.append(result)
            except Exception as e:
                raise RuntimeError(
                    f"AgentGroupRouter: Error executing batch task on agent_group: {str(e)} Traceback: {traceback.format_exc()}"
                )
        return results

    def concurrent_run(
        self,
        task: str,
        img: Optional[str] = None,
        imgs: Optional[List[str]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a task on the selected or matched agent_group type concurrently.

        Args:
            task (str): The task to be executed by the agent_group.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the agent_group's execution.

        Raises:
            Exception: If an error occurs during task execution.
        """

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=os.cpu_count()
        ) as executor:
            future = executor.submit(
                self.run, task, img=img, imgs=imgs, *args, **kwargs
            )
            result = future.result()
            return result

    def _serialize_callable(
        self, attr_value: Callable
    ) -> Dict[str, Any]:
        """
        Serializes callable attributes by extracting their name and docstring.

        Args:
            attr_value (Callable): The callable to serialize.

        Returns:
            Dict[str, Any]: Dictionary with name and docstring of the callable.
        """
        return {
            "name": getattr(
                attr_value, "__name__", type(attr_value).__name__
            ),
            "doc": getattr(attr_value, "__doc__", None),
        }

    def _serialize_attr(self, attr_name: str, attr_value: Any) -> Any:
        """
        Serializes an individual attribute, handling non-serializable objects.

        Args:
            attr_name (str): The name of the attribute.
            attr_value (Any): The value of the attribute.

        Returns:
            Any: The serialized value of the attribute.
        """
        try:
            if callable(attr_value):
                return self._serialize_callable(attr_value)
            elif hasattr(attr_value, "to_dict"):
                return (
                    attr_value.to_dict()
                )  # Recursive serialization for nested objects
            else:
                json.dumps(
                    attr_value
                )  # Attempt to serialize to catch non-serializable objects
                return attr_value
        except (TypeError, ValueError):
            return f"<Non-serializable: {type(attr_value).__name__}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts all attributes of the class, including callables, into a dictionary.
        Handles non-serializable attributes by converting them or skipping them.

        Returns:
            Dict[str, Any]: A dictionary representation of the class attributes.
        """
        return {
            attr_name: self._serialize_attr(attr_name, attr_value)
            for attr_name, attr_value in self.__dict__.items()
        }
