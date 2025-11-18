import math
from typing import Dict, List, Union

from loguru import logger

from intelligenticai.structs.agent import Agent
from intelligenticai.structs.conversation import Conversation
from intelligenticai.structs.omni_agent_types import AgentListType
from intelligenticai.utils.history_output_formatter import (
    history_output_formatter,
)


# Base AgentGroup class that all other agent_group types will inherit from
class BaseAgentGroup:
    def __init__(
        self,
        agents: AgentListType,
        name: str = "BaseAgentGroup",
        description: str = "A base agent_group implementation",
        output_type: str = "dict",
    ):
        """
        Initialize the BaseAgentGroup with agents, name, description, and output type.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        # Ensure agents is a flat list of Agent objects
        self.agents = (
            [agent for sublist in agents for agent in sublist]
            if isinstance(agents[0], list)
            else agents
        )
        self.name = name
        self.description = description
        self.output_type = output_type
        self.conversation = Conversation()

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        # Implementation will be overridden by child classes
        raise NotImplementedError(
            "This method should be implemented by child classes"
        )

    def _format_return(self) -> Union[Dict, List, str]:
        """Format the return value based on the output_type using history_output_formatter"""
        return history_output_formatter(
            self.conversation, self.output_type
        )


class CircularAgentGroup(BaseAgentGroup):
    """
    Implements a circular agent_group where agents pass tasks in a circular manner.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "CircularAgentGroup",
        description: str = "A circular agent_group where agents pass tasks in a circular manner",
        output_type: str = "dict",
    ):
        """
        Initialize the CircularAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the circular agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        responses = []

        for task in tasks:
            for agent in self.agents:
                response = agent.run(task)
                self.conversation.add(
                    role=agent.agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class LinearAgentGroup(BaseAgentGroup):
    """
    Implements a linear agent_group where agents process tasks sequentially.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "LinearAgentGroup",
        description: str = "A linear agent_group where agents process tasks sequentially",
        output_type: str = "dict",
    ):
        """
        Initialize the LinearAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the linear agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        for agent in self.agents:
            if tasks_copy:
                task = tasks_copy.pop(0)
                response = agent.run(task)
                self.conversation.add(
                    role=agent.agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class StarAgentGroup(BaseAgentGroup):
    """
    Implements a star agent_group where a central agent processes all tasks, followed by others.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "StarAgentGroup",
        description: str = "A star agent_group where a central agent processes all tasks, followed by others",
        output_type: str = "dict",
    ):
        """
        Initialize the StarAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the star agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        responses = []
        center_agent = self.agents[0]  # The central agent

        for task in tasks:
            # Central agent processes the task
            center_response = center_agent.run(task)
            self.conversation.add(
                role=center_agent.agent_name,
                content=center_response,
            )
            responses.append(center_response)

            # Other agents process the same task
            for agent in self.agents[1:]:
                response = agent.run(task)
                self.conversation.add(
                    role=agent.agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class MeshAgentGroup(BaseAgentGroup):
    """
    Implements a mesh agent_group where agents work on tasks randomly from a task queue.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "MeshAgentGroup",
        description: str = "A mesh agent_group where agents work on tasks randomly from a task queue",
        output_type: str = "dict",
    ):
        """
        Initialize the MeshAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the mesh agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        task_queue = tasks.copy()
        responses = []

        while task_queue:
            for agent in self.agents:
                if task_queue:
                    task = task_queue.pop(0)
                    response = agent.run(task)
                    self.conversation.add(
                        role=agent.agent_name,
                        content=response,
                    )
                    responses.append(response)

        return self._format_return()


class PyramidAgentGroup(BaseAgentGroup):
    """
    Implements a pyramid agent_group where agents are arranged in a pyramid structure.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "PyramidAgentGroup",
        description: str = "A pyramid agent_group where agents are arranged in a pyramid structure",
        output_type: str = "dict",
    ):
        """
        Initialize the PyramidAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the pyramid agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        levels = int(
            (-1 + (1 + 8 * len(self.agents)) ** 0.5) / 2
        )  # Number of levels in the pyramid

        for i in range(levels):
            for j in range(i + 1):
                if tasks_copy:
                    task = tasks_copy.pop(0)
                    agent_index = int(i * (i + 1) / 2 + j)
                    if agent_index < len(self.agents):
                        response = self.agents[agent_index].run(task)
                        self.conversation.add(
                            role=self.agents[agent_index].agent_name,
                            content=response,
                        )
                        responses.append(response)

        return self._format_return()


class FibonacciAgentGroup(BaseAgentGroup):
    """
    Implements a Fibonacci agent_group where agents are arranged according to the Fibonacci sequence.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "FibonacciAgentGroup",
        description: str = "A Fibonacci agent_group where agents are arranged according to the Fibonacci sequence",
        output_type: str = "dict",
    ):
        """
        Initialize the FibonacciAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Fibonacci agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        fib = [1, 1]
        while len(fib) < len(self.agents):
            fib.append(fib[-1] + fib[-2])

        for i in range(len(fib)):
            for j in range(fib[i]):
                agent_index = int(sum(fib[:i]) + j)
                if agent_index < len(self.agents) and tasks_copy:
                    task = tasks_copy.pop(0)
                    response = self.agents[agent_index].run(task)
                    self.conversation.add(
                        role=self.agents[agent_index].agent_name,
                        content=response,
                    )
                    responses.append(response)

        return self._format_return()


class PrimeAgentGroup(BaseAgentGroup):
    """
    Implements a Prime agent_group where agents at prime indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "PrimeAgentGroup",
        description: str = "A Prime agent_group where agents at prime indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the PrimeAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Prime agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        primes = [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
        ]  # First 25 prime numbers

        for prime in primes:
            if prime < len(self.agents) and tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[prime].run(task)
                self.conversation.add(
                    role=self.agents[prime].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class PowerAgentGroup(BaseAgentGroup):
    """
    Implements a Power agent_group where agents at power-of-2 indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "PowerAgentGroup",
        description: str = "A Power agent_group where agents at power-of-2 indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the PowerAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Power agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        powers = [2**i for i in range(int(len(self.agents) ** 0.5))]

        for power in powers:
            if power < len(self.agents) and tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[power].run(task)
                self.conversation.add(
                    role=self.agents[power].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class LogAgentGroup(BaseAgentGroup):
    """
    Implements a Log agent_group where agents at logarithmic indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "LogAgentGroup",
        description: str = "A Log agent_group where agents at logarithmic indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the LogAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Log agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        for i in range(len(self.agents)):
            index = 2**i
            if index < len(self.agents) and tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class ExponentialAgentGroup(BaseAgentGroup):
    """
    Implements an Exponential agent_group where agents at exponential indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "ExponentialAgentGroup",
        description: str = "An Exponential agent_group where agents at exponential indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the ExponentialAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Exponential agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        for i in range(len(self.agents)):
            index = min(int(2**i), len(self.agents) - 1)
            if tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class GeometricAgentGroup(BaseAgentGroup):
    """
    Implements a Geometric agent_group where agents at geometrically increasing indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "GeometricAgentGroup",
        description: str = "A Geometric agent_group where agents at geometrically increasing indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the GeometricAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Geometric agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []
        ratio = 2

        for i in range(len(self.agents)):
            index = min(int(ratio**i), len(self.agents) - 1)
            if tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class HarmonicAgentGroup(BaseAgentGroup):
    """
    Implements a Harmonic agent_group where agents at harmonically spaced indices process tasks.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "HarmonicAgentGroup",
        description: str = "A Harmonic agent_group where agents at harmonically spaced indices process tasks",
        output_type: str = "dict",
    ):
        """
        Initialize the HarmonicAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, tasks: List[str]) -> Union[Dict, List, str]:
        """
        Run the Harmonic agent_group with the given tasks

        Args:
            tasks: List of tasks to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not tasks:
            raise ValueError(
                "Agents and tasks lists cannot be empty."
            )

        tasks_copy = tasks.copy()
        responses = []

        for i in range(1, len(self.agents) + 1):
            index = min(
                int(len(self.agents) / i), len(self.agents) - 1
            )
            if tasks_copy:
                task = tasks_copy.pop(0)
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class StaircaseAgentGroup(BaseAgentGroup):
    """
    Implements a Staircase agent_group where agents at staircase-patterned indices process a task.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "StaircaseAgentGroup",
        description: str = "A Staircase agent_group where agents at staircase-patterned indices process a task",
        output_type: str = "dict",
    ):
        """
        Initialize the StaircaseAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, task: str) -> Union[Dict, List, str]:
        """
        Run the Staircase agent_group with the given task

        Args:
            task: Task to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not task:
            raise ValueError("Agents and task cannot be empty.")

        responses = []
        step = len(self.agents) // 5

        for i in range(len(self.agents)):
            index = (i // step) * step
            if index < len(self.agents):
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class SigmoidAgentGroup(BaseAgentGroup):
    """
    Implements a Sigmoid agent_group where agents at sigmoid-distributed indices process a task.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "SigmoidAgentGroup",
        description: str = "A Sigmoid agent_group where agents at sigmoid-distributed indices process a task",
        output_type: str = "dict",
    ):
        """
        Initialize the SigmoidAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, task: str) -> Union[Dict, List, str]:
        """
        Run the Sigmoid agent_group with the given task

        Args:
            task: Task to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not task:
            raise ValueError("Agents and task cannot be empty.")

        responses = []

        for i in range(len(self.agents)):
            index = int(len(self.agents) / (1 + math.exp(-i)))
            if index < len(self.agents):
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


class SinusoidalAgentGroup(BaseAgentGroup):
    """
    Implements a Sinusoidal agent_group where agents at sinusoidally-distributed indices process a task.
    """

    def __init__(
        self,
        agents: AgentListType,
        name: str = "SinusoidalAgentGroup",
        description: str = "A Sinusoidal agent_group where agents at sinusoidally-distributed indices process a task",
        output_type: str = "dict",
    ):
        """
        Initialize the SinusoidalAgentGroup.

        Args:
            agents: List of Agent objects or nested list of Agent objects
            name: Name of the agent_group
            description: Description of the agent_group's purpose
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        super().__init__(agents, name, description, output_type)

    def run(self, task: str) -> Union[Dict, List, str]:
        """
        Run the Sinusoidal agent_group with the given task

        Args:
            task: Task to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.agents or not task:
            raise ValueError("Agents and task cannot be empty.")

        responses = []

        for i in range(len(self.agents)):
            index = int((math.sin(i) + 1) / 2 * len(self.agents))
            if index < len(self.agents):
                response = self.agents[index].run(task)
                self.conversation.add(
                    role=self.agents[index].agent_name,
                    content=response,
                )
                responses.append(response)

        return self._format_return()


# Communication classes
class OneToOne:
    """
    Facilitates one-to-one communication between two agents.
    """

    def __init__(
        self,
        sender: Agent,
        receiver: Agent,
        output_type: str = "dict",
    ):
        """
        Initialize the OneToOne communication.

        Args:
            sender: The sender agent
            receiver: The receiver agent
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        self.sender = sender
        self.receiver = receiver
        self.output_type = output_type
        self.conversation = Conversation()

    def run(
        self, task: str, max_loops: int = 1
    ) -> Union[Dict, List, str]:
        """
        Run the one-to-one communication with the given task

        Args:
            task: Task to be processed
            max_loops: Number of exchange iterations

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.sender or not self.receiver or not task:
            raise ValueError(
                "Sender, receiver, and task cannot be empty."
            )

        responses = []

        try:
            for loop in range(max_loops):
                # Sender processes the task
                sender_response = self.sender.run(task)
                self.conversation.add(
                    role=self.sender.agent_name,
                    content=sender_response,
                )
                responses.append(sender_response)

                # Receiver processes the result of the sender
                receiver_response = self.receiver.run(sender_response)
                self.conversation.add(
                    role=self.receiver.agent_name,
                    content=receiver_response,
                )
                responses.append(receiver_response)

                # Update task for next loop if needed
                if loop < max_loops - 1:
                    task = receiver_response

        except Exception as error:
            logger.error(
                f"Error during one_to_one communication: {error}"
            )
            raise error

        return history_output_formatter(
            self.conversation, self.output_type
        )


class Broadcast:
    """
    Facilitates broadcasting from one agent to many agents.
    """

    def __init__(
        self,
        sender: Agent,
        receivers: AgentListType,
        output_type: str = "dict",
    ):
        """
        Initialize the Broadcast communication.

        Args:
            sender: The sender agent
            receivers: List of receiver agents
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        self.sender = sender
        self.receivers = (
            [agent for sublist in receivers for agent in sublist]
            if isinstance(receivers[0], list)
            else receivers
        )
        self.output_type = output_type
        self.conversation = Conversation()

    def run(self, task: str) -> Union[Dict, List, str]:
        """
        Run the broadcast communication with the given task

        Args:
            task: Task to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.sender or not self.receivers or not task:
            raise ValueError(
                "Sender, receivers, and task cannot be empty."
            )

        try:
            # First get the sender's broadcast message
            broadcast_message = self.sender.run(task)
            self.conversation.add(
                role=self.sender.agent_name,
                content=broadcast_message,
            )

            # Then have all receivers process it
            for agent in self.receivers:
                response = agent.run(broadcast_message)
                self.conversation.add(
                    role=agent.agent_name,
                    content=response,
                )

            return history_output_formatter(
                self.conversation, self.output_type
            )

        except Exception as error:
            logger.error(f"Error during broadcast: {error}")
            raise error


class OneToThree:
    """
    Facilitates one-to-three communication from one agent to exactly three agents.
    """

    def __init__(
        self,
        sender: Agent,
        receivers: AgentListType,
        output_type: str = "dict",
    ):
        """
        Initialize the OneToThree communication.

        Args:
            sender: The sender agent
            receivers: List of exactly three receiver agents
            output_type: Type of output format, one of 'dict', 'list', 'string', 'json', 'yaml', 'xml', etc.
        """
        if len(receivers) != 3:
            raise ValueError(
                "The number of receivers must be exactly 3."
            )

        self.sender = sender
        self.receivers = receivers
        self.output_type = output_type
        self.conversation = Conversation()

    def run(self, task: str) -> Union[Dict, List, str]:
        """
        Run the one-to-three communication with the given task

        Args:
            task: Task to be processed

        Returns:
            Union[Dict, List, str]: The conversation history in the requested format
        """
        if not self.sender or not task:
            raise ValueError("Sender and task cannot be empty.")

        try:
            # Get sender's message
            sender_message = self.sender.run(task)
            self.conversation.add(
                role=self.sender.agent_name,
                content=sender_message,
            )

            # Have each receiver process the message
            for i, agent in enumerate(self.receivers):
                response = agent.run(sender_message)
                self.conversation.add(
                    role=agent.agent_name,
                    content=response,
                )

            return history_output_formatter(
                self.conversation, self.output_type
            )

        except Exception as error:
            logger.error(f"Error in one_to_three: {error}")
            raise error
