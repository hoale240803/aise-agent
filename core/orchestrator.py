from typing import Dict, List, Optional
from agents.base_agent import BaseAgent, AgentMessage
import asyncio
import logging
from datetime import datetime

class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.projects: Dict[str, Dict] = {}
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)

    async def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type})")

    async def start_project(self, project_data: Dict) -> str:
        """Start a new project and assign initial tasks"""
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.projects[project_id] = {
            "data": project_data,
            "status": "initializing",
            "agents": [],
            "tasks": []
        }
        
        # Assign business analyst agent to analyze requirements
        ba_agent = self._find_agent_by_type("business_analyst")
        if ba_agent:
            await self.assign_task(ba_agent.agent_id, {
                "project_id": project_id,
                "task_type": "requirement_analysis",
                "data": project_data
            })

        return project_id

    async def assign_task(self, agent_id: str, task_data: Dict) -> None:
        """Assign a task to a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        await agent.start_task(task_data)
        self.logger.info(f"Assigned task to agent {agent_id}")

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message between agents"""
        await self.message_queue.put(message)
        self.logger.debug(f"Message queued: {message.sender} -> {message.receiver}")

    async def process_messages(self) -> None:
        """Process messages in the queue"""
        while True:
            message = await self.message_queue.get()
            try:
                if message.receiver in self.agents:
                    response = await self.agents[message.receiver].process_message(message)
                    if response:
                        await self.send_message(response)
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
            finally:
                self.message_queue.task_done()

    def _find_agent_by_type(self, agent_type: str) -> Optional[BaseAgent]:
        """Find an available agent of specific type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == "idle":
                return agent
        return None

    async def get_project_status(self, project_id: str) -> Dict:
        """Get current status of a project"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        return self.projects[project_id]

    async def update_project_status(self, project_id: str, status: str) -> None:
        """Update project status"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        self.projects[project_id]["status"] = status
        self.logger.info(f"Updated project {project_id} status to {status}") 