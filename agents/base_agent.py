from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: float
    message_type: str

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.current_project: Optional[str] = None

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming messages and return response"""
        pass

    @abstractmethod
    async def start_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new task"""
        pass

    @abstractmethod
    async def update_status(self, status: str) -> None:
        """Update agent status"""
        pass

    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors during task execution"""
        return {
            "error": str(error),
            "agent_id": self.agent_id,
            "status": "error"
        } 