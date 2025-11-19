# PTY Create Function for MCP Server

This implementation provides a cross-platform `pty_create(sandbox_id: str)` function for MCP (Model Context Protocol) servers, enabling terminal interaction with sandboxes.

## Features

- ✅ **Cross-platform support**: Works on macOS and Windows
- ✅ **Optional sandbox_id parameter**: Reuse existing sandboxes or create new ones
- ✅ **MCP protocol integration**: Full server/client implementation
- ✅ **Async/await support**: Non-blocking terminal operations
- ✅ **Session management**: Create, manage, and close multiple terminal sessions
- ✅ **Backward compatibility**: Works even without agentsphere package

## Installation

```bash
# Install basic dependencies
pip install -r requirements.txt

# Install agentsphere for full functionality (optional)
pip install agentsphere
```

## Quick Start

### Basic Usage

```python
from pty_create import pty_create, get_terminal_session

# Create a new PTY session
session_id = pty_create()
print(f"Session ID: {session_id}")

# Get session object
session = get_terminal_session(session_id)

# Write to terminal
session.write(b"ls -la\n")

# Read from terminal
output = await session.read()
print(f"Output: {output}")

# Close session
await close_terminal_session(session_id)
```

### With Specific Sandbox

```python
# Create PTY session with specific sandbox
session_id = pty_create("sandbox_123")
```

### Simple Terminal Mode (without agentsphere)

The function works even without the agentsphere package, providing a simple terminal interface:

```python
# This will work even without agentsphere
session_id = pty_create()
session = get_terminal_session(session_id)
```

## MCP Server Integration

### Running the Server

```bash
# Start the MCP server
python examples/server_example.py server
```

### Client Connection

```python
from mcp_terminal import MCPClient

# Connect to server
client = MCPClient(host="localhost", port=8001)
await client.connect()

# Create session
session_id = await client.pty_create()

# Interact with terminal
await client.pty_write("ls -la\n")
output = await client.pty_read()
```

### Interactive Client

```bash
# Run interactive client
python examples/server_example.py interactive
```

## API Reference

### pty_create(sandbox_id: Optional[str] = None) -> str

Create a new PTY terminal session.

**Parameters:**
- `sandbox_id` (str, optional): Sandbox ID to connect to. If not provided, uses existing or creates new.

**Returns:**
- `str`: Unique session identifier

**Example:**
```python
session_id = pty_create()                    # Use default sandbox
session_id = pty_create("sandbox_123")        # Use specific sandbox
```

### get_terminal_session(session_id: str) -> TerminalSession

Get a terminal session by ID.

**Parameters:**
- `session_id` (str): The session ID returned by pty_create()

**Returns:**
- `TerminalSession`: Terminal session object

**Example:**
```python
session = get_terminal_session(session_id)
session.write(b"command\n")
output = await session.read()
```

### list_terminal_sessions() -> dict

List all active terminal sessions.

**Returns:**
- `dict`: Dictionary containing session information

**Example:**
```python
sessions = list_terminal_sessions()
for session_id, info in sessions.items():
    print(f"Session {session_id}: PID {info['pid']}")
```

### close_terminal_session(session_id: str) -> bool

Close a terminal session.

**Parameters:**
- `session_id` (str): The session ID to close

**Returns:**
- `bool`: True if closed successfully

**Example:**
```python
success = await close_terminal_session(session_id)
```

## TerminalSession Methods

### write(data: bytes) -> None

Write data to the terminal.

**Parameters:**
- `data` (bytes): Data to write

**Example:**
```python
session.write(b"echo hello\n")
```

### read() -> str

Read data from the terminal.

**Returns:**
- `str`: Terminal output

**Example:**
```python
output = await session.read()
```

### resize(rows: int, cols: int) -> None

Resize the terminal.

**Parameters:**
- `rows` (int): Number of rows
- `cols` (int): Number of columns

**Example:**
```python
await session.resize(40, 120)
```

### close() -> None

Close the terminal session.

**Example:**
```python
await session.close()
```

## Examples

### Example 1: Basic Usage

```python
import asyncio
from pty_create import pty_create, get_terminal_session

async def main():
    # Create session
    session_id = pty_create()
    session = get_terminal_session(session_id)

    # Run commands
    session.write(b"ls -la\n")
    await asyncio.sleep(1)
    output = await session.read()
    print(f"Directory listing: {output}")

    # Close session
    await close_terminal_session(session_id)

asyncio.run(main())
```

### Example 2: Multiple Sessions

```python
async def multiple_sessions():
    # Create multiple sessions
    session1 = pty_create()
    session2 = pty_create("sandbox_456")

    # Get session objects
    s1 = get_terminal_session(session1)
    s2 = get_terminal_session(session2)

    # Run different commands
    s1.write(b"echo 'Session 1'\n")
    s2.write(b"echo 'Session 2'\n")

    # Wait for completion
    await asyncio.sleep(2)

    # Read outputs
    print(f"Session 1 output: {await s1.read()}")
    print(f"Session 2 output: {await s2.read()}")

    # Close all sessions
    await close_terminal_session(session1)
    await close_terminal_session(session2)
```

### Example 3: MCP Server Integration

```python
from mcp_terminal import TerminalMCPServer

async def run_server():
    server = TerminalMCPServer()
    await server.start_server(host="localhost", port=8001)
    print("MCP server running on ws://localhost:8001")

    # Keep server running
    await asyncio.Event().wait()

asyncio.run(run_server())
```

## Testing

Run the test suite:

```bash
# Test basic functionality
python pty_create.py test

# Test examples
python examples/basic_usage.py full
```

## Platform Compatibility

### macOS
- ✅ Full support with agentsphere
- ✅ Unix PTY mechanisms
- ✅ Terminal.app compatible

### Windows
- ✅ Basic support without agentsphere
- ✅ Terminal integration
- ✅ Command prompt compatible

### Linux
- ✅ Full support with agentsphere
- ✅ Native PTY support

## Error Handling

The function includes comprehensive error handling:

```python
try:
    session_id = pty_create()
except Exception as e:
    print(f"Failed to create session: {e}")
```

Common errors:
- `agentsphere package not available`: Install agentsphere for full functionality
- `Session creation failed`: Check network connectivity and sandbox status
- `Permission denied`: Check file permissions and sandbox access

## Development

### Project Structure

```
agentsphere-mcp-server/
├── terminal_manager.py      # Core terminal management
├── mcp_terminal.py          # MCP server implementation
├── pty_create.py            # Main API function
├── examples/                # Usage examples
│   ├── basic_usage.py       # Basic usage example
│   └── server_example.py    # MCP server example
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Adding New Features

1. Add methods to `TerminalManager` class
2. Update MCP server handlers in `TerminalMCPServer`
3. Add tests in examples directory
4. Update documentation

## License

This implementation is provided for educational and development purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request