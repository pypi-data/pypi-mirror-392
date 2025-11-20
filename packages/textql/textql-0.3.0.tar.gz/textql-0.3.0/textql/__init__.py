"""TextQL Python Client Library

Clean, intuitive API for TextQL platform services.

Example:
    from textql import TextQLClient, ChatTools

    client = TextQLClient(
        api_key='your-api-key',
        base_url='https://staging.textql.com'
    )

    tools = ChatTools(
        connector_ids=[513],
        web_search_enabled=True,
        sql_enabled=True,
        python_enabled=True
    )

    # Stream responses
    stream = client.chat.stream(
        question="Tell me about the data",
        tools=tools
    )

    for response in stream:
        if response.HasField('text'):
            print(response.text, end='', flush=True)
"""

__version__ = "0.2.9"

# Main client exports
from .client import TextQLClient, ChatTools, ChatClient, ConnectorsClient, PlaybooksClient

# Exceptions for error handling
from .exceptions import (
    TextQLError,
    AuthenticationError,
    ConnectionError,
    InvalidRequestError,
    RateLimitError,
    NotFoundError,
    ServerError,
)

# Type aliases for better autocomplete
from .types import (
    StreamResponse,
    ChatResponse,
    Connector,
    Playbook,
)

# For advanced users who need direct proto access
from .platform import chat_pb2, chat_pb2_grpc
from .platform import connectors_pb2, connectors_pb2_grpc
from .platform import playbooks_pb2, playbooks_pb2_grpc

__all__ = [
    # Main client API (recommended)
    "TextQLClient",
    "ChatTools",
    "ChatClient",
    "ConnectorsClient",
    "PlaybooksClient",
    # Exceptions
    "TextQLError",
    "AuthenticationError",
    "ConnectionError",
    "InvalidRequestError",
    "RateLimitError",
    "NotFoundError",
    "ServerError",
    # Common types
    "StreamResponse",
    "ChatResponse",
    "Connector",
    "Playbook",
]
