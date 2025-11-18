"""Main client for interacting with the Synq API."""

import requests
from typing import Dict, List, Optional, Any
from .models import Agent, Pod, Message, OutputFormat
from .exceptions import SynqAPIError, SynqConnectionError, SynqValidationError


class SynqClient:
    """Client for interacting with the Synq Multi-Agent AI System API.
    
    Example:
        >>> client = SynqClient(base_url="http://localhost:8080")
        >>> agents = client.list_agents()
        >>> pod = client.create_pod(
        ...     pod_id="test_pod",
        ...     agent_ids=["agent1", "agent2"],
        ...     ttl_seconds=3600
        ... )
    """

    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 30):
        """Initialize the Synq client.
        
        Args:
            base_url: Base URL of the Synq API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request to the Synq API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data to send in request body
            params: Query parameters
            
        Returns:
            Response data as dictionary or list
            
        Raises:
            SynqConnectionError: If connection fails
            SynqAPIError: If API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = response.text or error_msg
                
                raise SynqAPIError(
                    error_msg,
                    status_code=response.status_code,
                    response_body=response.text,
                )
            
            # Return JSON response if available
            if response.text:
                try:
                    return response.json()
                except ValueError:
                    return response.text
            
            return None
            
        except requests.ConnectionError as e:
            raise SynqConnectionError(f"Failed to connect to Synq API at {url}: {e}")
        except requests.Timeout as e:
            raise SynqConnectionError(f"Request to Synq API timed out: {e}")
        except requests.RequestException as e:
            raise SynqConnectionError(f"Request to Synq API failed: {e}")

    # Agent Management

    def create_agent(
        self,
        agent_id: str,
        provider: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """Create a new AI agent.
        
        Args:
            agent_id: Unique identifier for the agent
            provider: AI provider ("openai", "anthropic", "custom", "external")
            system_prompt: System prompt for the agent (required for AI providers)
            model: Model name (e.g., "gpt-4o-mini", "claude-3-sonnet-20240229")
            temperature: Temperature for response generation (0.0-1.0)
            api_key: Optional API key (falls back to environment variables)
            metadata: Optional metadata dictionary
            
        Returns:
            Created Agent object
            
        Raises:
            SynqValidationError: If inputs are invalid
            SynqAPIError: If API returns an error
        """
        if not agent_id:
            raise SynqValidationError("agent_id cannot be empty")
        if not provider:
            raise SynqValidationError("provider cannot be empty")
        if provider not in ["openai", "anthropic", "custom", "external"] and not system_prompt:
            raise SynqValidationError("system_prompt is required for AI providers")

        payload = {
            "id": agent_id,
            "provider": provider,
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        if model:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if api_key:
            payload["api_key"] = api_key
        if metadata:
            payload["metadata"] = metadata

        data = self._request("POST", "/agents", data=payload)
        
        # Return the created agent
        return Agent(
            id=agent_id,
            owner_id="",
            type=provider,
            metadata=metadata or {},
            status="active",
        )

    def list_agents(self) -> List[Agent]:
        """List all registered agents.
        
        Returns:
            List of Agent objects
        """
        data = self._request("GET", "/agents")
        if not data or "agents" not in data:
            return []
        return [Agent.from_dict(agent) for agent in data["agents"]]

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Agent object or None if not found
        """
        agents = self.list_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Response data from the API
        """
        return self._request("DELETE", f"/agents/{agent_id}")

    # Pod Management

    def create_pod(
        self,
        pod_id: str,
        agent_ids: List[str],
        ttl_seconds: int = 3600,
        output_format: Optional[OutputFormat] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Pod:
        """Create a new pod for agents to interact in.
        
        Args:
            pod_id: Unique identifier for the pod
            agent_ids: List of agent IDs to include in the pod
            ttl_seconds: Time-to-live in seconds (default: 3600)
            output_format: Optional output format configuration
            context: Optional context metadata
            
        Returns:
            Created Pod object
            
        Raises:
            SynqValidationError: If inputs are invalid
            SynqAPIError: If API returns an error
        """
        if not pod_id:
            raise SynqValidationError("pod_id cannot be empty")
        if not agent_ids:
            raise SynqValidationError("agent_ids cannot be empty")
        if ttl_seconds <= 0:
            raise SynqValidationError("ttl_seconds must be positive")

        payload = {
            "id": pod_id,
            "agents": agent_ids,
            "ttl_seconds": ttl_seconds,
        }
        
        if output_format:
            payload["output_format"] = output_format.to_dict()
        
        if context:
            payload["context"] = context

        data = self._request("POST", "/pods", data=payload)
        
        # The API may return the pod data or just a success message
        if isinstance(data, dict) and "pod" in data:
            return Pod.from_dict(data["pod"])
        else:
            # Construct pod from request data
            return Pod(
                id=pod_id,
                agent_ids=agent_ids,
                ttl_seconds=ttl_seconds,
                status="active",
                output_format=output_format,
                context=context or {},
            )

    def list_pods(self) -> List[Pod]:
        """List all active pods.
        
        Returns:
            List of Pod objects
        """
        data = self._request("GET", "/pods")
        if not data or "pods" not in data:
            # Backward compatibility: also check for "sandboxes" key
            if "sandboxes" in data:
                return [Pod.from_dict(pod) for pod in data["sandboxes"]]
            return []
        return [Pod.from_dict(pod) for pod in data["pods"]]

    def get_pod(self, pod_id: str) -> Optional[Pod]:
        """Get a specific pod by ID.
        
        Args:
            pod_id: The pod's unique identifier
            
        Returns:
            Pod object or None if not found
        """
        pods = self.list_pods()
        for pod in pods:
            if pod.id == pod_id:
                return pod
        return None

    def close_pod(self, pod_id: str) -> Dict[str, Any]:
        """Close a pod, stopping all interactions.
        
        Args:
            pod_id: The pod's unique identifier
            
        Returns:
            Response data from the API
        """
        return self._request("POST", f"/pods/{pod_id}/stop")

    # Message Management

    def get_messages(self, pod_id: str) -> List[Message]:
        """Get all messages in a pod.
        
        Args:
            pod_id: The pod's unique identifier
            
        Returns:
            List of Message objects
        """
        data = self._request("GET", f"/pods/{pod_id}/messages")
        if not data or "messages" not in data:
            return []
        return [Message.from_dict(msg) for msg in data["messages"]]
    
    def inject_message(
        self,
        pod_id: str,
        from_agent: str,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Inject a message into a pod conversation.
        
        Args:
            pod_id: The pod's unique identifier
            from_agent: Agent ID sending the message (can be "system" or "user")
            content: The message content
            role: Message role (default: "user")
            metadata: Optional metadata dict
            
        Returns:
            Response data from the API
        """
        payload = {
            "from": from_agent,
            "content": content,
            "role": role,
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        return self._request(
            "POST",
            f"/pods/{pod_id}/inject",
            data=payload,
        )

    def agent_respond(
        self,
        pod_id: str,
        agent_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Trigger a specific agent to respond to a message.
        
        Args:
            pod_id: The pod's unique identifier
            agent_id: The agent's unique identifier
            message: The message content
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            f"/pods/{pod_id}/agent-respond",
            data={
                "agent_id": agent_id,
                "message": message,
            },
        )

    def start_ai_conversation(
        self,
        pod_id: str,
        rounds: int = 5,
    ) -> Dict[str, Any]:
        """Start an automatic AI conversation between agents.
        
        Args:
            pod_id: The pod's unique identifier
            rounds: Number of conversation rounds (default: 5)
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            f"/pods/{pod_id}/start-ai-conversation",
            data={
                "rounds": rounds,
            },
        )

    def continue_conversation(
        self,
        pod_id: str,
        rounds: int = 3,
    ) -> Dict[str, Any]:
        """Continue an existing conversation for additional rounds.
        
        Args:
            pod_id: The pod's unique identifier
            rounds: Number of additional conversation rounds (default: 3)
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            f"/pods/{pod_id}/continue-conversation",
            data={
                "rounds": rounds,
            },
        )

    # Output Generation

    def generate_output(self, pod_id: str) -> Dict[str, Any]:
        """Generate formatted output from a pod conversation.
        
        Args:
            pod_id: The pod's unique identifier
            
        Returns:
            Generated output data
        """
        return self._request(
            "GET",
            f"/pods/{pod_id}/generate-output",
        )

    # Vector Search

    def vector_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for similar agents using vector embeddings.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of similar agents with scores
        """
        data = self._request(
            "POST",
            "/vector/search",
            data={
                "query_vector": query_vector,
                "top_k": top_k,
            },
        )
        return data.get("results", [])

    # Health Check

    def health_check(self) -> Dict[str, Any]:
        """Check if the Synq API is healthy.
        
        Returns:
            Health status data
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

