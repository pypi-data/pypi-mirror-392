"""Type aliases and helper types for better IDE autocomplete"""

from typing import TypeAlias
from .platform import chat_pb2, connectors_pb2, playbooks_pb2

# Chat types
StreamResponse: TypeAlias = chat_pb2.StreamResponse
ChatResponse: TypeAlias = chat_pb2.ChatResponse
GetChatResponse: TypeAlias = "chat_pb2.GetChatResponse"
CancelStreamResponse: TypeAlias = "chat_pb2.CancelStreamResponse"

# Connector types
Connector: TypeAlias = connectors_pb2.Connector
ListConnectorsResponse: TypeAlias = connectors_pb2.ListConnectorsResponse

# Playbook types
Playbook: TypeAlias = playbooks_pb2.Playbook
PlaybookStatus: TypeAlias = "playbooks_pb2.PlaybookStatus"
CreatePlaybookResponse: TypeAlias = playbooks_pb2.CreatePlaybookResponse
GetPlaybookResponse: TypeAlias = playbooks_pb2.GetPlaybookResponse
ListPlaybooksResponse: TypeAlias = playbooks_pb2.ListPlaybooksResponse
UpdatePlaybookResponse: TypeAlias = playbooks_pb2.UpdatePlaybookResponse
DeletePlaybookResponse: TypeAlias = playbooks_pb2.DeletePlaybookResponse

__all__ = [
    "StreamResponse",
    "ChatResponse",
    "GetChatResponse",
    "CancelStreamResponse",
    "Connector",
    "ListConnectorsResponse",
    "Playbook",
    "PlaybookStatus",
    "CreatePlaybookResponse",
    "GetPlaybookResponse",
    "ListPlaybooksResponse",
    "UpdatePlaybookResponse",
    "DeletePlaybookResponse",
]
