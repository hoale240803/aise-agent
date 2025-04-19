from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
import os
from pathlib import Path
from app.core.agent import Agent, AgentMessage
from app.core.message_broker import MessageBroker
from app.core.models import ModelManager
from app.core.tools import CodeGenerator, CodeReviewer, DocumentationGenerator

logger = logging.getLogger(__name__)

class DeveloperAgent(Agent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "developer")
        self.message_broker = MessageBroker()
        self.model_manager = ModelManager()
        self.code_generator = CodeGenerator()
        self.code_reviewer = CodeReviewer()
        self.docs_generator = DocumentationGenerator()
        
        # Initialize with deepseek-chat model
        self.model = self.model_manager.get_model("deepseek-chat")
        
        self.current_sprint: Dict[str, Any] = {}
        self.daily_tasks: List[Dict[str, Any]] = []
        self.progress_reports: Dict[str, Any] = {}
        self.screenshots_dir = Path("screenshots")
        self.demos_dir = Path("demos")
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories for screenshots and demos"""
        self.screenshots_dir.mkdir(exist_ok=True)
        self.demos_dir.mkdir(exist_ok=True)

    async def process_message(self, message: AgentMessage) -> None:
        """Process incoming messages using deepseek-chat model"""
        try:
            # Use model to determine message handling
            response = await self.model.generate(
                prompt=f"Process message: {message.message_type} with content: {message.content}",
                max_tokens=100
            )
            
            if message.message_type == "task_assignment":
                await self.handle_task_assignment(message)
            elif message.message_type == "code_review_feedback":
                await self.handle_code_review(message)
            elif message.message_type == "sprint_planning":
                await self.handle_sprint_planning(message)
            elif message.message_type == "daily_standup":
                await self.handle_daily_standup(message)
            else:
                logger.warning(f"Unknown message type: {message.message_type}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.handle_error(e)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        if task_type == "implement_feature":
            return await self.implement_feature(task)
        elif task_type == "create_pull_request":
            return await self.create_pull_request(task)
        elif task_type == "update_documentation":
            return await self.update_documentation(task)
        elif task_type == "prepare_daily_report":
            return await self.prepare_daily_report()
        else:
            return {"error": f"Unknown task type: {task_type}"}

    async def handle_task_assignment(self, message: AgentMessage) -> None:
        """Handle new task assignments"""
        task = message.content
        self.daily_tasks.append(task)
        await self.update_status("task_received")
        
        # Start working on the task
        await self.implement_feature(task)

    async def implement_feature(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a feature using deepseek-chat model"""
        await self.update_status("implementing")
        
        try:
            # 1. Analysis with model
            analysis_prompt = f"Analyze requirements for task: {task['title']}\nDescription: {task['description']}"
            analysis_result = await self.model.generate(analysis_prompt, max_tokens=200)
            
            # 2. Design with model
            design_prompt = f"Create design for: {analysis_result}"
            design_result = await self.model.generate(design_prompt, max_tokens=300)
            
            # 3. Implementation using code generator
            implementation_result = await self.code_generator.generate_code(
                design=design_result,
                task=task
            )
            
            # 4. Code review using model
            review_prompt = f"Review code: {implementation_result['code']}"
            review_result = await self.model.generate(review_prompt, max_tokens=200)
            
            # 5. Documentation using docs generator
            doc_result = await self.docs_generator.generate_documentation(
                code=implementation_result['code'],
                task=task
            )
            
            # 6. Update progress
            await self.update_daily_progress(task, {
                "analysis": analysis_result,
                "design": design_result,
                "implementation": implementation_result,
                "review": review_result,
                "documentation": doc_result
            })
            
            return {
                "status": "completed",
                "task_id": task["id"],
                "results": {
                    "analysis": analysis_result,
                    "design": design_result,
                    "implementation": implementation_result,
                    "review": review_result,
                    "documentation": doc_result
                }
            }
        except Exception as e:
            logger.error(f"Error implementing feature: {str(e)}")
            return await self.handle_error(e)

    async def create_pull_request(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pull request using deepseek-chat model"""
        await self.update_status("creating_pr")
        
        # Generate PR description using model
        pr_prompt = f"""
        Create a pull request description for task: {task['title']}
        Changes: {task.get('changes', [])}
        Screenshots: {task.get('screenshots', [])}
        Tests: {task.get('tests', [])}
        Documentation: {task.get('documentation', {})}
        """
        
        pr_description = await self.model.generate(pr_prompt, max_tokens=300)
        
        pr_data = {
            "title": f"Feature: {task['title']}",
            "description": pr_description,
            "changes": task.get("changes", []),
            "screenshots": task.get("screenshots", []),
            "tests": task.get("tests", []),
            "documentation": task.get("documentation", {})
        }
        
        # Send PR to Technical Lead for review
        await self.send_message(
            receiver="technical_lead",
            content=pr_data,
            message_type="code_review_request"
        )
        
        return {"status": "pr_created", "pr_data": pr_data}

    async def update_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update documentation using deepseek-chat model"""
        await self.update_status("updating_docs")
        
        # Generate documentation using model
        docs_prompt = f"""
        Update documentation for task: {task['title']}
        Code changes: {task.get('changes', [])}
        API changes: {task.get('api_changes', [])}
        Progress: {task.get('progress', {})}
        """
        
        docs = await self.model.generate(docs_prompt, max_tokens=400)
        
        return {
            "status": "docs_updated",
            "documentation": {
                "code_docs": await self._update_code_documentation(task),
                "api_docs": await self._update_api_documentation(task),
                "progress_docs": await self._update_progress_documentation(task)
            }
        }

    async def prepare_daily_report(self) -> Dict[str, Any]:
        """Prepare daily report using deepseek-chat model"""
        await self.update_status("preparing_report")
        
        # Generate report using model
        report_prompt = f"""
        Create a daily report with:
        Completed tasks: {self._get_completed_tasks()}
        In progress: {self._get_in_progress_tasks()}
        Next steps: {self._get_next_steps()}
        Technical notes: {self._get_technical_notes()}
        Blockers: {self._get_blockers()}
        """
        
        report = await self.model.generate(report_prompt, max_tokens=500)
        
        # Send report to Project Manager
        await self.send_message(
            receiver="project_manager",
            content=report,
            message_type="daily_report"
        )
        
        return {"status": "report_sent", "report": report}

    async def handle_sprint_planning(self, message: AgentMessage) -> None:
        """Handle sprint planning messages"""
        self.current_sprint = message.content
        await self.update_status("sprint_planned")
        
        # Plan daily tasks
        await self.plan_daily_tasks()

    async def handle_daily_standup(self, message: AgentMessage) -> None:
        """Handle daily standup updates"""
        await self.update_status("standup")
        
        # Prepare standup update
        update = {
            "yesterday": self._get_yesterdays_progress(),
            "today": self._get_todays_plan(),
            "blockers": self._get_blockers()
        }
        
        # Send update to Project Manager
        await self.send_message(
            receiver="project_manager",
            content=update,
            message_type="standup_update"
        )

    def _generate_pr_description(self, task: Dict[str, Any]) -> str:
        """Generate PR description with all necessary information"""
        return f"""
## Feature: {task['title']}

### Changes
{self._format_changes(task.get('changes', []))}

### Screenshots
{self._format_screenshots(task.get('screenshots', []))}

### Tests
{self._format_tests(task.get('tests', []))}

### Documentation
{self._format_documentation(task.get('documentation', {}))}
"""

    def _format_changes(self, changes: List[str]) -> str:
        return "\n".join(f"- {change}" for change in changes)

    def _format_screenshots(self, screenshots: List[str]) -> str:
        return "\n".join(f"![Screenshot]({screenshot})" for screenshot in screenshots)

    def _format_tests(self, tests: List[str]) -> str:
        return "\n".join(f"- {test}" for test in tests)

    def _format_documentation(self, docs: Dict[str, Any]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in docs.items())

    async def _update_code_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update code documentation"""
        return {
            "functions": await self._document_functions(task),
            "classes": await self._document_classes(task),
            "modules": await self._document_modules(task)
        }

    async def _update_api_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update API documentation"""
        return {
            "endpoints": await self._document_endpoints(task),
            "schemas": await self._document_schemas(task),
            "examples": await self._document_examples(task)
        }

    async def _update_progress_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update progress documentation"""
        return {
            "daily_updates": await self._document_daily_updates(task),
            "screenshots": await self._document_screenshots(task),
            "demos": await self._document_demos(task)
        }

    def _get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get list of completed tasks"""
        return [task for task in self.daily_tasks if task.get("status") == "completed"]

    def _get_in_progress_tasks(self) -> List[Dict[str, Any]]:
        """Get list of in-progress tasks"""
        return [task for task in self.daily_tasks if task.get("status") == "in_progress"]

    def _get_next_steps(self) -> List[Dict[str, Any]]:
        """Get list of next steps"""
        return [task for task in self.daily_tasks if task.get("status") == "pending"]

    def _get_technical_notes(self) -> List[str]:
        """Get technical notes from today's work"""
        return self.progress_reports.get("technical_notes", [])

    def _get_todays_screenshots(self) -> List[str]:
        """Get today's screenshots"""
        return self.progress_reports.get("screenshots", [])

    def _get_blockers(self) -> List[str]:
        """Get current blockers"""
        return self.progress_reports.get("blockers", [])

    def _get_yesterdays_progress(self) -> Dict[str, Any]:
        """Get yesterday's progress"""
        return self.progress_reports.get("yesterday", {})

    def _get_todays_plan(self) -> Dict[str, Any]:
        """Get today's plan"""
        return {
            "tasks": self._get_in_progress_tasks() + self._get_next_steps(),
            "goals": [task["title"] for task in self.daily_tasks]
        } 