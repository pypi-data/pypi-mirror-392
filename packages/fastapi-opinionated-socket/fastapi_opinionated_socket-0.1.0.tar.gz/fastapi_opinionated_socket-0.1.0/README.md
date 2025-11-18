# FastAPI Opinionated Socket Extension

FastAPI Opinionated Socket is an optional extension for the FastAPI Opinionated Core framework that provides Socket.IO functionality for real-time bidirectional communication between clients and servers.

## Overview

This package extends the FastAPI Opinionated Core framework by adding Socket.IO capabilities through a plugin system. It allows you to easily integrate real-time features into your FastAPI applications using the python-socketio library.

## Features

- **Socket.IO Integration**: Provides WebSocket-like bidirectional communication between clients and servers
- **Plugin Architecture**: Integrates seamlessly with the FastAPI Opinionated Core plugin system
- **ASGI Mounting**: Automatically mounts the Socket.IO application onto your FastAPI application
- **Convenience Accessor**: Provides easy access to the AsyncServer instance for emitting events and registering handlers
- **Decorator-Based Event Registration**: Use `@SocketEvent` decorator to register Socket.IO event handlers
- **Namespace Support**: Supports Socket.IO namespaces for organizing events
- **Lifecycle Management**: Properly handles shutdown of the Socket.IO server with graceful cleanup
- **Full CORS Configuration**: Comprehensive CORS support for cross-origin communication
- **Connection Lifecycle Management**: Automatic handling of connect/disconnect events
- **Room and Broadcast Support**: Built-in support for rooms and broadcasting to multiple clients

## Installation

```bash
# Install via Poetry (recommended)
poetry add fastapi-opinionated-socket

# Or via pip
pip install fastapi-opinionated-socket
```

## Quick Start

### 1. Enable the Socket plugin with configuration

```python
from fastapi_opinionated import App
from fastapi_opinionated_socket import SocketPlugin

# Configure the plugin with options
App.configurePlugin(
    SocketPlugin(),
    async_mode="asgi",
    cors_allowed_origins=["*"],  # Adjust for production
    ping_interval=25,
    ping_timeout=5,
    socketio_path="socket.io"
)

# Create your application
app = App.create(title="My API with Socket.IO")
```

### 2. Register Socket.IO event handlers

```python
from fastapi_opinionated_socket import SocketEvent

@SocketEvent("connect")
async def handle_connect(sid, environ):
    print(f"Client {sid} connected")
    await socket_api().emit("welcome", {"msg": "Welcome!"}, to=sid)

@SocketEvent("disconnect")
async def handle_disconnect(sid):
    print(f"Client {sid} disconnected")

@SocketEvent("message")
async def handle_message(sid, data):
    print(f"Received message from {sid}: {data}")
    # Broadcast to all clients
    await socket_api().emit("response", {"message": data, "from": sid})
```

### 3. Use Socket.IO features in your application

```python
from fastapi_opinionated_socket import socket_api

# Broadcast to all clients
await socket_api().emit("notification", {"message": "System update!"})

# Emit to a specific room
await socket_api().emit("room_event", {"data": "Hello room!"}, room="lobby")

# Emit to a specific client
await socket_api().emit("private_msg", {"message": "Private data"}, to="client_sid")
```

## Configuration

The SocketPlugin accepts all python-socketio AsyncServer options:

```python
from fastapi_opinionated import App
from fastapi_opinionated_socket import SocketPlugin

App.configurePlugin(
    SocketPlugin(),
    # Core configuration
    async_mode="asgi",                           # Use ASGI mode
    cors_allowed_origins=["*"],                 # CORS configuration (production: specify domains)
    
    # Connection settings
    ping_interval=25,                           # Ping interval in seconds
    ping_timeout=5,                             # Ping timeout in seconds
    
    # Mount path
    socketio_path="socket.io",                  # Socket.IO endpoint path
    
    # Advanced options
    allow_upgrades=True,                        # Allow transport upgrades
    max_http_buffer_size=1000000,              # Max HTTP buffer size
    engineio_logger=False,                      # Enable engine.io logging
    logger=False                               # Enable Socket.IO logging
)
app = App.create()
```

## Advanced Usage

### Namespaces

Use namespaces to organize related Socket.IO events:

```python
@SocketEvent("join", namespace="/chat")
async def handle_join_room(sid, data):
    room = data.get("room")
    await socket_api().enter_room(sid, room, namespace="/chat")
    await socket_api().emit("joined", {"room": room}, room=sid, namespace="/chat")

@SocketEvent("message", namespace="/chat")
async def handle_chat_message(sid, data):
    room = data.get("room")
    message = data.get("message")
    await socket_api().emit(
        "new_message", 
        {"user": sid, "message": message}, 
        room=room, 
        namespace="/chat"
    )
```

### Rooms and Broadcasting

Manage rooms and send targeted messages:

```python
@SocketEvent("join_room")
async def handle_join_room(sid, room_name):
    await socket_api().enter_room(sid, room_name)
    await socket_api().emit("joined_room", {"room": room_name}, to=sid)

@SocketEvent("leave_room")
async def handle_leave_room(sid, room_name):
    await socket_api().leave_room(sid, room_name)
    await socket_api().emit("left_room", {"room": room_name}, to=sid)

@SocketEvent("send_to_room")
async def handle_room_message(sid, data):
    room = data.get("room")
    message = data.get("message")
    await socket_api().emit("room_message", {"from": sid, "message": message}, room=room)
```

### Authentication and Authorization

Add authentication to socket connections:

```python
@SocketEvent("connect")
async def handle_connect(sid, environ):
    # Extract token from query parameters
    token = environ.get('QUERY_STRING', '').split('token=')[-1]
    
    if not validate_token(token):
        await socket_api().disconnect(sid)
        return False
    
    print(f"Authenticated client {sid} connected")
    await socket_api().emit("authenticated", to=sid)
```

## Architecture

The package consists of:

- **SocketPlugin**: A plugin class that extends BasePlugin and handles the initialization, mounting, and lifecycle of Socket.IO
- **socket_api()**: A helper function that provides access to the AsyncServer instance from the application's plugin registry
- **SocketEvent**: A decorator for registering Socket.IO event handlers with lazy loading and automatic namespace support
- **Event Registry**: Internal registry mechanism that stores and processes Socket.IO event handlers using PluginRegistryStore
- **ASGI Integration**: Automatic mounting of the Socket.IO ASGI app onto the FastAPI application
- **Lifecycle Management**: Proper shutdown handling with graceful cleanup of the Socket.IO server

### Plugin Lifecycle Integration

The Socket plugin properly handles lifecycle management through multiple lifecycle hooks:

- `on_controllers_loaded`: Collects registered socket event handlers after controller discovery
- `on_ready`: Registers collected event handlers with the AsyncServer instance
- `on_shutdown_async`: Gracefully shuts down the Socket.IO server

## Best Practices

1. **CORS Configuration**: Configure CORS properly for production environments - don't use ["*"] in production
2. **Connection Validation**: Always validate and authenticate connections in the connect handler
3. **Error Handling**: Implement proper error handling for Socket.IO operations
4. **Resource Cleanup**: Use disconnect handlers to clean up resources associated with client sessions
5. **Room Management**: Implement proper room join/leave logic to prevent resource leaks
6. **Message Validation**: Validate incoming messages to prevent security issues
7. **Performance**: Keep event handlers lightweight; offload heavy operations to background tasks

## CLI Integration

The Socket plugin can be managed using the FastAPI Opinionated CLI:

```bash
# Enable the Socket plugin
fastapi-opinionated plugins enable fastapi_opinionated_socket.plugin.SocketPlugin

# List registered socket event handlers
fastapi-opinionated list plugins --plugin socket

# List all application routes (including Socket.IO mount point)
fastapi-opinionated list routes
```

## Client-Side Integration

Connect to your Socket.IO server from clients:

```javascript
// Using socket.io-client
import { io } from 'socket.io-client';

// Connect to the server
const socket = io('http://localhost:8000', {
  path: '/socket.io',
  transports: ['websocket', 'polling']
});

socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('response', (data) => {
  console.log('Received response:', data);
});

socket.emit('message', { text: 'Hello server!' });

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

## Troubleshooting

### Common Issues

1. **Plugin Not Enabled**: Make sure to configure SocketPlugin before creating the app
2. **CORS Issues**: Configure `cors_allowed_origins` to match your client domains
3. **Connection Refused**: Verify Socket.IO path matches your client configuration
4. **Event Handlers Not Working**: Ensure App.configurePlugin() is called before App.create()

### Debugging

Enable verbose logging to debug Socket.IO operations:

```python
import logging
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)
```

## Note

FastAPI Opinionated Socket is an **optional extension** of the FastAPI Opinionated Core framework. It provides additional functionality for applications that require real-time communication features, but is not required for basic FastAPI Opinionated Core functionality.