import os
from typing import List
from intelligenticai.structs.agent import Agent
from intelligenticai.structs.conversation import Conversation
from intelligenticai.structs.multi_agent_exec import get_agent_groups_info
from intelligenticai.structs.agent_group_router import AgentGroupRouter
from intelligenticai.utils.history_output_formatter import (
    history_output_formatter,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union, Callable
from intelligenticai.utils.history_output_formatter import HistoryOutputType

tools = [
    {
        "type": "function",
        "function": {
            "name": "select_agent_group",
            "description": "Analyzes the input task and selects the most appropriate agent_group configuration, outputting both the agent_group name and the formatted task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": "The reasoning behind the selection of the agent_group and task description.",
                    },
                    "agent_group_name": {
                        "type": "string",
                        "description": "The name of the selected agent_group that is most appropriate for handling the given task.",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "A clear and structured description of the task to be performed by the agent_group.",
                    },
                },
                "required": [
                    "reasoning",
                    "agent_group_name",
                    "task_description",
                ],
            },
        },
    },
]

router_system_prompt = """
You are an intelligent Router Agent responsible for analyzing tasks and directing them to the most appropriate agent_group in our system. Your role is critical in ensuring optimal task execution and resource utilization.

Key Responsibilities:
1. Task Analysis:
   - Carefully analyze the input task's requirements, complexity, and domain
   - Identify key components and dependencies
   - Determine the specialized skills needed for completion

2. AgentGroup Selection Criteria:
   - Match task requirements with agent_group capabilities
   - Consider agent_group specializations and past performance
   - Evaluate computational resources needed
   - Account for task priority and time constraints

3. Decision Making Framework:
   - Use a systematic approach to evaluate all available agent_groups
   - Consider load balancing across the system
   - Factor in agent_group availability and current workload
   - Assess potential risks and failure points

4. Output Requirements:
   - Provide clear justification for agent_group selection
   - Structure the task description in a way that maximizes agent_group efficiency
   - Include any relevant context or constraints
   - Ensure all critical information is preserved

Best Practices:
- Always prefer specialized agent_groups for domain-specific tasks
- Consider breaking complex tasks into subtasks when appropriate
- Maintain consistency in task formatting across different agent_groups
- Include error handling considerations in task descriptions

Your output must strictly follow the required format:
{
    "agent_group_name": "Name of the selected agent_group",
    "task_description": "Detailed and structured task description"
}

Remember: Your selection directly impacts the overall system performance and task completion success rate. Take all factors into account before making your final decision.
"""


class HybridHierarchicalClusterAgentGroup:
    """
    A class representing a Hybrid Hierarchical-Cluster AgentGroup that routes tasks to appropriate agent_groups.

    Attributes:
        name (str): The name of the agent_group.
        description (str): A description of the agent_group's functionality.
        agent_groups (List[AgentGroupRouter]): A list of available agent_group routers.
        max_loops (int): The maximum number of loops for task processing.
        output_type (str): The format of the output (e.g., list).
        conversation (Conversation): An instance of the Conversation class to manage interactions.
        router_agent (Agent): An instance of the Agent class responsible for routing tasks.
    """

    def __init__(
        self,
        name: str = "Hybrid Hierarchical-Cluster AgentGroup",
        description: str = "A agent_group that uses a hybrid hierarchical-peer model to solve complex tasks.",
        agent_groups: List[Union[AgentGroupRouter, Callable]] = [],
        max_loops: int = 1,
        output_type: HistoryOutputType = "list",
        router_agent_model_name: str = "gpt-4o-mini",
        *args,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.agent_groups = agent_groups
        self.max_loops = max_loops
        self.output_type = output_type

        self.conversation = Conversation()

        self.router_agent = Agent(
            agent_name="Router Agent",
            agent_description="A router agent that routes tasks to the appropriate agent_groups.",
            system_prompt=f"{router_system_prompt}\n\n{get_agent_groups_info(agent_groups=self.agent_groups)}",
            tools_list_dictionary=tools,
            model_name=router_agent_model_name,
            max_loops=1,
            output_type="final",
        )

    def convert_str_to_dict(self, response: str):
        # Handle response whether it's a string or dictionary
        if isinstance(response, str):
            try:
                import json

                response = json.loads(response)
            except json.JSONDecodeError:
                raise ValueError(
                    "Invalid JSON response from router agent"
                )

        return response

    def run(self, task: str, *args, **kwargs):
        """
        Runs the routing process for a given task.

        Args:
            task (str): The task to be processed by the agent_group.

        Returns:
            str: The formatted history output of the conversation.

        Raises:
            ValueError: If the task is empty or invalid.
        """
        if not task:
            raise ValueError("Task cannot be empty.")

        self.conversation.add(role="User", content=task)

        response = self.router_agent.run(task=task)

        if isinstance(response, str):
            response = self.convert_str_to_dict(response)
        else:
            pass

        agent_group_name = response.get("agent_group_name")
        task_description = response.get("task_description")

        if not agent_group_name or not task_description:
            raise ValueError(
                "Invalid response from router agent: both 'agent_group_name' and 'task_description' must be present. "
                f"Received: agent_group_name={agent_group_name}, task_description={task_description}. "
                f"Please check the response format from the model: {self.router_agent.model_name}."
            )

        self.route_task(agent_group_name, task_description)

        return history_output_formatter(
            self.conversation, self.output_type
        )

    def find_agent_group_by_name(self, agent_group_name: str):
        """
        Finds a agent_group by its name.

        Args:
            agent_group_name (str): The name of the agent_group to find.

        Returns:
            AgentGroupRouter: The found agent_group router, or None if not found.
        """
        for agent_group in self.agent_groups:
            if agent_group.name == agent_group_name:
                return agent_group
        return None

    def route_task(self, agent_group_name: str, task_description: str):
        """
        Routes the task to the specified agent_group.

        Args:
            agent_group_name (str): The name of the agent_group to route the task to.
            task_description (str): The description of the task to be executed.

        Raises:
            ValueError: If the agent_group is not found.
        """
        agent_group = self.find_agent_group_by_name(agent_group_name)

        if agent_group:
            output = agent_group.run(task_description)
            self.conversation.add(role=agent_group.name, content=output)
        else:
            raise ValueError(f"AgentGroup '{agent_group_name}' not found.")

    def batched_run(self, tasks: List[str]):
        """
        Runs the routing process for a list of tasks in batches.

        Args:
            tasks (List[str]): A list of tasks to be processed by the agent_group.

        Returns:
            List[str]: A list of formatted history outputs for each batch.

        Raises:
            ValueError: If the task list is empty or invalid.
        """
        if not tasks:
            raise ValueError("Task list cannot be empty.")

        max_workers = os.cpu_count() * 2

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks to the executor
            future_to_task = {
                executor.submit(self.run, task): task
                for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle any errors that occurred during task execution
                    results.append(f"Error processing task: {str(e)}")

        return results
