from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MCPTransportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MCP_TRANSPORT_TYPE_UNSPECIFIED: _ClassVar[MCPTransportType]
    SSE: _ClassVar[MCPTransportType]
    HTTP: _ClassVar[MCPTransportType]

class MCPError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MCP_ERROR_UNSPECIFIED: _ClassVar[MCPError]
    MCP_ERROR_INVALID_TOKEN: _ClassVar[MCPError]
    MCP_ERROR_AUTHENTICATION_REQUIRED: _ClassVar[MCPError]
    MCP_ERROR_UNSUPPORTED_PROTOCOL_VERSION: _ClassVar[MCPError]
    MCP_ERROR_CLIENT_NOT_INITIALIZED: _ClassVar[MCPError]
    MCP_ERROR_URL_REQUIRED: _ClassVar[MCPError]
    MCP_ERROR_UNSUPPORTED_TRANSPORT_TYPE: _ClassVar[MCPError]
    MCP_ERROR_SERVER_NOT_FOUND: _ClassVar[MCPError]
MCP_TRANSPORT_TYPE_UNSPECIFIED: MCPTransportType
SSE: MCPTransportType
HTTP: MCPTransportType
MCP_ERROR_UNSPECIFIED: MCPError
MCP_ERROR_INVALID_TOKEN: MCPError
MCP_ERROR_AUTHENTICATION_REQUIRED: MCPError
MCP_ERROR_UNSUPPORTED_PROTOCOL_VERSION: MCPError
MCP_ERROR_CLIENT_NOT_INITIALIZED: MCPError
MCP_ERROR_URL_REQUIRED: MCPError
MCP_ERROR_UNSUPPORTED_TRANSPORT_TYPE: MCPError
MCP_ERROR_SERVER_NOT_FOUND: MCPError

class HttpConfig(_message.Message):
    __slots__ = ("url", "headers")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    url: str
    headers: _containers.ScalarMap[str, str]
    def __init__(self, url: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SseConfig(_message.Message):
    __slots__ = ("url", "headers")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    url: str
    headers: _containers.ScalarMap[str, str]
    def __init__(self, url: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class MCPServer(_message.Message):
    __slots__ = ("id", "name", "transport", "http_config", "sse_config", "member_id", "organization_id", "created_at", "updated_at", "enabled")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    HTTP_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SSE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    transport: MCPTransportType
    http_config: HttpConfig
    sse_config: SseConfig
    member_id: str
    organization_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    enabled: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., transport: _Optional[_Union[MCPTransportType, str]] = ..., http_config: _Optional[_Union[HttpConfig, _Mapping]] = ..., sse_config: _Optional[_Union[SseConfig, _Mapping]] = ..., member_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., enabled: bool = ...) -> None: ...

class MCPTool(_message.Message):
    __slots__ = ("name", "description", "schema")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    schema: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., schema: _Optional[str] = ...) -> None: ...

class MCPServerWithTools(_message.Message):
    __slots__ = ("mcp_server", "tools", "error")
    MCP_SERVER_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    mcp_server: MCPServer
    tools: _containers.RepeatedCompositeFieldContainer[MCPTool]
    error: MCPError
    def __init__(self, mcp_server: _Optional[_Union[MCPServer, _Mapping]] = ..., tools: _Optional[_Iterable[_Union[MCPTool, _Mapping]]] = ..., error: _Optional[_Union[MCPError, str]] = ...) -> None: ...

class GetMCPServersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMCPServersResponse(_message.Message):
    __slots__ = ("mcp_servers",)
    MCP_SERVERS_FIELD_NUMBER: _ClassVar[int]
    mcp_servers: _containers.RepeatedCompositeFieldContainer[MCPServerWithTools]
    def __init__(self, mcp_servers: _Optional[_Iterable[_Union[MCPServerWithTools, _Mapping]]] = ...) -> None: ...

class UpsertMCPServersRequest(_message.Message):
    __slots__ = ("mcp_servers",)
    MCP_SERVERS_FIELD_NUMBER: _ClassVar[int]
    mcp_servers: _containers.RepeatedCompositeFieldContainer[MCPServer]
    def __init__(self, mcp_servers: _Optional[_Iterable[_Union[MCPServer, _Mapping]]] = ...) -> None: ...

class UpsertMCPServersResponse(_message.Message):
    __slots__ = ("mcp_servers",)
    MCP_SERVERS_FIELD_NUMBER: _ClassVar[int]
    mcp_servers: _containers.RepeatedCompositeFieldContainer[MCPServerWithTools]
    def __init__(self, mcp_servers: _Optional[_Iterable[_Union[MCPServerWithTools, _Mapping]]] = ...) -> None: ...

class ToggleMCPServerRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ToggleMCPServerResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ClearOAuthTokenRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    def __init__(self, server_id: _Optional[str] = ...) -> None: ...

class ClearOAuthTokenResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class DeleteMCPServerRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteMCPServerResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class InitiateOAuthFlowRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    def __init__(self, server_id: _Optional[str] = ...) -> None: ...

class InitiateOAuthFlowResponse(_message.Message):
    __slots__ = ("success", "error", "authorization_url")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_URL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    authorization_url: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., authorization_url: _Optional[str] = ...) -> None: ...

class HandleOAuthCallbackRequest(_message.Message):
    __slots__ = ("server_id", "code", "state")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    code: str
    state: str
    def __init__(self, server_id: _Optional[str] = ..., code: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class HandleOAuthCallbackResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
