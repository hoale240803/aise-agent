from typing import Dict, Any, Optional
import logging
from .models import ModelManager

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model = model_manager.get_model("deepseek-chat")
        
    async def generate_code(self, task: Dict[str, Any]) -> str:
        try:
            prompt = f"""
            Generate code for the following task:
            Title: {task['title']}
            Description: {task['description']}
            Requirements: {task.get('requirements', '')}
            Technical specifications: {task.get('technical_specifications', '')}
            
            Please provide:
            1. Complete implementation code
            2. Any necessary imports
            3. Comments explaining key parts
            """
            return await self.model.generate(prompt, max_tokens=1000)
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

class CodeReviewer:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model = model_manager.get_model("deepseek-chat")
        
    async def review_code(self, code: str, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
            Review the following code for task: {task['title']}
            
            Code:
            {code}
            
            Please provide:
            1. Code quality assessment
            2. Potential issues or bugs
            3. Performance considerations
            4. Security concerns
            5. Suggested improvements
            """
            review = await self.model.generate(prompt, max_tokens=1000)
            return {
                "review": review,
                "status": "completed",
                "suggestions": []  # This would be parsed from the review
            }
        except Exception as e:
            logger.error(f"Error reviewing code: {str(e)}")
            raise

class DocumentationGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model = model_manager.get_model("deepseek-chat")
        
    async def generate_documentation(self, task: Dict[str, Any], code: Optional[str] = None) -> str:
        try:
            prompt = f"""
            Generate documentation for the following task:
            Title: {task['title']}
            Description: {task['description']}
            Requirements: {task.get('requirements', '')}
            Technical specifications: {task.get('technical_specifications', '')}
            
            {f'Code to document:\n{code}' if code else ''}
            
            Please provide:
            1. Overview of the feature/functionality
            2. Technical implementation details
            3. Usage examples
            4. API documentation (if applicable)
            5. Configuration options
            6. Troubleshooting guide
            """
            return await self.model.generate(prompt, max_tokens=1000)
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            raise 