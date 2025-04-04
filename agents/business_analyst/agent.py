from agents.base_agent import BaseAgent, AgentMessage
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from enum import Enum

class ChangePriority(Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class ChangeRequest:
    def __init__(self, 
                 change_id: str,
                 description: str,
                 priority: ChangePriority,
                 impact_analysis: Dict[str, Any],
                 proposed_sprint: Optional[str] = None):
        self.change_id = change_id
        self.description = description
        self.priority = priority
        self.impact_analysis = impact_analysis
        self.proposed_sprint = proposed_sprint
        self.status = "pending"
        self.created_at = datetime.now()
        self.approved = False

class BusinessAnalystAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "business_analyst")
        self.logger = logging.getLogger(__name__)
        self.change_requests: Dict[str, ChangeRequest] = {}
        self.current_sprint_scope: Dict[str, Any] = {}

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming messages"""
        self.logger.info(f"Business Analyst {self.agent_id} received message: {message.message_type}")
        
        if message.message_type == "requirement_analysis":
            analysis_result = await self.analyze_requirements(message.content)
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=analysis_result,
                timestamp=datetime.now().timestamp(),
                message_type="requirement_analysis_result"
            )
        elif message.message_type == "requirement_change":
            change_analysis = await self.analyze_requirement_change(message.content)
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=change_analysis,
                timestamp=datetime.now().timestamp(),
                message_type="change_analysis_result"
            )
        
        return None

    async def start_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new analysis task"""
        self.status = "busy"
        self.current_project = task_data.get("project_id")
        
        try:
            analysis_result = await self.analyze_requirements(task_data)
            self.status = "idle"
            return {
                "status": "completed",
                "result": analysis_result
            }
        except Exception as e:
            self.status = "error"
            return await self.handle_error(e)

    async def analyze_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project requirements and create specifications"""
        requirements = data.get("requirements", "")
        
        # TODO: Implement actual requirement analysis using NLP
        # This is a placeholder implementation
        analysis = {
            "project_scope": self._extract_project_scope(requirements),
            "main_features": self._identify_main_features(requirements),
            "technical_requirements": self._identify_technical_requirements(requirements),
            "timeline_estimate": self._estimate_timeline(requirements),
            "risk_assessment": self._assess_risks(requirements)
        }
        
        return analysis

    def _extract_project_scope(self, requirements: str) -> Dict[str, Any]:
        """Extract project scope from requirements"""
        # TODO: Implement actual scope extraction
        return {
            "description": "Project scope extracted from requirements",
            "objectives": ["Objective 1", "Objective 2"],
            "deliverables": ["Deliverable 1", "Deliverable 2"]
        }

    def _identify_main_features(self, requirements: str) -> List[Dict[str, Any]]:
        """Identify main features from requirements"""
        # TODO: Implement actual feature identification
        return [
            {
                "name": "Feature 1",
                "description": "Description of feature 1",
                "priority": "high"
            },
            {
                "name": "Feature 2",
                "description": "Description of feature 2",
                "priority": "medium"
            }
        ]

    def _identify_technical_requirements(self, requirements: str) -> Dict[str, Any]:
        """Identify technical requirements"""
        # TODO: Implement actual technical requirement identification
        return {
            "frontend": ["React", "TypeScript"],
            "backend": ["Python", "FastAPI"],
            "database": "PostgreSQL",
            "infrastructure": ["Docker", "Kubernetes"]
        }

    def _estimate_timeline(self, requirements: str) -> Dict[str, Any]:
        """Estimate project timeline"""
        # TODO: Implement actual timeline estimation
        return {
            "total_weeks": 12,
            "phases": [
                {"name": "Planning", "weeks": 2},
                {"name": "Development", "weeks": 8},
                {"name": "Testing", "weeks": 2}
            ]
        }

    def _assess_risks(self, requirements: str) -> List[Dict[str, Any]]:
        """Assess project risks"""
        # TODO: Implement actual risk assessment
        return [
            {
                "risk": "Technical complexity",
                "impact": "high",
                "probability": "medium",
                "mitigation": "Early technical spikes"
            }
        ]

    async def update_status(self, status: str) -> None:
        """Update agent status"""
        self.status = status
        self.logger.info(f"Business Analyst {self.agent_id} status updated to {status}")

    async def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "requirement_analysis",
            "scope_definition",
            "feature_identification",
            "technical_requirement_analysis",
            "timeline_estimation",
            "risk_assessment"
        ]

    async def analyze_requirement_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirement changes and determine impact"""
        change_id = f"cr_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        change_description = data.get("change_description", "")
        current_sprint = data.get("current_sprint", {})
        
        # Analyze change impact
        impact_analysis = await self._analyze_change_impact(
            change_description,
            current_sprint
        )
        
        # Determine if change can be accommodated in current sprint
        can_accommodate = await self._can_accommodate_in_current_sprint(
            impact_analysis,
            current_sprint
        )
        
        # Create change request
        change_request = ChangeRequest(
            change_id=change_id,
            description=change_description,
            priority=self._determine_priority(impact_analysis),
            impact_analysis=impact_analysis,
            proposed_sprint=current_sprint.get("id") if can_accommodate else None
        )
        
        self.change_requests[change_id] = change_request
        
        return {
            "change_id": change_id,
            "can_accommodate": can_accommodate,
            "impact_analysis": impact_analysis,
            "recommendation": self._generate_recommendation(change_request),
            "priority": change_request.priority.value
        }

    async def _analyze_change_impact(self, change_description: str, current_sprint: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of a requirement change"""
        # TODO: Implement actual impact analysis using NLP and project data
        return {
            "timeline_impact": {
                "additional_days": 3,
                "can_meet_deadline": True
            },
            "cost_impact": {
                "additional_hours": 24,
                "budget_impact": "within_budget"
            },
            "resource_impact": {
                "additional_resources_needed": False,
                "resource_availability": "available"
            },
            "technical_impact": {
                "complexity": "medium",
                "feasibility": "feasible"
            },
            "dependencies": {
                "affected_features": ["feature1", "feature2"],
                "blocking_issues": []
            },
            "risks": [
                {
                    "risk": "Integration complexity",
                    "severity": "medium",
                    "mitigation": "Additional testing required"
                }
            ]
        }

    async def _can_accommodate_in_current_sprint(self, impact_analysis: Dict[str, Any], current_sprint: Dict[str, Any]) -> bool:
        """Determine if change can be accommodated in current sprint"""
        # TODO: Implement actual sprint capacity analysis
        timeline_impact = impact_analysis["timeline_impact"]
        resource_impact = impact_analysis["resource_impact"]
        
        return (
            timeline_impact["can_meet_deadline"] and
            not resource_impact["additional_resources_needed"] and
            impact_analysis["technical_impact"]["feasibility"] == "feasible"
        )

    def _determine_priority(self, impact_analysis: Dict[str, Any]) -> ChangePriority:
        """Determine priority of the change request"""
        # TODO: Implement actual priority determination logic
        if impact_analysis["technical_impact"]["complexity"] == "high":
            return ChangePriority.MAJOR
        elif impact_analysis["timeline_impact"]["additional_days"] > 5:
            return ChangePriority.MAJOR
        else:
            return ChangePriority.MINOR

    def _generate_recommendation(self, change_request: ChangeRequest) -> str:
        """Generate recommendation for handling the change"""
        if change_request.priority == ChangePriority.CRITICAL:
            return "Immediate implementation required"
        elif change_request.proposed_sprint:
            return f"Can be implemented in current sprint with {change_request.impact_analysis['timeline_impact']['additional_days']} days extension"
        else:
            return "Should be planned for next sprint"

    async def update_sprint_scope(self, sprint_data: Dict[str, Any]) -> None:
        """Update current sprint scope"""
        self.current_sprint_scope = sprint_data
        self.logger.info(f"Updated sprint scope for sprint {sprint_data.get('id')}")

    async def get_change_requests(self) -> List[Dict[str, Any]]:
        """Get all change requests"""
        return [
            {
                "change_id": cr.change_id,
                "description": cr.description,
                "priority": cr.priority.value,
                "status": cr.status,
                "proposed_sprint": cr.proposed_sprint
            }
            for cr in self.change_requests.values()
        ] 