"""
Deployment Manager for Promptlyzer Client

Handles deployment inference and log retrieval.
"""

from typing import Dict, List, Any, Optional, TYPE_CHECKING
from .exceptions import (
    PromptlyzerError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    ServerError,
)

if TYPE_CHECKING:
    from .client import PromptlyzerClient


class DeploymentManager:
    """Manager for deployment operations"""

    def __init__(self, promptlyzer_client: Optional["PromptlyzerClient"] = None, api_key: str = None, base_url: str = None):
        """
        Initialize Deployment Manager

        Args:
            promptlyzer_client: Parent PromptlyzerClient instance (preferred)
            api_key: API key for authentication (for standalone usage)
            base_url: Base URL of the API (for standalone usage)
        """
        if promptlyzer_client:
            # Use shared client (preferred way)
            self.client = promptlyzer_client
            self.api_key = promptlyzer_client.api_key
            self.base_url = promptlyzer_client.api_url.rstrip('/')
            self._standalone = False
        else:
            # Standalone mode (backward compatibility)
            if not api_key:
                raise ValueError("Either promptlyzer_client or api_key must be provided")
            self.client = None
            self.api_key = api_key
            self.base_url = (base_url or "https://api.promptlyzer.com").rstrip('/')
            self._standalone = True

            # Create own session for standalone mode
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            })

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"

        if self._standalone:
            # Standalone mode: use own session
            try:
                import requests
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                elif response.status_code == 404:
                    raise ResourceNotFoundError(f"Resource not found: {endpoint}")
                elif response.status_code == 400:
                    raise ValidationError(f"Validation error: {response.text}")
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.text}")

                response.raise_for_status()
                return response.json() if response.content else {}

            except Exception as e:
                if isinstance(e, (AuthenticationError, ResourceNotFoundError, ValidationError, ServerError)):
                    raise
                raise PromptlyzerError(f"Request failed: {str(e)}")
        else:
            # Shared client mode: use parent client's session directly
            # Extract parameters compatible with requests.Session.request()
            import requests

            timeout = kwargs.pop('timeout', self.client._request_timeout)
            headers = self.client.get_headers()

            try:
                response = self.client._session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=timeout,
                    **kwargs  # params, json, etc.
                )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                elif response.status_code == 404:
                    raise ResourceNotFoundError(f"Resource not found: {endpoint}")
                elif response.status_code == 400:
                    raise ValidationError(f"Validation error: {response.text}")
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.text}")

                response.raise_for_status()
                return response.json() if response.content else {}

            except requests.exceptions.RequestException as e:
                if isinstance(e, (AuthenticationError, ResourceNotFoundError, ValidationError, ServerError)):
                    raise
                raise PromptlyzerError(f"Request failed: {str(e)}")

    def infer(
        self,
        deployment_id: str,
        prompt: str,
        task_type: str = "customer_agent",
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        provider_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform inference through a deployment with 3-tier smart routing

        Args:
            deployment_id: ID of the deployment (deployment_id)
            prompt: User prompt
            task_type: Task type for routing ("customer_agent" or "summarization")
            context: Optional context (chat history, document to summarize, etc.)
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
            provider_api_key: Optional external API key

        Returns:
            Inference response with content, routing decision, and metrics
        """
        payload = {
            "prompt": prompt,
            "task_type": task_type,
        }

        if context is not None:
            payload["context"] = context
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if provider_api_key is not None:
            payload["provider_api_key"] = provider_api_key

        response = self._make_request(
            "POST",
            f"/deployments/{deployment_id}/infer",
            json=payload,
            timeout=60
        )

        # Response is already dict from _make_request
        return response if isinstance(response, dict) else response.json()

    def get_logs(
        self,
        deployment_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get deployment request logs

        Args:
            deployment_id: Filter by deployment ID
            status: Filter by status (success/error)
            limit: Maximum number of logs to return
            skip: Number of logs to skip

        Returns:
            List of log entries
        """
        params = {
            "limit": limit,
            "skip": skip
        }

        if deployment_id:
            params["deployment_id"] = deployment_id
        if status:
            params["status"] = status

        response = self._make_request(
            "GET",
            "/deployments/logs",
            params=params,
            timeout=10
        )

        return response if isinstance(response, (dict, list)) else response.json()

    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment details by ID"""
        response = self._make_request(
            "GET",
            f"/deployments/{deployment_id}",
            timeout=10
        )
        return response if isinstance(response, dict) else response.json()

    def list_deployments(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """List all deployments"""
        params = {
            "limit": limit,
            "skip": skip
        }

        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status

        response = self._make_request(
            "GET",
            "/deployments",
            params=params,
            timeout=10
        )

        return response if isinstance(response, list) else response.json()
