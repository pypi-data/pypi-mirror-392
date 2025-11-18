"""
Synq Agent Client

Connect your AI agent to a Synq pod and participate in conversations.
"""

import asyncio
import json
import logging
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import websockets
except ImportError:
    raise ImportError(
        "websockets library required. Install with: pip install websockets"
    )

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in a Synq conversation"""
    id: str
    pod_id: str
    from_agent: str
    role: str
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create Message from dictionary"""
        return cls(
            id=data.get("id", ""),
            pod_id=data.get("pod_id", ""),
            from_agent=data.get("from", ""),
            role=data.get("role", "agent"),
            content=data.get("content", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            metadata=data.get("metadata")
        )


class AgentClient:
    """
    Client for connecting an AI agent to a Synq pod.
    
    Example:
        client = AgentClient("my_agent", "pod_12345", "ws://localhost:8080")
        
        @client.on_message
        def handle(message):
            print(f"Got: {message.content}")
            client.send("Response!")
        
        client.run()
    """
    
    def __init__(
        self,
        agent_id: str,
        pod_id: str,
        synq_url: str = "ws://localhost:8080",
        auto_reconnect: bool = True
    ):
        """
        Initialize Synq Agent Client
        
        Args:
            agent_id: Your agent's unique ID
            pod_id: The pod ID to connect to
            synq_url: Synq server WebSocket URL
            auto_reconnect: Whether to reconnect on disconnect
        """
        self.agent_id = agent_id
        self.pod_id = pod_id
        self.synq_url = synq_url.rstrip("/")
        self.auto_reconnect = auto_reconnect
        
        # Build WebSocket URL
        self.ws_url = f"{self.synq_url}/pods/{pod_id}/agents/{agent_id}/connect"
        
        self.websocket = None
        self._message_handler: Optional[Callable] = None
        self._running = False
        self._loop = None  # Event loop reference
        
        logger.info(f"Synq Agent initialized: {agent_id} → {pod_id}")
    
    def on_message(self, handler: Callable[[Message], None]):
        """
        Decorator to register message handler
        
        Example:
            @client.on_message
            def handle(msg):
                print(msg.content)
        """
        self._message_handler = handler
        return handler
    
    def send(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send a message to the pod
        
        Args:
            content: Message content
            metadata: Optional metadata dict
        """
        if not self.websocket:
            raise RuntimeError("Not connected to Synq. Call run() first.")
        
        message = {
            "type": "message",
            "content": content,
        }
        
        if metadata:
            message["metadata"] = metadata
        
        # Schedule the send in the event loop
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_json(message), self._loop)
        else:
            logger.warning("Cannot send message: event loop not running")
    
    async def _send_json(self, data: Dict[str, Any]):
        """Send JSON data over WebSocket"""
        try:
            await self.websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def _connect(self):
        """Establish WebSocket connection"""
        logger.info(f"Connecting to {self.ws_url}")
        self.websocket = await websockets.connect(self.ws_url)
        logger.info("Connected to Synq!")
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type")
            
            if msg_type == "connected":
                logger.info(f"Agent {self.agent_id} connected to pod {self.pod_id}")
            
            elif msg_type == "message":
                if self._message_handler:
                    msg = Message.from_dict(data.get("message", {}))
                    # Run handler in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._message_handler, msg)
            
            elif msg_type == "ack":
                logger.debug(f"Message acknowledged: {data.get('message_id')}")
            
            elif msg_type == "error":
                logger.error(f"Error from Synq: {data.get('error')}")
            
            elif msg_type == "pong":
                logger.debug("Received pong")
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _listen(self):
        """Listen for messages from Synq"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed")
            if self.auto_reconnect and self._running:
                logger.info("Reconnecting...")
                await asyncio.sleep(2)
                await self.run_async()
    
    async def run_async(self):
        """Run the agent (async version)"""
        self._running = True
        self._loop = asyncio.get_event_loop()
        
        try:
            await self._connect()
            await self._listen()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self._running = False
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            if self.auto_reconnect and self._running:
                await asyncio.sleep(2)
                await self.run_async()
    
    def run(self):
        """
        Run the agent (blocking)
        
        This will connect to Synq and listen for messages until interrupted.
        """
        asyncio.run(self.run_async())
    
    def stop(self):
        """Stop the agent"""
        self._running = False
        if self.websocket and self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self._loop)


# Convenience function for simple use cases
def create_agent(
    agent_id: str,
    pod_id: str,
    message_handler: Callable[[Message], None],
    synq_url: str = "ws://localhost:8080"
) -> AgentClient:
    """
    Create and configure an agent in one call
    
    Example:
        def my_handler(msg):
            print(msg.content)
        
        agent = create_agent("my_agent", "pod_123", my_handler)
        agent.run()
    """
    client = AgentClient(agent_id, pod_id, synq_url)
    client.on_message(message_handler)
    return client

