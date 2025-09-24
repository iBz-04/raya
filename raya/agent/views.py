from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4
from langchain_core.messages import BaseMessage
__all__ = ['AgentResult', 'Action', 'AgentData', 'AgentState', 'AgentStep']

class AgentResult(BaseModel):
    is_done: bool = False
    content: str | None = None
    error: str | None = None

class Action(BaseModel):
    name: str
    params: dict

class AgentData(BaseModel):
    evaluate: Optional[str] = None
    memory: Optional[str] = None
    plan: Optional[str] = None
    thought: Optional[str] = None
    action: Optional[Action] = None

class AgentState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    consecutive_failures: int = 0
    result: Optional[str] = None
    error: Optional[str] = None
    agent_data: Optional[AgentData] = None
    messages: List[BaseMessage] = Field(default_factory=list)
    previous_observation: Optional[str] = None
    query: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def is_done(self) -> bool:
        """Check if the agent is done based on the action name."""
        if self.agent_data and self.agent_data.action and self.agent_data.action.name:
            return self.agent_data.action.name == "Done Tool"
        return False

    def init_state(self, query: str, messages: List[BaseMessage]) -> None:
        """Initialize state for a new query."""
        self.query = query
        self.consecutive_failures = 0
        self.result = None
        self.messages = messages

    def update_state(self, agent_data: AgentData = None, observation: str = None, 
                    result: str = None, messages: List[BaseMessage] = None) -> None:
        """Update the agent state with new data."""
        if agent_data is not None:
            self.agent_data = agent_data
        if observation is not None:
            self.previous_observation = observation
        if result is not None:
            self.result = result
        if messages is not None:
            self.messages.extend(messages)

class AgentStep(BaseModel):
    step_number: int = 0
    max_steps: int

    def is_last_step(self) -> bool:
        """Check if this is the last step."""
        return self.step_number >= self.max_steps - 1

    def increment_step(self) -> None:
        """Increment the step number."""
        self.step_number += 1
