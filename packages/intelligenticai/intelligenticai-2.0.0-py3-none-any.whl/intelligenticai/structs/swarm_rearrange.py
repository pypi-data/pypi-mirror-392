import threading
import uuid
from typing import Any, Callable, Dict, List, Optional

from intelligenticai.structs.conversation import Conversation
from intelligenticai.structs.agent_group_id import agent_group_id
from intelligenticai.utils.any_to_str import any_to_str
from intelligenticai.utils.history_output_formatter import (
    HistoryOutputType,
)
from intelligenticai.utils.loguru_logger import initialize_logger

logger = initialize_logger(log_folder="agent_group_arange")


class AgentGroupRearrange:
    """
    A class representing a agent_group of agent_groups for rearranging tasks.

    Attributes:
        id (str): Unique identifier for the agent_group arrangement
        name (str): Name of the agent_group arrangement
        description (str): Description of what this agent_group arrangement does
        agent_groups (dict): A dictionary of agent_groups, where the key is the agent_group's name and the value is the agent_group object
        flow (str): The flow pattern of the tasks
        max_loops (int): The maximum number of loops to run the agent_group
        verbose (bool): A flag indicating whether to log verbose messages
        human_in_the_loop (bool): A flag indicating whether human intervention is required
        custom_human_in_the_loop (Callable[[str], str], optional): A custom function for human-in-the-loop intervention
        return_json (bool): A flag indicating whether to return the result in JSON format
        agent_group_history (dict): A dictionary to keep track of the history of each agent_group
        lock (threading.Lock): A lock for thread-safe operations

    Methods:
        __init__(id: str, name: str, description: str, agent_groups: List[agent_group], flow: str, max_loops: int, verbose: bool,
                human_in_the_loop: bool, custom_human_in_the_loop: Callable, return_json: bool): Initializes the AgentGroupRearrange object
        add_agent_group(agent_group: agent_group): Adds an agent_group to the agent_group
        remove_agent_group(agent_group_name: str): Removes an agent_group from the agent_group
        add_agent_groups(agent_groups: List[agent_group]): Adds multiple agent_groups to the agent_group
        validate_flow(): Validates the flow pattern
        run(task): Runs the agent_group to rearrange the tasks
    """

    def __init__(
        self,
        id: str = agent_group_id(),
        name: str = "AgentGroupRearrange",
        description: str = "A agent_group of agent_groups for rearranging tasks.",
        agent_groups: List[Any] = [],
        flow: str = None,
        max_loops: int = 1,
        verbose: bool = True,
        human_in_the_loop: bool = False,
        custom_human_in_the_loop: Optional[
            Callable[[str], str]
        ] = None,
        return_json: bool = False,
        output_type: HistoryOutputType = "dict-all-except-first",
        *args,
        **kwargs,
    ):
        """
        Initializes the AgentGroupRearrange object.

        Args:
            id (str): Unique identifier for the agent_group arrangement. Defaults to generated UUID.
            name (str): Name of the agent_group arrangement. Defaults to "AgentGroupRearrange".
            description (str): Description of what this agent_group arrangement does.
            agent_groups (List[agent_group]): A list of agent_group objects. Defaults to empty list.
            flow (str): The flow pattern of the tasks. Defaults to None.
            max_loops (int): Maximum number of loops to run. Defaults to 1.
            verbose (bool): Whether to log verbose messages. Defaults to True.
            human_in_the_loop (bool): Whether human intervention is required. Defaults to False.
            custom_human_in_the_loop (Callable): Custom function for human intervention. Defaults to None.
            return_json (bool): Whether to return results as JSON. Defaults to False.
        """
        self.id = id
        self.name = name
        self.description = description
        self.agent_groups = {agent_group.name: agent_group for agent_group in agent_groups}
        self.flow = flow if flow is not None else ""
        self.max_loops = max_loops if max_loops > 0 else 1
        self.verbose = verbose
        self.human_in_the_loop = human_in_the_loop
        self.custom_human_in_the_loop = custom_human_in_the_loop
        self.output_type = output_type
        self.return_json = return_json

        self.agent_group_history = {agent_group.name: [] for agent_group in agent_groups}
        self.lock = threading.Lock()
        self.id = uuid.uuid4().hex if id is None else id

        # Run the reliability checks
        self.reliability_checks()

        # Conversation
        self.conversation = Conversation()

    def reliability_checks(self):
        logger.info("Running reliability checks.")
        if not self.agent_groups:
            raise ValueError("No agent_groups found in the agent_group.")

        if not self.flow:
            raise ValueError("No flow found in the agent_group.")

        if self.max_loops <= 0:
            raise ValueError("Max loops must be a positive integer.")

        logger.info(
            "AgentGroupRearrange initialized with agent_groups: {}".format(
                list(self.agent_groups.keys())
            )
        )

    def set_custom_flow(self, flow: str):
        self.flow = flow
        logger.info(f"Custom flow set: {flow}")

    def add_agent_group(self, agent_group: Any):
        """
        Adds an agent_group to the agent_group.

        Args:
            agent_group (agent_group): The agent_group to be added.
        """
        logger.info(f"Adding agent_group {agent_group.name} to the agent_group.")
        self.agent_groups[agent_group.name] = agent_group

    def track_history(
        self,
        agent_group_name: str,
        result: str,
    ):
        self.agent_group_history[agent_group_name].append(result)

    def remove_agent_group(self, agent_group_name: str):
        """
        Removes an agent_group from the agent_group.

        Args:
            agent_group_name (str): The name of the agent_group to be removed.
        """
        del self.agent_groups[agent_group_name]

    def add_agent_groups(self, agent_groups: List[Any]):
        """
        Adds multiple agent_groups to the agent_group.

        Args:
            agent_groups (List[agent_group]): A list of agent_group objects.
        """
        for agent_group in agent_groups:
            self.agent_groups[agent_group.name] = agent_group

    def validate_flow(self):
        """
        Validates the flow pattern.

        Raises:
            ValueError: If the flow pattern is incorrectly formatted or contains duplicate agent_group names.

        Returns:
            bool: True if the flow pattern is valid.
        """
        if "->" not in self.flow:
            raise ValueError(
                "Flow must include '->' to denote the direction of the task."
            )

        agent_groups_in_flow = []

        # Arrow
        tasks = self.flow.split("->")

        # For the task in tasks
        for task in tasks:
            agent_group_names = [name.strip() for name in task.split(",")]

            # Loop over the agent_group names
            for agent_group_name in agent_group_names:
                if (
                    agent_group_name not in self.agent_groups
                    and agent_group_name != "H"
                ):
                    raise ValueError(
                        f"agent_group '{agent_group_name}' is not registered."
                    )
                agent_groups_in_flow.append(agent_group_name)

        # If the length of the agent_groups does not equal the length of the agent_groups in flow
        if len(set(agent_groups_in_flow)) != len(agent_groups_in_flow):
            raise ValueError(
                "Duplicate agent_group names in the flow are not allowed."
            )

        logger.info("Flow is valid.")
        return True

    def run(
        self,
        task: str = None,
        img: str = None,
        custom_tasks: Optional[Dict[str, str]] = None,
        *args,
        **kwargs,
    ):
        """
        Runs the agent_group to rearrange the tasks.

        Args:
            task: The initial task to be processed.
            img: An optional image input.
            custom_tasks: A dictionary of custom tasks for specific agent_groups.

        Returns:
            str: The final processed task.
        """
        try:
            if not self.validate_flow():
                return "Invalid flow configuration."

            tasks = self.flow.split("->")
            current_task = task

            # Check if custom_tasks is a dictionary and not empty
            if isinstance(custom_tasks, dict) and custom_tasks:
                c_agent_group_name, c_task = next(
                    iter(custom_tasks.items())
                )

                # Find the position of the custom agent_group in the tasks list
                if c_agent_group_name in tasks:
                    position = tasks.index(c_agent_group_name)

                    # If there is a previous agent_group, merge its task with the custom tasks
                    if position > 0:
                        tasks[position - 1] += "->" + c_task
                    else:
                        # If there is no previous agent_group, just insert the custom tasks
                        tasks.insert(position, c_task)

            # Set the loop counter
            loop_count = 0
            while loop_count < self.max_loops:
                for task in tasks:
                    agent_group_names = [
                        name.strip() for name in task.split(",")
                    ]
                    if len(agent_group_names) > 1:
                        # Parallel processing
                        logger.info(
                            f"Running agent_groups in parallel: {agent_group_names}"
                        )
                        results = []
                        for agent_group_name in agent_group_names:
                            if agent_group_name == "H":
                                # Human in the loop intervention
                                if (
                                    self.human_in_the_loop
                                    and self.custom_human_in_the_loop
                                ):
                                    current_task = (
                                        self.custom_human_in_the_loop(
                                            current_task
                                        )
                                    )
                                else:
                                    current_task = input(
                                        "Enter your response: "
                                    )
                            else:
                                agent_group = self.agent_groups[agent_group_name]
                                result = agent_group.run(
                                    current_task, img, *args, **kwargs
                                )
                                result = any_to_str(result)
                                self.conversation.add(
                                    role=agent_group.name, content=result
                                )

                                logger.info(
                                    f"AgentGroup {agent_group_name} returned result of type: {type(result)}"
                                )
                                if isinstance(result, bool):
                                    logger.warning(
                                        f"AgentGroup {agent_group_name} returned a boolean value: {result}"
                                    )
                                    result = str(
                                        result
                                    )  # Convert boolean to string
                                results.append(result)

                        current_task = "; ".join(
                            str(r) for r in results if r is not None
                        )
                    else:
                        # Sequential processing
                        logger.info(
                            f"Running agent_groups sequentially: {agent_group_names}"
                        )
                        agent_group_name = agent_group_names[0]
                        if agent_group_name == "H":
                            # Human-in-the-loop intervention
                            if (
                                self.human_in_the_loop
                                and self.custom_human_in_the_loop
                            ):
                                current_task = (
                                    self.custom_human_in_the_loop(
                                        current_task
                                    )
                                )
                            else:
                                current_task = input(
                                    "Enter the next task: "
                                )
                        else:
                            agent_group = self.agent_groups[agent_group_name]
                            result = agent_group.run(
                                current_task, img, *args, **kwargs
                            )
                            result = any_to_str(result)

                            self.conversation.add(
                                role=agent_group.name, content=result
                            )
                            logger.info(
                                f"AgentGroup {agent_group_name} returned result of type: {type(result)}"
                            )
                            if isinstance(result, bool):
                                logger.warning(
                                    f"AgentGroup {agent_group_name} returned a boolean value: {result}"
                                )
                                result = str(
                                    result
                                )  # Convert boolean to string
                            current_task = (
                                result
                                if result is not None
                                else current_task
                            )
                loop_count += 1

            return current_task

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return str(e)


def agent_group_arrange(
    name: str = "AgentGroupArrange-01",
    description: str = "Combine multiple agent_groups and execute them sequentially",
    agent_groups: List[Callable] = None,
    output_type: str = "json",
    flow: str = None,
    task: str = None,
    *args,
    **kwargs,
):
    """
    Orchestrates the execution of multiple agent_groups in a sequential manner.

    Args:
        name (str, optional): The name of the agent_group arrangement. Defaults to "AgentGroupArrange-01".
        description (str, optional): A description of the agent_group arrangement. Defaults to "Combine multiple agent_groups and execute them sequentially".
        agent_groups (List[Callable], optional): A list of agent_group objects to be executed. Defaults to None.
        output_type (str, optional): The format of the output. Defaults to "json".
        flow (str, optional): The flow pattern of the tasks. Defaults to None.
        task (str, optional): The task to be executed by the agent_groups. Defaults to None.
        *args: Additional positional arguments to be passed to the AgentGroupRearrange object.
        **kwargs: Additional keyword arguments to be passed to the AgentGroupRearrange object.

    Returns:
        Any: The result of the agent_group arrangement execution.
    """
    try:
        agent_group_arrangement = AgentGroupRearrange(
            name,
            description,
            agent_groups,
            output_type,
            flow,
        )
        result = agent_group_arrangement.run(task, *args, **kwargs)
        result = any_to_str(result)
        logger.info(
            f"AgentGroup arrangement {name} executed successfully with output type {output_type}."
        )
        return result
    except Exception as e:
        logger.error(
            f"An error occurred during agent_group arrangement execution: {e}"
        )
        return str(e)
