import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable, Set
import time
from dataclasses import dataclass
from enum import Enum
import websockets
from websockets.exceptions import ConnectionClosedError

class ConnectionState(Enum):
    """Connection states for clients."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass
class ClientSession:
    """Client session information."""
    client_id: str
    connection: Any
    state: ConnectionState
    last_seen: float
    reconnect_attempts: int = 0
    last_message_id: int = 0
    pending_messages: Dict[int, Any] = None
    
    def __post_init__(self):
        self.pending_messages = {}

class ConnectionManager:
    def __init__(self, 
                 max_reconnect_attempts: int = 3,
                 reconnect_timeout: float = 30.0,
                 heartbeat_interval: float = 10.0,
                 message_timeout: float = 5.0):
        """Initialize connection manager.
        
        Args:
            max_reconnect_attempts: Maximum number of reconnection attempts
            reconnect_timeout: Timeout for reconnection attempts in seconds
            heartbeat_interval: Interval between heartbeat checks in seconds
            message_timeout: Timeout for message delivery in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_timeout = reconnect_timeout
        self.heartbeat_interval = heartbeat_interval
        self.message_timeout = message_timeout
        
        # Session management
        self.sessions: Dict[str, ClientSession] = {}
        self.message_counter: int = 0
        
        # Heartbeat task will be created when needed
        self.heartbeat_task = None
        self._heartbeat_started = False

    async def handle_connection(self, 
                              websocket: Any,
                              client_id: str,
                              message_handler: Callable[[str, Any], Awaitable[None]]):
        """Handle client connection and message routing."""
        # Start heartbeat monitor if not already started
        if not self._heartbeat_started:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            self._heartbeat_started = True
            
        try:
            session = self._create_or_update_session(websocket, client_id)
            
            while True:
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=self.message_timeout
                    )
                    
                    # Update last seen timestamp
                    session.last_seen = time.time()
                    
                    # Handle message
                    await message_handler(client_id, message)
                    
                except asyncio.TimeoutError:
                    if not await self._check_connection(session):
                        break
                        
                except ConnectionClosedError:
                    if not await self._handle_disconnection(session):
                        break
                        
        except Exception as e:
            self.logger.error(f"Error handling connection for client {client_id}: {str(e)}")
            await self._cleanup_session(client_id)

    async def send_message(self, 
                          client_id: str,
                          message: Any,
                          require_ack: bool = True) -> bool:
        """Send message to client with optional acknowledgment."""
        try:
            session = self.sessions.get(client_id)
            if not session or session.state != ConnectionState.CONNECTED:
                return False
                
            if require_ack:
                # Assign message ID for tracking
                self.message_counter += 1
                message_id = self.message_counter
                session.pending_messages[message_id] = message
                
                # Send message with ID
                await session.connection.send({
                    'id': message_id,
                    'data': message
                })
                
                # Wait for acknowledgment
                try:
                    await asyncio.wait_for(
                        self._wait_for_ack(session, message_id),
                        timeout=self.message_timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(f"Message {message_id} to client {client_id} not acknowledged")
                    return False
                    
            else:
                # Send message without waiting for acknowledgment
                await session.connection.send(message)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message to client {client_id}: {str(e)}")
            return False

    async def broadcast_message(self,
                              message: Any,
                              clients: Optional[Set[str]] = None,
                              require_ack: bool = False) -> Dict[str, bool]:
        """Broadcast message to multiple clients."""
        results = {}
        target_clients = clients or self.sessions.keys()
        
        for client_id in target_clients:
            success = await self.send_message(client_id, message, require_ack)
            results[client_id] = success
            
        return results

    async def _handle_disconnection(self, session: ClientSession) -> bool:
        """Handle client disconnection with reconnection attempts."""
        try:
            session.state = ConnectionState.DISCONNECTED
            
            if session.reconnect_attempts >= self.max_reconnect_attempts:
                self.logger.warning(
                    f"Client {session.client_id} exceeded maximum reconnection attempts"
                )
                return False
                
            session.state = ConnectionState.RECONNECTING
            session.reconnect_attempts += 1
            
            # Wait for client to reconnect
            try:
                await asyncio.wait_for(
                    self._wait_for_reconnection(session),
                    timeout=self.reconnect_timeout
                )
                return True
                
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Reconnection timeout for client {session.client_id}"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Error handling disconnection: {str(e)}")
            return False

    async def _wait_for_reconnection(self, session: ClientSession) -> bool:
        """Wait for client to reconnect."""
        while session.state == ConnectionState.RECONNECTING:
            await asyncio.sleep(1.0)
            if session.state == ConnectionState.CONNECTED:
                return True
        return False

    async def _wait_for_ack(self, session: ClientSession, message_id: int):
        """Wait for message acknowledgment."""
        while message_id in session.pending_messages:
            await asyncio.sleep(0.1)

    async def _heartbeat_monitor(self):
        """Monitor client connections with heartbeat checks."""
        while True:
            try:
                current_time = time.time()
                disconnected_clients = []
                
                for client_id, session in self.sessions.items():
                    if session.state == ConnectionState.CONNECTED:
                        if current_time - session.last_seen > self.heartbeat_interval:
                            # Send heartbeat
                            try:
                                await session.connection.send({'type': 'ping'})
                            except Exception:
                                disconnected_clients.append(client_id)
                                
                # Clean up disconnected clients
                for client_id in disconnected_clients:
                    await self._cleanup_session(client_id)
                    
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat monitor: {str(e)}")
                await asyncio.sleep(self.heartbeat_interval)

    def _create_or_update_session(self, 
                                websocket: Any,
                                client_id: str) -> ClientSession:
        """Create new session or update existing one."""
        if client_id in self.sessions:
            session = self.sessions[client_id]
            session.connection = websocket
            session.state = ConnectionState.CONNECTED
            session.last_seen = time.time()
            session.reconnect_attempts = 0
        else:
            session = ClientSession(
                client_id=client_id,
                connection=websocket,
                state=ConnectionState.CONNECTED,
                last_seen=time.time()
            )
            self.sessions[client_id] = session
            
        return session

    async def _cleanup_session(self, client_id: str):
        """Clean up client session."""
        if client_id in self.sessions:
            session = self.sessions[client_id]
            try:
                await session.connection.close()
            except Exception:
                pass
            del self.sessions[client_id]

    async def _check_connection(self, session: ClientSession) -> bool:
        """Check if connection is still alive."""
        try:
            await session.connection.send({'type': 'ping'})
            return True
        except Exception:
            return await self._handle_disconnection(session)

    def get_active_clients(self) -> Set[str]:
        """Get set of currently active client IDs."""
        return {
            client_id
            for client_id, session in self.sessions.items()
            if session.state == ConnectionState.CONNECTED
        }

    def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get status information for a specific client."""
        if client_id not in self.sessions:
            return {'state': ConnectionState.DISCONNECTED.value}
            
        session = self.sessions[client_id]
        return {
            'state': session.state.value,
            'last_seen': session.last_seen,
            'reconnect_attempts': session.reconnect_attempts,
            'pending_messages': len(session.pending_messages)
        }