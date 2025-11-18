import pytest
import asyncio
import websockets
from unittest.mock import Mock, AsyncMock, patch
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from websockets.exceptions import ConnectionClosedError
from federated_learning_framework.connection_manager import (
    ConnectionState,
    ClientSession,
    ConnectionManager
)

@pytest.fixture
def mock_websocket():
    websocket = AsyncMock()
    websocket.send = AsyncMock()
    websocket.recv = AsyncMock()
    websocket.close = AsyncMock()
    return websocket

@pytest.fixture
def connection_manager():
    return ConnectionManager(
        max_reconnect_attempts=3,
        reconnect_timeout=1.0,
        heartbeat_interval=0.5,
        message_timeout=0.5
    )

@pytest.mark.asyncio
async def test_session_creation(connection_manager, mock_websocket):
    client_id = "test_client"
    message_handler = AsyncMock()
    
    # Create task for handle_connection
    task = asyncio.create_task(
        connection_manager.handle_connection(
            mock_websocket,
            client_id,
            message_handler
        )
    )
    
    # Allow tasks to run
    await asyncio.sleep(0.1)
    
    # Check session was created
    assert client_id in connection_manager.sessions
    session = connection_manager.sessions[client_id]
    assert session.client_id == client_id
    assert session.state == ConnectionState.CONNECTED
    
    # Cleanup
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

@pytest.mark.asyncio
async def test_message_sending(connection_manager, mock_websocket):
    client_id = "test_client"
    test_message = "test_message"
    
    # Setup session
    connection_manager._create_or_update_session(mock_websocket, client_id)
    
    # Test sending message
    success = await connection_manager.send_message(client_id, test_message)
    assert success
    mock_websocket.send.assert_awaited_once()

@pytest.mark.asyncio
async def test_message_broadcast(connection_manager):
    mock_websockets = [AsyncMock(), AsyncMock(), AsyncMock()]
    client_ids = ["client1", "client2", "client3"]
    test_message = "broadcast_message"
    
    # Setup sessions
    for client_id, websocket in zip(client_ids, mock_websockets):
        connection_manager._create_or_update_session(websocket, client_id)
        
    # Test broadcast
    results = await connection_manager.broadcast_message(test_message)
    
    # Verify results
    assert len(results) == 3
    assert all(results.values())
    for websocket in mock_websockets:
        websocket.send.assert_awaited_once()

@pytest.mark.asyncio
async def test_heartbeat(connection_manager, mock_websocket):
    client_id = "test_client"
    
    # Setup session
    session = connection_manager._create_or_update_session(mock_websocket, client_id)
    
    # Wait for heartbeat interval
    await asyncio.sleep(0.6)
    
    # Check heartbeat was sent
    mock_websocket.send.assert_awaited()
    assert '{"type": "ping"}' in str(mock_websocket.send.call_args)

@pytest.mark.asyncio
async def test_reconnection(connection_manager, mock_websocket):
    client_id = "test_client"
    session = connection_manager._create_or_update_session(mock_websocket, client_id)
    
    # Simulate disconnection
    mock_websocket.send.side_effect = websockets.exceptions.ConnectionClosedError(
        None, None
    )
    
    # Check reconnection attempt
    success = await connection_manager._handle_disconnection(session)
    assert not success  # Should fail after max attempts
    assert session.reconnect_attempts > 0

@pytest.mark.asyncio
async def test_client_status(connection_manager, mock_websocket):
    client_id = "test_client"
    
    # Test status before session exists
    status = connection_manager.get_client_status(client_id)
    assert status["state"] == ConnectionState.DISCONNECTED.value
    
    # Create session and test status
    session = connection_manager._create_or_update_session(mock_websocket, client_id)
    status = connection_manager.get_client_status(client_id)
    assert status["state"] == ConnectionState.CONNECTED.value
    
    # Test active clients list
    active_clients = connection_manager.get_active_clients()
    assert client_id in active_clients

@pytest.mark.asyncio
async def test_message_acknowledgment(connection_manager, mock_websocket):
    client_id = "test_client"
    test_message = "test_message"
    
    # Setup session
    session = connection_manager._create_or_update_session(mock_websocket, client_id)
    
    # Test sending message with acknowledgment
    send_task = asyncio.create_task(
        connection_manager.send_message(client_id, test_message, require_ack=True)
    )
    
    # Allow send task to start
    await asyncio.sleep(0.1)
    
    # Verify message was sent with ID
    mock_websocket.send.assert_awaited_once()
    sent_data = mock_websocket.send.call_args[0][0]
    assert isinstance(sent_data, dict)
    assert "id" in sent_data
    
    # Remove message from pending to simulate acknowledgment
    message_id = sent_data["id"]
    del session.pending_messages[message_id]
    
    # Check send task completes successfully
    result = await send_task
    assert result

@pytest.mark.asyncio
async def test_cleanup(connection_manager, mock_websocket):
    client_id = "test_client"
    connection_manager._create_or_update_session(mock_websocket, client_id)
    
    # Test cleanup
    await connection_manager._cleanup_session(client_id)
    
    # Verify session was removed
    assert client_id not in connection_manager.sessions
    mock_websocket.close.assert_awaited_once()