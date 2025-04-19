from typing import Dict, Any, Optional, List
import logging
from .models import ModelManager
from .tools import CodeGenerator, CodeReviewer, DocumentationGenerator

logger = logging.getLogger(__name__)

class DeveloperAgent:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model = model_manager.get_model("deepseek-chat")
        self.code_generator = CodeGenerator(model_manager)
        self.code_reviewer = CodeReviewer(model_manager)
        self.documentation_generator = DocumentationGenerator(model_manager)
        self.current_task: Optional[Dict[str, Any]] = None
        self.progress: Dict[str, Any] = {}
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            message_type = message.get("type")
            if message_type == "task_assignment":
                return await self.handle_task_assignment(message)
            elif message_type == "code_review":
                return await self.handle_code_review(message)
            elif message_type == "documentation_request":
                return await self.handle_documentation_request(message)
            elif message_type == "progress_update":
                return await self.handle_progress_update(message)
            else:
                return await self.handle_unknown_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_task_assignment(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.current_task = message["task"]
        self.progress = {
            "status": "in_progress",
            "completed_steps": [],
            "current_step": "analysis"
        }
        
        # Generate implementation plan
        implementation_plan = await self.generate_implementation_plan()
        self.progress["implementation_plan"] = implementation_plan
        
        return {
            "status": "accepted",
            "message": "Task accepted and implementation plan generated",
            "implementation_plan": implementation_plan
        }
        
    async def generate_implementation_plan(self) -> str:
        try:
            prompt = f"""
            Generate an implementation plan for the following task:
            Title: {self.current_task['title']}
            Description: {self.current_task['description']}
            Requirements: {self.current_task.get('requirements', '')}
            
            Please provide:
            1. Analysis of requirements
            2. Technical approach
            3. Implementation steps
            4. Testing strategy
            5. Timeline estimation
            """
            return await self.model.generate(prompt, max_tokens=1000)
        except Exception as e:
            logger.error(f"Error generating implementation plan: {str(e)}")
            raise
            
    async def implement_feature(self) -> Dict[str, Any]:
        try:
            # Generate code
            code = await self.code_generator.generate_code(self.current_task)
            
            # Review code
            review = await self.code_reviewer.review_code(code, self.current_task)
            
            # Generate documentation
            documentation = await self.documentation_generator.generate_documentation(
                self.current_task, code
            )
            
            self.progress["status"] = "completed"
            self.progress["completed_steps"].extend(["code_generation", "code_review", "documentation"])
            
            return {
                "status": "completed",
                "code": code,
                "review": review,
                "documentation": documentation
            }
        except Exception as e:
            logger.error(f"Error implementing feature: {str(e)}")
            raise
            
    async def create_pull_request(self) -> Dict[str, Any]:
        try:
            prompt = f"""
            Generate a pull request description for the following task:
            Title: {self.current_task['title']}
            Description: {self.current_task['description']}
            Implementation details: {self.progress.get('implementation_plan', '')}
            
            Please provide:
            1. Overview of changes
            2. Technical details
            3. Testing performed
            4. Documentation updates
            5. Any breaking changes
            """
            pr_description = await self.model.generate(prompt, max_tokens=1000)
            
            return {
                "status": "created",
                "title": f"Implement {self.current_task['title']}",
                "description": pr_description,
                "branch": f"feature/{self.current_task['title'].lower().replace(' ', '-')}"
            }
        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            raise
            
    async def generate_daily_report(self) -> Dict[str, Any]:
        try:
            prompt = f"""
            Generate a daily progress report for the following task:
            Title: {self.current_task['title']}
            Current status: {self.progress['status']}
            Completed steps: {', '.join(self.progress['completed_steps'])}
            Implementation plan: {self.progress.get('implementation_plan', '')}
            
            Please provide:
            1. Progress summary
            2. Completed work
            3. Current challenges
            4. Next steps
            5. Blockers (if any)
            """
            report = await self.model.generate(prompt, max_tokens=1000)
            
            return {
                "status": "completed",
                "report": report,
                "task_status": self.progress["status"]
            }
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            raise
            
    async def handle_code_review(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            review = await self.code_reviewer.review_code(
                message["code"],
                self.current_task
            )
            return {
                "status": "completed",
                "review": review
            }
        except Exception as e:
            logger.error(f"Error handling code review: {str(e)}")
            raise
            
    async def handle_documentation_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            documentation = await self.documentation_generator.generate_documentation(
                self.current_task,
                message.get("code")
            )
            return {
                "status": "completed",
                "documentation": documentation
            }
        except Exception as e:
            logger.error(f"Error handling documentation request: {str(e)}")
            raise
            
    async def handle_progress_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.progress.update(message["progress"])
            return {
                "status": "updated",
                "progress": self.progress
            }
        except Exception as e:
            logger.error(f"Error handling progress update: {str(e)}")
            raise
            
    async def handle_unknown_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
            Process the following unknown message type:
            Type: {message.get('type', 'unknown')}
            Content: {message}
            
            Please provide:
            1. Suggested action
            2. Response message
            """
            response = await self.model.generate(prompt, max_tokens=500)
            
            return {
                "status": "unknown_message",
                "message": response
            }
        except Exception as e:
            logger.error(f"Error handling unknown message: {str(e)}")
            raise 