from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from public import cells_pb2 as _cells_pb2
from public import dataset_pb2 as _dataset_pb2
from public import paradigm_pb2 as _paradigm_pb2
from public import identity_pb2 as _identity_pb2
from public import context_prompts_pb2 as _context_prompts_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LlmModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODEL_UNKNOWN: _ClassVar[LlmModel]
    MODEL_DEFAULT_SMALL: _ClassVar[LlmModel]
    MODEL_DEFAULT: _ClassVar[LlmModel]
    MODEL_DEFAULT_LARGE: _ClassVar[LlmModel]
    MODEL_DEFAULT_REASONING: _ClassVar[LlmModel]
    MODEL_HAIKU_3: _ClassVar[LlmModel]
    MODEL_HAIKU_3_5: _ClassVar[LlmModel]
    MODEL_SONNET_3_5: _ClassVar[LlmModel]
    MODEL_SONNET_3_6: _ClassVar[LlmModel]
    MODEL_SONNET_3_7: _ClassVar[LlmModel]
    MODEL_SONNET_4: _ClassVar[LlmModel]
    MODEL_OPUS_4: _ClassVar[LlmModel]
    MODEL_SONNET_4_5: _ClassVar[LlmModel]
    MODEL_HAIKU_4_5: _ClassVar[LlmModel]
    MODEL_GPT_4: _ClassVar[LlmModel]
    MODEL_GPT_4_TURBO: _ClassVar[LlmModel]
    MODEL_GPT_4O: _ClassVar[LlmModel]
    MODEL_GPT_4_1: _ClassVar[LlmModel]
    MODEL_GPT_4_1_MINI: _ClassVar[LlmModel]
    MODEL_GPT_4_1_NANO: _ClassVar[LlmModel]
    MODEL_O_1: _ClassVar[LlmModel]
    MODEL_O_1_MINI: _ClassVar[LlmModel]
    MODEL_O_3: _ClassVar[LlmModel]
    MODEL_O_3_MINI: _ClassVar[LlmModel]
    MODEL_O_4_MINI: _ClassVar[LlmModel]
    MODEL_GPT_5: _ClassVar[LlmModel]
    MODEL_KIMI_K2_INSTRUCT: _ClassVar[LlmModel]
    MODEL_QWEN3_CODER: _ClassVar[LlmModel]
    MODEL_QWEN3_CODER_SMALL: _ClassVar[LlmModel]
    MODEL_GPT_OSS: _ClassVar[LlmModel]
    MODEL_GPT_OSS_SMALL: _ClassVar[LlmModel]
    MODEL_GLM_4_5: _ClassVar[LlmModel]
    MODEL_GLM_4_6: _ClassVar[LlmModel]
    MODEL_KIMI_K2_THINKING: _ClassVar[LlmModel]

class CellLifecycle(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIFECYCLE_UNKNOWN: _ClassVar[CellLifecycle]
    LIFECYCLE_CREATING: _ClassVar[CellLifecycle]
    LIFECYCLE_CREATED: _ClassVar[CellLifecycle]
    LIFECYCLE_EXECUTING: _ClassVar[CellLifecycle]
    LIFECYCLE_EXECUTED: _ClassVar[CellLifecycle]

class ChatSortField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHAT_SORT_FIELD_UNKNOWN: _ClassVar[ChatSortField]
    CHAT_SORT_FIELD_NAME: _ClassVar[ChatSortField]
    CHAT_SORT_FIELD_CREATED_AT: _ClassVar[ChatSortField]
    CHAT_SORT_FIELD_UPDATED_AT: _ClassVar[ChatSortField]

class ChatSortDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHAT_SORT_DIRECTION_UNKNOWN: _ClassVar[ChatSortDirection]
    CHAT_SORT_DIRECTION_ASC: _ClassVar[ChatSortDirection]
    CHAT_SORT_DIRECTION_DESC: _ClassVar[ChatSortDirection]

class HealthStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNKNOWN: _ClassVar[HealthStatus]
    STATUS_HEALTHY: _ClassVar[HealthStatus]
    STATUS_MINOR: _ClassVar[HealthStatus]
    STATUS_MAJOR: _ClassVar[HealthStatus]
    STATUS_CRITICAL: _ClassVar[HealthStatus]

class StreamlitHealthStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAMLIT_HEALTH_STATUS_UNKNOWN: _ClassVar[StreamlitHealthStatus]
    STREAMLIT_HEALTH_STATUS_HEALTHY: _ClassVar[StreamlitHealthStatus]
    STREAMLIT_HEALTH_STATUS_RESTORING: _ClassVar[StreamlitHealthStatus]
    STREAMLIT_HEALTH_STATUS_FAILED: _ClassVar[StreamlitHealthStatus]
MODEL_UNKNOWN: LlmModel
MODEL_DEFAULT_SMALL: LlmModel
MODEL_DEFAULT: LlmModel
MODEL_DEFAULT_LARGE: LlmModel
MODEL_DEFAULT_REASONING: LlmModel
MODEL_HAIKU_3: LlmModel
MODEL_HAIKU_3_5: LlmModel
MODEL_SONNET_3_5: LlmModel
MODEL_SONNET_3_6: LlmModel
MODEL_SONNET_3_7: LlmModel
MODEL_SONNET_4: LlmModel
MODEL_OPUS_4: LlmModel
MODEL_SONNET_4_5: LlmModel
MODEL_HAIKU_4_5: LlmModel
MODEL_GPT_4: LlmModel
MODEL_GPT_4_TURBO: LlmModel
MODEL_GPT_4O: LlmModel
MODEL_GPT_4_1: LlmModel
MODEL_GPT_4_1_MINI: LlmModel
MODEL_GPT_4_1_NANO: LlmModel
MODEL_O_1: LlmModel
MODEL_O_1_MINI: LlmModel
MODEL_O_3: LlmModel
MODEL_O_3_MINI: LlmModel
MODEL_O_4_MINI: LlmModel
MODEL_GPT_5: LlmModel
MODEL_KIMI_K2_INSTRUCT: LlmModel
MODEL_QWEN3_CODER: LlmModel
MODEL_QWEN3_CODER_SMALL: LlmModel
MODEL_GPT_OSS: LlmModel
MODEL_GPT_OSS_SMALL: LlmModel
MODEL_GLM_4_5: LlmModel
MODEL_GLM_4_6: LlmModel
MODEL_KIMI_K2_THINKING: LlmModel
LIFECYCLE_UNKNOWN: CellLifecycle
LIFECYCLE_CREATING: CellLifecycle
LIFECYCLE_CREATED: CellLifecycle
LIFECYCLE_EXECUTING: CellLifecycle
LIFECYCLE_EXECUTED: CellLifecycle
CHAT_SORT_FIELD_UNKNOWN: ChatSortField
CHAT_SORT_FIELD_NAME: ChatSortField
CHAT_SORT_FIELD_CREATED_AT: ChatSortField
CHAT_SORT_FIELD_UPDATED_AT: ChatSortField
CHAT_SORT_DIRECTION_UNKNOWN: ChatSortDirection
CHAT_SORT_DIRECTION_ASC: ChatSortDirection
CHAT_SORT_DIRECTION_DESC: ChatSortDirection
STATUS_UNKNOWN: HealthStatus
STATUS_HEALTHY: HealthStatus
STATUS_MINOR: HealthStatus
STATUS_MAJOR: HealthStatus
STATUS_CRITICAL: HealthStatus
STREAMLIT_HEALTH_STATUS_UNKNOWN: StreamlitHealthStatus
STREAMLIT_HEALTH_STATUS_HEALTHY: StreamlitHealthStatus
STREAMLIT_HEALTH_STATUS_RESTORING: StreamlitHealthStatus
STREAMLIT_HEALTH_STATUS_FAILED: StreamlitHealthStatus

class Chat(_message.Message):
    __slots__ = ("id", "paradigm", "model", "timestamp", "org_id", "member_id", "summary", "playbook_id", "research", "creator_email", "api_key_client_id", "updated_at", "is_bookmarked", "preferred_provider", "template_data_id", "batch_run_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    CREATOR_EMAIL_FIELD_NUMBER: _ClassVar[int]
    API_KEY_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_BOOKMARKED_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DATA_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    paradigm: _paradigm_pb2.Paradigm
    model: LlmModel
    timestamp: _timestamp_pb2.Timestamp
    org_id: str
    member_id: str
    summary: str
    playbook_id: str
    research: bool
    creator_email: str
    api_key_client_id: str
    updated_at: _timestamp_pb2.Timestamp
    is_bookmarked: bool
    preferred_provider: str
    template_data_id: str
    batch_run_id: str
    def __init__(self, id: _Optional[str] = ..., paradigm: _Optional[_Union[_paradigm_pb2.Paradigm, _Mapping]] = ..., model: _Optional[_Union[LlmModel, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ..., member_id: _Optional[str] = ..., summary: _Optional[str] = ..., playbook_id: _Optional[str] = ..., research: bool = ..., creator_email: _Optional[str] = ..., api_key_client_id: _Optional[str] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_bookmarked: bool = ..., preferred_provider: _Optional[str] = ..., template_data_id: _Optional[str] = ..., batch_run_id: _Optional[str] = ...) -> None: ...

class Cell(_message.Message):
    __slots__ = ("id", "timestamp", "complete", "generated", "lifecycle", "tool_call_id", "exec_error", "sender_member_id", "md_cell", "py_cell", "sql_cell", "ans_cell", "document_cell", "ws_cell", "report_cell", "tabular_file_cell", "status_cell", "metrics_cell", "summary_cell", "tableau_cell", "tableau_sql_cell", "context_prompt_editor_cell", "ontology_editor_cell", "image_cell", "text_cell", "mcp_tool_cell", "preview_cell", "playbook_editor_cell", "streamlit_cell", "google_drive_content_cell", "google_drive_search_cell", "powerbi_cell", "powerbi_dax_cell", "form_editor_cell", "tableau_search_fields_cell", "report_history_cell")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    EXEC_ERROR_FIELD_NUMBER: _ClassVar[int]
    SENDER_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MD_CELL_FIELD_NUMBER: _ClassVar[int]
    PY_CELL_FIELD_NUMBER: _ClassVar[int]
    SQL_CELL_FIELD_NUMBER: _ClassVar[int]
    ANS_CELL_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_CELL_FIELD_NUMBER: _ClassVar[int]
    WS_CELL_FIELD_NUMBER: _ClassVar[int]
    REPORT_CELL_FIELD_NUMBER: _ClassVar[int]
    TABULAR_FILE_CELL_FIELD_NUMBER: _ClassVar[int]
    STATUS_CELL_FIELD_NUMBER: _ClassVar[int]
    METRICS_CELL_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_CELL_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_CELL_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_SQL_CELL_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PROMPT_EDITOR_CELL_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_EDITOR_CELL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_CELL_FIELD_NUMBER: _ClassVar[int]
    TEXT_CELL_FIELD_NUMBER: _ClassVar[int]
    MCP_TOOL_CELL_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_CELL_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_EDITOR_CELL_FIELD_NUMBER: _ClassVar[int]
    STREAMLIT_CELL_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_CONTENT_CELL_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_SEARCH_CELL_FIELD_NUMBER: _ClassVar[int]
    POWERBI_CELL_FIELD_NUMBER: _ClassVar[int]
    POWERBI_DAX_CELL_FIELD_NUMBER: _ClassVar[int]
    FORM_EDITOR_CELL_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_SEARCH_FIELDS_CELL_FIELD_NUMBER: _ClassVar[int]
    REPORT_HISTORY_CELL_FIELD_NUMBER: _ClassVar[int]
    id: str
    timestamp: _timestamp_pb2.Timestamp
    complete: bool
    generated: bool
    lifecycle: CellLifecycle
    tool_call_id: str
    exec_error: str
    sender_member_id: str
    md_cell: _cells_pb2.MarkdownCell
    py_cell: _cells_pb2.PythonCell
    sql_cell: _cells_pb2.SQLCell
    ans_cell: _cells_pb2.AnswerCell
    document_cell: _cells_pb2.DocumentCell
    ws_cell: _cells_pb2.WebSearchCell
    report_cell: _cells_pb2.ReportCell
    tabular_file_cell: _cells_pb2.TabularFileCell
    status_cell: _cells_pb2.StatusCell
    metrics_cell: _cells_pb2.MetricsCell
    summary_cell: _cells_pb2.SummaryCell
    tableau_cell: _cells_pb2.TableauCell
    tableau_sql_cell: _cells_pb2.TableauSQLCell
    context_prompt_editor_cell: _cells_pb2.ContextPromptEditorCell
    ontology_editor_cell: _cells_pb2.OntologyEditorCell
    image_cell: _cells_pb2.ImageCell
    text_cell: _cells_pb2.TextCell
    mcp_tool_cell: _cells_pb2.MCPToolCell
    preview_cell: _cells_pb2.PreviewCell
    playbook_editor_cell: _cells_pb2.PlaybookEditorCell
    streamlit_cell: _cells_pb2.StreamlitCell
    google_drive_content_cell: _cells_pb2.GoogleDriveContentCell
    google_drive_search_cell: _cells_pb2.GoogleDriveSearchCell
    powerbi_cell: _cells_pb2.PowerBICell
    powerbi_dax_cell: _cells_pb2.PowerBIDAXCell
    form_editor_cell: _cells_pb2.FormEditorCell
    tableau_search_fields_cell: _cells_pb2.TableauSearchFieldsCell
    report_history_cell: _cells_pb2.ReportHistoryCell
    def __init__(self, id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., complete: bool = ..., generated: bool = ..., lifecycle: _Optional[_Union[CellLifecycle, str]] = ..., tool_call_id: _Optional[str] = ..., exec_error: _Optional[str] = ..., sender_member_id: _Optional[str] = ..., md_cell: _Optional[_Union[_cells_pb2.MarkdownCell, _Mapping]] = ..., py_cell: _Optional[_Union[_cells_pb2.PythonCell, _Mapping]] = ..., sql_cell: _Optional[_Union[_cells_pb2.SQLCell, _Mapping]] = ..., ans_cell: _Optional[_Union[_cells_pb2.AnswerCell, _Mapping]] = ..., document_cell: _Optional[_Union[_cells_pb2.DocumentCell, _Mapping]] = ..., ws_cell: _Optional[_Union[_cells_pb2.WebSearchCell, _Mapping]] = ..., report_cell: _Optional[_Union[_cells_pb2.ReportCell, _Mapping]] = ..., tabular_file_cell: _Optional[_Union[_cells_pb2.TabularFileCell, _Mapping]] = ..., status_cell: _Optional[_Union[_cells_pb2.StatusCell, _Mapping]] = ..., metrics_cell: _Optional[_Union[_cells_pb2.MetricsCell, _Mapping]] = ..., summary_cell: _Optional[_Union[_cells_pb2.SummaryCell, _Mapping]] = ..., tableau_cell: _Optional[_Union[_cells_pb2.TableauCell, _Mapping]] = ..., tableau_sql_cell: _Optional[_Union[_cells_pb2.TableauSQLCell, _Mapping]] = ..., context_prompt_editor_cell: _Optional[_Union[_cells_pb2.ContextPromptEditorCell, _Mapping]] = ..., ontology_editor_cell: _Optional[_Union[_cells_pb2.OntologyEditorCell, _Mapping]] = ..., image_cell: _Optional[_Union[_cells_pb2.ImageCell, _Mapping]] = ..., text_cell: _Optional[_Union[_cells_pb2.TextCell, _Mapping]] = ..., mcp_tool_cell: _Optional[_Union[_cells_pb2.MCPToolCell, _Mapping]] = ..., preview_cell: _Optional[_Union[_cells_pb2.PreviewCell, _Mapping]] = ..., playbook_editor_cell: _Optional[_Union[_cells_pb2.PlaybookEditorCell, _Mapping]] = ..., streamlit_cell: _Optional[_Union[_cells_pb2.StreamlitCell, _Mapping]] = ..., google_drive_content_cell: _Optional[_Union[_cells_pb2.GoogleDriveContentCell, _Mapping]] = ..., google_drive_search_cell: _Optional[_Union[_cells_pb2.GoogleDriveSearchCell, _Mapping]] = ..., powerbi_cell: _Optional[_Union[_cells_pb2.PowerBICell, _Mapping]] = ..., powerbi_dax_cell: _Optional[_Union[_cells_pb2.PowerBIDAXCell, _Mapping]] = ..., form_editor_cell: _Optional[_Union[_cells_pb2.FormEditorCell, _Mapping]] = ..., tableau_search_fields_cell: _Optional[_Union[_cells_pb2.TableauSearchFieldsCell, _Mapping]] = ..., report_history_cell: _Optional[_Union[_cells_pb2.ReportHistoryCell, _Mapping]] = ...) -> None: ...

class LlmCompletionParameters(_message.Message):
    __slots__ = ("started_at", "completed_at", "member_id", "llm_model", "llm_provider", "system_messages", "messages", "tools", "tool_choice", "thinking", "max_tokens", "temperature", "stop_sequences", "service_tier", "custom_settings")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    LLM_MODEL_FIELD_NUMBER: _ClassVar[int]
    LLM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    TOOL_CHOICE_FIELD_NUMBER: _ClassVar[int]
    THINKING_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    STOP_SEQUENCES_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    member_id: str
    llm_model: str
    llm_provider: str
    system_messages: _containers.RepeatedScalarFieldContainer[str]
    messages: _containers.RepeatedScalarFieldContainer[str]
    tools: _containers.RepeatedScalarFieldContainer[str]
    tool_choice: str
    thinking: str
    max_tokens: int
    temperature: float
    stop_sequences: _containers.RepeatedScalarFieldContainer[str]
    service_tier: str
    custom_settings: str
    def __init__(self, started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., member_id: _Optional[str] = ..., llm_model: _Optional[str] = ..., llm_provider: _Optional[str] = ..., system_messages: _Optional[_Iterable[str]] = ..., messages: _Optional[_Iterable[str]] = ..., tools: _Optional[_Iterable[str]] = ..., tool_choice: _Optional[str] = ..., thinking: _Optional[str] = ..., max_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., stop_sequences: _Optional[_Iterable[str]] = ..., service_tier: _Optional[str] = ..., custom_settings: _Optional[str] = ...) -> None: ...

class CreateRequest(_message.Message):
    __slots__ = ("paradigm", "model", "message", "playbook_id", "research")
    PARADIGM_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    paradigm: _paradigm_pb2.Paradigm
    model: LlmModel
    message: str
    playbook_id: str
    research: bool
    def __init__(self, paradigm: _Optional[_Union[_paradigm_pb2.Paradigm, _Mapping]] = ..., model: _Optional[_Union[LlmModel, str]] = ..., message: _Optional[str] = ..., playbook_id: _Optional[str] = ..., research: bool = ...) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = ("chat",)
    CHAT_FIELD_NUMBER: _ClassVar[int]
    chat: Chat
    def __init__(self, chat: _Optional[_Union[Chat, _Mapping]] = ...) -> None: ...

class UpdateChatRequest(_message.Message):
    __slots__ = ("chat_id", "research", "summary")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    research: bool
    summary: str
    def __init__(self, chat_id: _Optional[str] = ..., research: bool = ..., summary: _Optional[str] = ...) -> None: ...

class UpdateChatResponse(_message.Message):
    __slots__ = ("chat",)
    CHAT_FIELD_NUMBER: _ClassVar[int]
    chat: Chat
    def __init__(self, chat: _Optional[_Union[Chat, _Mapping]] = ...) -> None: ...

class DeleteChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class RunChatRequest(_message.Message):
    __slots__ = ("chat_id", "latest_complete_cell_id", "research")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    LATEST_COMPLETE_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    latest_complete_cell_id: str
    research: bool
    def __init__(self, chat_id: _Optional[str] = ..., latest_complete_cell_id: _Optional[str] = ..., research: bool = ...) -> None: ...

class RunChatResponse(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedCompositeFieldContainer[Cell]
    def __init__(self, cells: _Optional[_Iterable[_Union[Cell, _Mapping]]] = ...) -> None: ...

class CancelStreamRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class CancelStreamResponse(_message.Message):
    __slots__ = ("exists",)
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    exists: bool
    def __init__(self, exists: bool = ...) -> None: ...

class SendRequest(_message.Message):
    __slots__ = ("chat_id", "message", "image_urls", "message_id")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URLS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    message: str
    image_urls: _containers.RepeatedScalarFieldContainer[str]
    message_id: str
    def __init__(self, chat_id: _Optional[str] = ..., message: _Optional[str] = ..., image_urls: _Optional[_Iterable[str]] = ..., message_id: _Optional[str] = ...) -> None: ...

class SendResponse(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    def __init__(self, cell_id: _Optional[str] = ...) -> None: ...

class AttachDatasetRequest(_message.Message):
    __slots__ = ("chat_id", "dataset_id")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    dataset_id: str
    def __init__(self, chat_id: _Optional[str] = ..., dataset_id: _Optional[str] = ...) -> None: ...

class AttachDatasetResponse(_message.Message):
    __slots__ = ("cell", "dataset")
    CELL_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    cell: Cell
    dataset: _dataset_pb2.Dataset
    def __init__(self, cell: _Optional[_Union[Cell, _Mapping]] = ..., dataset: _Optional[_Union[_dataset_pb2.Dataset, _Mapping]] = ...) -> None: ...

class HistoryRequest(_message.Message):
    __slots__ = ("chat_id", "limit", "skip")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    limit: int
    skip: int
    def __init__(self, chat_id: _Optional[str] = ..., limit: _Optional[int] = ..., skip: _Optional[int] = ...) -> None: ...

class HistoryResponse(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedCompositeFieldContainer[Cell]
    def __init__(self, cells: _Optional[_Iterable[_Union[Cell, _Mapping]]] = ...) -> None: ...

class GetAPIChatAnswerRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class GetAPIChatAnswerResponse(_message.Message):
    __slots__ = ("answer", "complete", "error")
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    answer: str
    complete: bool
    error: str
    def __init__(self, answer: _Optional[str] = ..., complete: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetChatsRequest(_message.Message):
    __slots__ = ("member_only", "search_term", "limit", "offset", "creator_member_id", "sort_by", "sort_direction", "bookmarked_only")
    MEMBER_ONLY_FIELD_NUMBER: _ClassVar[int]
    SEARCH_TERM_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    CREATOR_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    BOOKMARKED_ONLY_FIELD_NUMBER: _ClassVar[int]
    member_only: bool
    search_term: str
    limit: int
    offset: int
    creator_member_id: str
    sort_by: ChatSortField
    sort_direction: ChatSortDirection
    bookmarked_only: bool
    def __init__(self, member_only: bool = ..., search_term: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., creator_member_id: _Optional[str] = ..., sort_by: _Optional[_Union[ChatSortField, str]] = ..., sort_direction: _Optional[_Union[ChatSortDirection, str]] = ..., bookmarked_only: bool = ...) -> None: ...

class GetChatsResponse(_message.Message):
    __slots__ = ("chats", "total_count")
    CHATS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    chats: _containers.RepeatedCompositeFieldContainer[Chat]
    total_count: int
    def __init__(self, chats: _Optional[_Iterable[_Union[Chat, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("role", "content", "created_at")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, role: _Optional[str] = ..., content: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetChatResponse(_message.Message):
    __slots__ = ("chat", "messages", "assets")
    CHAT_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    chat: Chat
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    assets: _containers.RepeatedCompositeFieldContainer[_cells_pb2.PreviewCell]
    def __init__(self, chat: _Optional[_Union[Chat, _Mapping]] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., assets: _Optional[_Iterable[_Union[_cells_pb2.PreviewCell, _Mapping]]] = ...) -> None: ...

class GetPlaybookChatsRequest(_message.Message):
    __slots__ = ("playbook_id", "limit", "skip")
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    limit: int
    skip: int
    def __init__(self, playbook_id: _Optional[str] = ..., limit: _Optional[int] = ..., skip: _Optional[int] = ...) -> None: ...

class GetPlaybookChatsResponse(_message.Message):
    __slots__ = ("chats",)
    CHATS_FIELD_NUMBER: _ClassVar[int]
    chats: _containers.RepeatedCompositeFieldContainer[Chat]
    def __init__(self, chats: _Optional[_Iterable[_Union[Chat, _Mapping]]] = ...) -> None: ...

class GetCompletionParametersRequest(_message.Message):
    __slots__ = ("chat_id", "cell_id")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    cell_id: str
    def __init__(self, chat_id: _Optional[str] = ..., cell_id: _Optional[str] = ...) -> None: ...

class CheckChatPermissionsRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class CheckChatPermissionsResponse(_message.Message):
    __slots__ = ("has_write_permission", "has_read_permission", "connector_id", "ontology_id", "connector_ids", "ontology_ids")
    HAS_WRITE_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    HAS_READ_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_IDS_FIELD_NUMBER: _ClassVar[int]
    has_write_permission: bool
    has_read_permission: bool
    connector_id: int
    ontology_id: int
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    ontology_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, has_write_permission: bool = ..., has_read_permission: bool = ..., connector_id: _Optional[int] = ..., ontology_id: _Optional[int] = ..., connector_ids: _Optional[_Iterable[int]] = ..., ontology_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class GetCompletionParametersResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: LlmCompletionParameters
    def __init__(self, params: _Optional[_Union[LlmCompletionParameters, _Mapping]] = ...) -> None: ...

class CheckHealthRequest(_message.Message):
    __slots__ = ("model", "functional")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONAL_FIELD_NUMBER: _ClassVar[int]
    model: LlmModel
    functional: bool
    def __init__(self, model: _Optional[_Union[LlmModel, str]] = ..., functional: bool = ...) -> None: ...

class CheckHealthResponse(_message.Message):
    __slots__ = ("llm_status", "web_status", "ontology_status", "valkey_status", "tableau_status", "sandbox_status", "llm_execution_status", "sandbox_execution_status")
    LLM_STATUS_FIELD_NUMBER: _ClassVar[int]
    WEB_STATUS_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_STATUS_FIELD_NUMBER: _ClassVar[int]
    VALKEY_STATUS_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_STATUS_FIELD_NUMBER: _ClassVar[int]
    SANDBOX_STATUS_FIELD_NUMBER: _ClassVar[int]
    LLM_EXECUTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    SANDBOX_EXECUTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    llm_status: HealthStatus
    web_status: HealthStatus
    ontology_status: HealthStatus
    valkey_status: HealthStatus
    tableau_status: HealthStatus
    sandbox_status: HealthStatus
    llm_execution_status: HealthStatus
    sandbox_execution_status: HealthStatus
    def __init__(self, llm_status: _Optional[_Union[HealthStatus, str]] = ..., web_status: _Optional[_Union[HealthStatus, str]] = ..., ontology_status: _Optional[_Union[HealthStatus, str]] = ..., valkey_status: _Optional[_Union[HealthStatus, str]] = ..., tableau_status: _Optional[_Union[HealthStatus, str]] = ..., sandbox_status: _Optional[_Union[HealthStatus, str]] = ..., llm_execution_status: _Optional[_Union[HealthStatus, str]] = ..., sandbox_execution_status: _Optional[_Union[HealthStatus, str]] = ...) -> None: ...

class LlmUsage(_message.Message):
    __slots__ = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens", "model_name", "timestamp")
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_CREATION_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_READ_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
    model_name: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, input_tokens: _Optional[int] = ..., cache_creation_input_tokens: _Optional[int] = ..., cache_read_input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., model_name: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetLlmUsageRequest(_message.Message):
    __slots__ = ("chat_id", "include_costs")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_COSTS_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    include_costs: bool
    def __init__(self, chat_id: _Optional[str] = ..., include_costs: bool = ...) -> None: ...

class GetLlmUsageResponse(_message.Message):
    __slots__ = ("usage", "context_window_used", "estimated_cost")
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_WINDOW_USED_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_COST_FIELD_NUMBER: _ClassVar[int]
    usage: _containers.RepeatedCompositeFieldContainer[LlmUsage]
    context_window_used: float
    estimated_cost: float
    def __init__(self, usage: _Optional[_Iterable[_Union[LlmUsage, _Mapping]]] = ..., context_window_used: _Optional[float] = ..., estimated_cost: _Optional[float] = ...) -> None: ...

class ApproveContextPromptChangeRequest(_message.Message):
    __slots__ = ("cell_id", "edited_context")
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    EDITED_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    edited_context: str
    def __init__(self, cell_id: _Optional[str] = ..., edited_context: _Optional[str] = ...) -> None: ...

class ApproveContextPromptChangeResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _cells_pb2.ContextPromptChangeStatus
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_cells_pb2.ContextPromptChangeStatus, str]] = ...) -> None: ...

class RejectContextPromptChangeRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    def __init__(self, cell_id: _Optional[str] = ...) -> None: ...

class RejectContextPromptChangeResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _cells_pb2.ContextPromptChangeStatus
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_cells_pb2.ContextPromptChangeStatus, str]] = ...) -> None: ...

class SubmitContextPromptChangeRequest(_message.Message):
    __slots__ = ("cell_id", "edited_context")
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    EDITED_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    edited_context: str
    def __init__(self, cell_id: _Optional[str] = ..., edited_context: _Optional[str] = ...) -> None: ...

class SubmitContextPromptChangeResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _cells_pb2.ContextPromptChangeStatus
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_cells_pb2.ContextPromptChangeStatus, str]] = ...) -> None: ...

class ApproveOntologyChangeRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    def __init__(self, cell_id: _Optional[str] = ...) -> None: ...

class ApproveOntologyChangeResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RejectOntologyChangeRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    def __init__(self, cell_id: _Optional[str] = ...) -> None: ...

class RejectOntologyChangeResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetMembersWithChatsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMembersWithChatsResponse(_message.Message):
    __slots__ = ("members",)
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[_identity_pb2.MemberPreview]
    def __init__(self, members: _Optional[_Iterable[_Union[_identity_pb2.MemberPreview, _Mapping]]] = ...) -> None: ...

class CheckStreamlitHealthRequest(_message.Message):
    __slots__ = ("chat_id", "cell_id")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    cell_id: str
    def __init__(self, chat_id: _Optional[str] = ..., cell_id: _Optional[str] = ...) -> None: ...

class CheckStreamlitHealthResponse(_message.Message):
    __slots__ = ("status", "cell")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CELL_FIELD_NUMBER: _ClassVar[int]
    status: StreamlitHealthStatus
    cell: Cell
    def __init__(self, status: _Optional[_Union[StreamlitHealthStatus, str]] = ..., cell: _Optional[_Union[Cell, _Mapping]] = ...) -> None: ...

class UpdateFormStatusRequest(_message.Message):
    __slots__ = ("form_id", "status")
    FORM_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    form_id: str
    status: _cells_pb2.EditableFormStatus
    def __init__(self, form_id: _Optional[str] = ..., status: _Optional[_Union[_cells_pb2.EditableFormStatus, str]] = ...) -> None: ...

class UpdateFormStatusResponse(_message.Message):
    __slots__ = ("form",)
    FORM_FIELD_NUMBER: _ClassVar[int]
    form: _cells_pb2.EditableForm
    def __init__(self, form: _Optional[_Union[_cells_pb2.EditableForm, _Mapping]] = ...) -> None: ...

class UpdateFormFieldsRequest(_message.Message):
    __slots__ = ("form_id", "fields")
    FORM_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    form_id: str
    fields: _struct_pb2.Struct
    def __init__(self, form_id: _Optional[str] = ..., fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateFormFieldsResponse(_message.Message):
    __slots__ = ("form",)
    FORM_FIELD_NUMBER: _ClassVar[int]
    form: _cells_pb2.EditableForm
    def __init__(self, form: _Optional[_Union[_cells_pb2.EditableForm, _Mapping]] = ...) -> None: ...

class UpdateFormValidationErrorRequest(_message.Message):
    __slots__ = ("form_id", "validation_error")
    FORM_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_ERROR_FIELD_NUMBER: _ClassVar[int]
    form_id: str
    validation_error: str
    def __init__(self, form_id: _Optional[str] = ..., validation_error: _Optional[str] = ...) -> None: ...

class UpdateFormValidationErrorResponse(_message.Message):
    __slots__ = ("form",)
    FORM_FIELD_NUMBER: _ClassVar[int]
    form: _cells_pb2.EditableForm
    def __init__(self, form: _Optional[_Union[_cells_pb2.EditableForm, _Mapping]] = ...) -> None: ...

class GetCellRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: str
    def __init__(self, cell_id: _Optional[str] = ...) -> None: ...

class GetCellResponse(_message.Message):
    __slots__ = ("cell",)
    CELL_FIELD_NUMBER: _ClassVar[int]
    cell: Cell
    def __init__(self, cell: _Optional[_Union[Cell, _Mapping]] = ...) -> None: ...

class SetFormSubmitResultRequest(_message.Message):
    __slots__ = ("form_id", "submit_error", "submit_result", "status")
    FORM_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_ERROR_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_RESULT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    form_id: str
    submit_error: str
    submit_result: str
    status: _cells_pb2.EditableFormStatus
    def __init__(self, form_id: _Optional[str] = ..., submit_error: _Optional[str] = ..., submit_result: _Optional[str] = ..., status: _Optional[_Union[_cells_pb2.EditableFormStatus, str]] = ...) -> None: ...

class SetFormSubmitResultResponse(_message.Message):
    __slots__ = ("form",)
    FORM_FIELD_NUMBER: _ClassVar[int]
    form: _cells_pb2.EditableForm
    def __init__(self, form: _Optional[_Union[_cells_pb2.EditableForm, _Mapping]] = ...) -> None: ...

class QueryOneShotRequest(_message.Message):
    __slots__ = ("question", "paradigm", "model", "chat_id")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    question: str
    paradigm: _paradigm_pb2.Paradigm
    model: LlmModel
    chat_id: str
    def __init__(self, question: _Optional[str] = ..., paradigm: _Optional[_Union[_paradigm_pb2.Paradigm, _Mapping]] = ..., model: _Optional[_Union[LlmModel, str]] = ..., chat_id: _Optional[str] = ...) -> None: ...

class QueryOneShotResponse(_message.Message):
    __slots__ = ("chat_id", "answer", "cells")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    CELLS_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    answer: str
    cells: _containers.RepeatedCompositeFieldContainer[Cell]
    def __init__(self, chat_id: _Optional[str] = ..., answer: _Optional[str] = ..., cells: _Optional[_Iterable[_Union[Cell, _Mapping]]] = ...) -> None: ...

class BookmarkChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class UnbookmarkChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...
