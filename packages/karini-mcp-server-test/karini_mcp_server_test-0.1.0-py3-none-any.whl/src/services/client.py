import httpx
from typing import Dict, Any, Optional
from bson import ObjectId
from src.services.config import Config
import json
import mimetypes

class KariniClient:    
    def __init__(
        self,
        api_base: Optional[str] = None,
        copilot_id: Optional[str] = None,
        copilot_api_key: Optional[str] = None,
        webhook_api_key: Optional[str] = None,
        webhook_recipe_id: Optional[str] = None,
    ):
        """Initialize Karini client."""
        config = Config.from_env()
        self.api_base = api_base or config.api_base
        self.copilot_id = copilot_id or config.copilot_id
        self.copilot_api_key = copilot_api_key or config.copilot_api_key
        self.webhook_api_key = webhook_api_key or config.webhook_api_key
        self.webhook_recipe_id = webhook_recipe_id or config.webhook_recipe_id
    
    async def ask_copilot(
        self,
        question: str,
        suggest_followup_questions: bool = False,
        files: list = None,
    ):
        """Send a question to the copilot."""
        url = f"{self.api_base}/api/copilot/{self.copilot_id}"
        thread = "68f1efc97c30caba4676f6a0"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.copilot_api_key,
            "x-client-type": "swagger",
        }
        
        payload = {
            "request_id": str(ObjectId()),
            "question": question,
            "suggest_followup_questions": suggest_followup_questions,
            "thread": thread,
        }
        
        if files:
            payload["files"] = {
                "documents": files,
                "metadata": {}
            }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                
                full_response = ""
                async for chunk in response.aiter_text():
                    full_response += chunk
                
                if "#%&response&%#" in full_response:
                    response_part = full_response.split("#%&response&%#")[1]
                    response_part = json.loads(response_part)
                    if "response" in response_part:
                        return response_part.get("response")
                    return response_part
                
                return full_response

    async def invoke_webhook(
        self,
        input_message: str = None,
        files: list = None,
        metadata: dict = None,
    ) -> Dict[str, Any]:
        """Invoke webhook recipe."""
        url = f"{self.api_base}/api/webhook/recipe/{self.webhook_recipe_id}"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-token": self.webhook_api_key,
        }
        
        formatted_files = []
        if files:
            for file_path in files:
                content_type, _ = mimetypes.guess_type(file_path)
                formatted_files.append({
                    "content_type": content_type or "application/octet-stream",
                    "file_path": file_path
                })
        
        payload = {
            "files": formatted_files,
            "input_message": input_message or "",
            "metadata": metadata or {},
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_webhook_status(
        self,
        request_id: str = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get webhook request status - single request or recent requests."""
        
        if request_id:
            # Get single request by ID
            url = f"{self.api_base}/api/webhook/request/{request_id}"
        else:
            # Get recent requests for recipe
            url = f"{self.api_base}/api/webhook/recipe/{self.webhook_recipe_id}?limit={limit}"
        
        headers = {
            "accept": "application/json",
            "x-api-token": self.webhook_api_key,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
