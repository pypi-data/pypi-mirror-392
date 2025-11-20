"""Type stubs for TextQL Python Client Library"""

from .client import (
    TextQLClient as TextQLClient,
    ChatTools as ChatTools,
    ChatClient as ChatClient,
    ConnectorsClient as ConnectorsClient,
    PlaybooksClient as PlaybooksClient,
)
from .exceptions import (
    TextQLError as TextQLError,
    AuthenticationError as AuthenticationError,
    ConnectionError as ConnectionError,
    InvalidRequestError as InvalidRequestError,
    RateLimitError as RateLimitError,
    NotFoundError as NotFoundError,
    ServerError as ServerError,
)
from .types import (
    StreamResponse as StreamResponse,
    ChatResponse as ChatResponse,
    Connector as Connector,
    Playbook as Playbook,
)
from .platform import chat_pb2 as chat_pb2, chat_pb2_grpc as chat_pb2_grpc
from .platform import connectors_pb2 as connectors_pb2, connectors_pb2_grpc as connectors_pb2_grpc
from .platform import playbooks_pb2 as playbooks_pb2, playbooks_pb2_grpc as playbooks_pb2_grpc

__version__: str

__all__ = [
    "TextQLClient",
    "ChatTools",
    "ChatClient",
    "ConnectorsClient",
    "PlaybooksClient",
    "TextQLError",
    "AuthenticationError",
    "ConnectionError",
    "InvalidRequestError",
    "RateLimitError",
    "NotFoundError",
    "ServerError",
    "StreamResponse",
    "ChatResponse",
    "Connector",
    "Playbook",
]