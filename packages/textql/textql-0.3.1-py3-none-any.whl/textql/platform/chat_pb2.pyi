from public import chat_pb2 as _chat_pb2
from public import paradigm_pb2 as _paradigm_pb2
from public import cells_pb2 as _cells_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUERY_STATUS_UNKNOWN: _ClassVar[ChatStatus]
    QUERY_STATUS_COMPLETED: _ClassVar[ChatStatus]
    QUERY_STATUS_FAILED: _ClassVar[ChatStatus]
    QUERY_STATUS_CANCELLED: _ClassVar[ChatStatus]
    QUERY_STATUS_IN_PROGRESS: _ClassVar[ChatStatus]

class StopReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOP_REASON_UNKNOWN: _ClassVar[StopReason]
    STOP_REASON_END_TURN: _ClassVar[StopReason]
    STOP_REASON_MAX_TOKENS: _ClassVar[StopReason]
    STOP_REASON_TOOL_USE: _ClassVar[StopReason]
    STOP_REASON_STOP_SEQUENCE: _ClassVar[StopReason]
    STOP_REASON_REFUSAL: _ClassVar[StopReason]
QUERY_STATUS_UNKNOWN: ChatStatus
QUERY_STATUS_COMPLETED: ChatStatus
QUERY_STATUS_FAILED: ChatStatus
QUERY_STATUS_CANCELLED: ChatStatus
QUERY_STATUS_IN_PROGRESS: ChatStatus
STOP_REASON_UNKNOWN: StopReason
STOP_REASON_END_TURN: StopReason
STOP_REASON_MAX_TOKENS: StopReason
STOP_REASON_TOOL_USE: StopReason
STOP_REASON_STOP_SEQUENCE: StopReason
STOP_REASON_REFUSAL: StopReason

class ChatTools(_message.Message):
    __slots__ = ("connector_ids", "web_search_enabled", "sql_enabled", "ontology_enabled", "experimental_enabled", "tableau_enabled", "auto_approve_enabled", "python_enabled", "streamlit_enabled", "google_drive_enabled", "powerbi_enabled")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    WEB_SEARCH_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SQL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AUTO_APPROVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PYTHON_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAMLIT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    POWERBI_ENABLED_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    web_search_enabled: bool
    sql_enabled: bool
    ontology_enabled: bool
    experimental_enabled: bool
    tableau_enabled: bool
    auto_approve_enabled: bool
    python_enabled: bool
    streamlit_enabled: bool
    google_drive_enabled: bool
    powerbi_enabled: bool
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., web_search_enabled: bool = ..., sql_enabled: bool = ..., ontology_enabled: bool = ..., experimental_enabled: bool = ..., tableau_enabled: bool = ..., auto_approve_enabled: bool = ..., python_enabled: bool = ..., streamlit_enabled: bool = ..., google_drive_enabled: bool = ..., powerbi_enabled: bool = ...) -> None: ...

class ChatRequest(_message.Message):
    __slots__ = ("question", "chat_id", "tools")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    question: str
    chat_id: str
    tools: ChatTools
    def __init__(self, question: _Optional[str] = ..., chat_id: _Optional[str] = ..., tools: _Optional[_Union[ChatTools, _Mapping]] = ...) -> None: ...

class StreamRequest(_message.Message):
    __slots__ = ("question", "chat_id", "tools")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    question: str
    chat_id: str
    tools: ChatTools
    def __init__(self, question: _Optional[str] = ..., chat_id: _Optional[str] = ..., tools: _Optional[_Union[ChatTools, _Mapping]] = ...) -> None: ...

class ChatUsage(_message.Message):
    __slots__ = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "context_window_used")
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_CREATION_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_READ_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    REASONING_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_WINDOW_USED_FIELD_NUMBER: _ClassVar[int]
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int
    context_window_used: float
    def __init__(self, input_tokens: _Optional[int] = ..., cache_creation_input_tokens: _Optional[int] = ..., cache_read_input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., reasoning_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ..., context_window_used: _Optional[float] = ...) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ("id", "created_at", "error", "model", "response", "chat_id", "assets")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    error: str
    model: str
    response: str
    chat_id: str
    assets: _containers.RepeatedCompositeFieldContainer[_cells_pb2.PreviewCell]
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[str] = ..., model: _Optional[str] = ..., response: _Optional[str] = ..., chat_id: _Optional[str] = ..., assets: _Optional[_Iterable[_Union[_cells_pb2.PreviewCell, _Mapping]]] = ...) -> None: ...

class StreamResponse(_message.Message):
    __slots__ = ("metadata", "cell", "text", "preview")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CELL_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    metadata: StreamChatMetadata
    cell: _chat_pb2.Cell
    text: str
    preview: _cells_pb2.PreviewCell
    def __init__(self, metadata: _Optional[_Union[StreamChatMetadata, _Mapping]] = ..., cell: _Optional[_Union[_chat_pb2.Cell, _Mapping]] = ..., text: _Optional[str] = ..., preview: _Optional[_Union[_cells_pb2.PreviewCell, _Mapping]] = ...) -> None: ...

class StreamChatMetadata(_message.Message):
    __slots__ = ("id", "created_at", "model", "chat_id", "metadata", "is_continuation", "usage", "status", "error")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    IS_CONTINUATION_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    model: str
    chat_id: str
    metadata: _containers.ScalarMap[str, str]
    is_continuation: bool
    usage: ChatUsage
    status: ChatStatus
    error: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., chat_id: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., is_continuation: bool = ..., usage: _Optional[_Union[ChatUsage, _Mapping]] = ..., status: _Optional[_Union[ChatStatus, str]] = ..., error: _Optional[str] = ...) -> None: ...
