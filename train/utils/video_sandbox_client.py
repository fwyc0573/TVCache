import httpx
import json
import uuid
from typing import Dict, Any, Optional


class SandboxClient:
    """Simple client for interacting with the sandbox server."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the sandbox client.

        Args:
            base_url: Base URL of the sandbox server (default: http://localhost:5000)
        """
        self.base_url = base_url.rstrip('/')
        self.sandbox_id = None
        self._stop_operation_ids: Dict[str, str] = {}

    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the server."""
        url = f"{self.base_url}/{endpoint}"
        # Set timeout to 5 minutes for long-running operations like preprocess
        timeout = httpx.Timeout(300.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()

    async def start_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Start a new sandbox."""
        print(f'[SANDBOX]: Starting: {sandbox_id}')
        result = await self._post('start', {'sandbox_id': sandbox_id})
        self.sandbox_id = sandbox_id
        return result

    async def stop_sandbox(
        self,
        sandbox_id: str,
        operation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stop and remove a sandbox."""
        if not isinstance(sandbox_id, str) or not sandbox_id:
            raise ValueError("sandbox_id must be a non-empty string")

        if operation_id is None:
            operation_id = self._stop_operation_ids.setdefault(
                sandbox_id,
                uuid.uuid4().hex,
            )
        elif not isinstance(operation_id, str) or not operation_id:
            raise ValueError("operation_id must be a non-empty string")
        else:
            existing_operation_id = self._stop_operation_ids.get(
                sandbox_id
            )
            if (
                existing_operation_id is not None
                and existing_operation_id != operation_id
            ):
                raise ValueError(
                    f"Sandbox '{sandbox_id}' already has stop operation "
                    f"'{existing_operation_id}'"
                )
            self._stop_operation_ids[sandbox_id] = operation_id

        print(f'[SANDBOX]: Stopping: {sandbox_id}')
        result = await self._post(
            'stop',
            {
                'sandbox_id': sandbox_id,
                'operation_id': operation_id,
            },
        )
        if type(result["success"]) is not bool:
            raise TypeError("Sandbox stop response 'success' must be boolean")
        if not result["success"]:
            raise RuntimeError("Sandbox server rejected stop operation")
        if result["sandbox_id"] != sandbox_id:
            raise RuntimeError(
                "Sandbox stop response returned a mismatched sandbox_id"
            )
        if result["operation_id"] != operation_id:
            raise RuntimeError(
                "Sandbox stop response returned a mismatched operation_id"
            )
        return result

    async def execute(self, function_name: str, argument: str = '') -> Dict[str, Any]:
        """
        Execute a command in the sandbox.

        Args:
            function_name: Name of the function to execute (e.g., 'load_video', 'preprocess',
                          'object_memory_querying', 'segment_localization', 'caption_retrieval',
                          'visual_question_answering')
            argument: Argument for the function as a string
                     - For load_video_into_sandbox: video filename (e.g., 'tea.mp4')
                     - For object_memory_querying: question string
                     - For segment_localization: description string
                     - For caption_retrieval: tuple string (e.g., '(0, 5)')
                     - For visual_question_answering: tuple string (e.g., '("What is happening?", 3)')
                     - For preprocess: empty string or omit

        Returns:
            Response from the server
        """
        if not self.sandbox_id:
            raise ValueError("No sandbox started. Call start_sandbox() first.")

        return await self._post('execute', {
            'sandbox_id': self.sandbox_id,
            'command': function_name,
            'argument': argument
        })
    

    async def fork(self) -> Dict[str, str]:
        print(f'[SANDBOX]: Forking: {self.sandbox_id}')
        if not self.sandbox_id:
            raise ValueError("No sandbox started. Call start_sandbox() first.")

        return await self._post('fork', {
            'sandbox_id': self.sandbox_id
        })
