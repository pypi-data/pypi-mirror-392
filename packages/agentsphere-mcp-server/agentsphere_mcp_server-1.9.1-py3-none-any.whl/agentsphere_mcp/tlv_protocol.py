"""
TLV (Type-Length-Value) Protocol Implementation

This module provides a structured communication protocol using Type-Length-Value format.
The protocol structure is: length(64bit):sign(8bit):content(variable)
"""

import json
import struct
from enum import IntEnum
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from .logger import logger


class TLVSign(IntEnum):
    """TLV message type/signature enumeration"""
    REGISTER = 1      # Register sandbox ID (A → B)
    EXECUTE = 2       # Execute command (B → A)
    GET_OUTPUT = 3    # Get history output (B → A)
    PTY_CLOSE = 4     # Close PTY connection (A → B, B exits)

    @classmethod
    def description(cls, sign: int) -> str:
        """Get human-readable description for a sign value"""
        try:
            return cls(sign).name
        except ValueError:
            return "UNKNOWN"


@dataclass
class TLVMessage:
    """Represents a TLV message structure"""
    sign: TLVSign
    content: Dict[str, Any]

    def to_bytes(self) -> bytes:
        """Convert TLV message to bytes format"""
        # Serialize content to JSON
        content_json = json.dumps(self.content, separators=(',', ':'), ensure_ascii=False)
        content_bytes = content_json.encode('utf-8')

        # Pack structure: length(64bit, big-endian):sign(8bit):content
        length = len(content_bytes)
        packed_header = struct.pack('!QB', length, self.sign)

        return packed_header + content_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TLVMessage':
        """Create TLV message from bytes"""
        if len(data) < 9:  # Minimum size: 8 bytes length + 1 byte sign
            raise ValueError("Data too short for TLV message")

        # Unpack header
        length, sign = struct.unpack('!QB', data[:9])

        # Validate length
        if len(data) < 9 + length:
            raise ValueError(f"Data length mismatch. Expected {9 + length} bytes, got {len(data)}")

        # Extract and parse content
        content_bytes = data[9:9+length]
        try:
            content = json.loads(content_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in TLV content: {e}")

        return cls(sign=TLVSign(sign), content=content)

    def __str__(self) -> str:
        return f"TLVMessage(sign={TLVSign.description(self.sign)}, content={self.content})"


class TLVProtocol:
    """High-level TLV protocol handler"""

    @staticmethod
    def create_register_message(sandbox_id: str, client_info: Optional[Dict[str, Any]] = None) -> TLVMessage:
        """Create a registration message

        Args:
            sandbox_id: Unique identifier for the sandbox/client
            client_info: Additional client information (optional)

        Returns:
            TLVMessage with REGISTER type
        """
        content = {
            "sandbox_id": sandbox_id,
            "timestamp": TLVProtocol._get_timestamp()
        }

        if client_info:
            content.update(client_info)

        return TLVMessage(sign=TLVSign.REGISTER, content=content)

    @staticmethod
    def create_execute_command_message(sandbox_id: str, command: str) -> TLVMessage:
        """Create an execute command message

        Args:
            sandbox_id: Target sandbox ID
            command: Command to execute

        Returns:
            TLVMessage with EXECUTE type
        """
        content = {
            "sandbox_id": sandbox_id,
            "command": command,
            "timestamp": TLVProtocol._get_timestamp()
        }
        return TLVMessage(sign=TLVSign.EXECUTE, content=content)

    @staticmethod
    def create_get_output_message(sandbox_id: str, output_id: Optional[str] = None,
                                max_lines: Optional[int] = None) -> TLVMessage:
        """Create a get output message

        Args:
            sandbox_id: Target sandbox ID
            output_id: Specific output ID to retrieve (optional)
            max_lines: Maximum number of lines to retrieve (optional)

        Returns:
            TLVMessage with GET_OUTPUT type
        """
        content = {
            "sandbox_id": sandbox_id,
            "timestamp": TLVProtocol._get_timestamp()
        }

        if output_id:
            content["output_id"] = output_id
        if max_lines is not None:
            content["max_lines"] = max_lines

        return TLVMessage(sign=TLVSign.GET_OUTPUT, content=content)

    @staticmethod
    def create_pty_close_message(sandbox_id: str) -> TLVMessage:
        """Create a PTY close message to request client exit

        When the client receives this message, it should:
        1. Call pty.send_input("exit\\n") to gracefully close the PTY
        2. Exit the main program

        Args:
            sandbox_id: Target sandbox ID to close

        Returns:
            TLVMessage with PTY_CLOSE type
        """
        content = {
            "sandbox_id": sandbox_id,
            "timestamp": TLVProtocol._get_timestamp(),
            "action": "close_pty"
        }
        return TLVMessage(sign=TLVSign.PTY_CLOSE, content=content)

    @staticmethod
    def parse_message(data: bytes) -> TLVMessage:
        """Parse raw bytes into TLV message

        Args:
            data: Raw bytes data

        Returns:
            Parsed TLVMessage

        Raises:
            ValueError: If data is invalid or malformed
        """
        return TLVMessage.from_bytes(data)

    @staticmethod
    def _get_timestamp() -> float:
        """Get current timestamp"""
        import time
        return time.time()


class TLVClient:
    """Helper class for TLV client operations"""

    def __init__(self, socket):
        self.socket = socket
        self.buffer = b""

    def send_tlv_message(self, message: TLVMessage) -> None:
        """Send a TLV message to the socket

        Args:
            message: TLVMessage to send
        """
        try:
            data = message.to_bytes()
            self.socket.send(data)
            logger.debug(f"Sent TLV message: {message}")
        except Exception as e:
            logger.error(f"Failed to send TLV message: {e}")
            raise

    def receive_tlv_message(self, timeout: Optional[float] = None) -> TLVMessage:
        """Receive a TLV message from the socket

        Args:
            timeout: Optional receive timeout in seconds

        Returns:
            Received TLVMessage

        Raises:
            ValueError: If message is malformed
            ConnectionError: If connection is lost
        """
        import select

        # Read until we have at least 9 bytes (header)
        while len(self.buffer) < 9:
            if timeout is not None:
                # Use select for timeout
                readable, _, _ = select.select([self.socket], [], [], timeout)
                if not readable:
                    raise TimeoutError("Receive timeout")

            try:
                data = self.socket.recv(4096)
                if not data:
                    raise ConnectionError("Connection closed by peer")
                self.buffer += data
            except Exception as e:
                logger.error(f"Failed to receive data: {e}")
                raise

        # Parse length and sign from header
        length, sign = struct.unpack('!QB', self.buffer[:9])

        # Check if we have the complete message
        message_size = 9 + length
        if len(self.buffer) < message_size:
            # Read more data until we have the complete message
            while len(self.buffer) < message_size:
                if timeout is not None:
                    readable, _, _ = select.select([self.socket], [], [], timeout)
                    if not readable:
                        raise TimeoutError("Receive timeout")

                try:
                    data = self.socket.recv(4096)
                    if not data:
                        raise ConnectionError("Connection closed by peer")
                    self.buffer += data
                except Exception as e:
                    logger.error(f"Failed to receive data: {e}")
                    raise

        # Extract complete message and update buffer
        message_data = self.buffer[:message_size]
        self.buffer = self.buffer[message_size:]

        try:
            message = TLVMessage.from_bytes(message_data)
            logger.debug(f"Received TLV message: {message}")
            return message
        except Exception as e:
            logger.error(f"Failed to parse TLV message: {e}")
            raise


class TLVServer:
    """Helper class for TLV server operations"""

    def __init__(self, socket):
        self.socket = socket
        self.buffer = b""

    def send_tlv_message(self, message: TLVMessage) -> None:
        """Send a TLV message to the socket

        Args:
            message: TLVMessage to send
        """
        try:
            data = message.to_bytes()
            self.socket.send(data)
            logger.debug(f"Sent TLV message: {message}")
        except Exception as e:
            logger.error(f"Failed to send TLV message: {e}")
            raise

    def receive_tlv_message(self, timeout: Optional[float] = None) -> TLVMessage:
        """Receive a TLV message from the socket

        Args:
            timeout: Optional receive timeout in seconds

        Returns:
            Received TLVMessage
        """
        import select
        import socket

        # Read until we have at least 9 bytes (header)
        while len(self.buffer) < 9:
            if timeout is not None:
                readable, _, _ = select.select([self.socket], [], [], timeout)
                if not readable:
                    raise TimeoutError("Receive timeout")

            try:
                data = self.socket.recv(4096)
                if not data:
                    raise ConnectionError("Connection closed by peer")
                self.buffer += data
            except socket.timeout:
                raise TimeoutError("Receive timeout")
            except Exception as e:
                logger.error(f"Failed to receive data: {e}")
                raise

        # Parse length and sign from header
        length, sign = struct.unpack('!QB', self.buffer[:9])

        # Check if we have the complete message
        message_size = 9 + length
        if len(self.buffer) < message_size:
            # Read more data until we have the complete message
            while len(self.buffer) < message_size:
                if timeout is not None:
                    readable, _, _ = select.select([self.socket], [], [], timeout)
                    if not readable:
                        raise TimeoutError("Receive timeout")

                try:
                    data = self.socket.recv(4096)
                    if not data:
                        raise ConnectionError("Connection closed by peer")
                    self.buffer += data
                except socket.timeout:
                    raise TimeoutError("Receive timeout")
                except Exception as e:
                    logger.error(f"Failed to receive data: {e}")
                    raise

        # Extract complete message and update buffer
        message_data = self.buffer[:message_size]
        self.buffer = self.buffer[message_size:]
        print("-----------")

        try:
            message = TLVMessage.from_bytes(message_data)
            logger.debug(f"Received TLV message: {message}")
            return message
        except Exception as e:
            logger.error(f"Failed to parse TLV message: {e}")
            raise

    def close(self):
        """Close the connection"""
        try:
            self.socket.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
