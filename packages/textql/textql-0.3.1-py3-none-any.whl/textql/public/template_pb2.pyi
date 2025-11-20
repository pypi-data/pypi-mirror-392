from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from public import playbook_pb2 as _playbook_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlaybookTemplateHeader(_message.Message):
    __slots__ = ("id", "headers", "template_name", "org_id", "created_at", "updated_at", "can_edit", "created_by", "created_by_email")
    ID_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CAN_EDIT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_EMAIL_FIELD_NUMBER: _ClassVar[int]
    id: str
    headers: _struct_pb2.Struct
    template_name: str
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    can_edit: bool
    created_by: str
    created_by_email: str
    def __init__(self, id: _Optional[str] = ..., headers: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., template_name: _Optional[str] = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., can_edit: bool = ..., created_by: _Optional[str] = ..., created_by_email: _Optional[str] = ...) -> None: ...

class CreatePlaybookTemplateHeaderRequest(_message.Message):
    __slots__ = ("headers", "template_name")
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    headers: _struct_pb2.Struct
    template_name: str
    def __init__(self, headers: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., template_name: _Optional[str] = ...) -> None: ...

class CreatePlaybookTemplateHeaderResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: PlaybookTemplateHeader
    def __init__(self, header: _Optional[_Union[PlaybookTemplateHeader, _Mapping]] = ...) -> None: ...

class GetPlaybookTemplateHeaderRequest(_message.Message):
    __slots__ = ("header_id",)
    HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    header_id: str
    def __init__(self, header_id: _Optional[str] = ...) -> None: ...

class GetPlaybookTemplateHeaderResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: PlaybookTemplateHeader
    def __init__(self, header: _Optional[_Union[PlaybookTemplateHeader, _Mapping]] = ...) -> None: ...

class UpdatePlaybookTemplateHeaderRequest(_message.Message):
    __slots__ = ("header_id", "headers", "template_name")
    HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    header_id: str
    headers: _struct_pb2.Struct
    template_name: str
    def __init__(self, header_id: _Optional[str] = ..., headers: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., template_name: _Optional[str] = ...) -> None: ...

class UpdatePlaybookTemplateHeaderResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: PlaybookTemplateHeader
    def __init__(self, header: _Optional[_Union[PlaybookTemplateHeader, _Mapping]] = ...) -> None: ...

class DeletePlaybookTemplateHeaderRequest(_message.Message):
    __slots__ = ("header_id",)
    HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    header_id: str
    def __init__(self, header_id: _Optional[str] = ...) -> None: ...

class ListPlaybookTemplateHeadersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPlaybookTemplateHeadersResponse(_message.Message):
    __slots__ = ("headers",)
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[PlaybookTemplateHeader]
    def __init__(self, headers: _Optional[_Iterable[_Union[PlaybookTemplateHeader, _Mapping]]] = ...) -> None: ...

class PlaybookTemplateData(_message.Message):
    __slots__ = ("id", "playbook_header", "entries", "org_id", "created_at", "updated_at", "execution_status", "last_execution_started_at", "last_execution_completed_at", "last_execution_error")
    ID_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_HEADER_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    LAST_EXECUTION_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_EXECUTION_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_EXECUTION_ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    playbook_header: str
    entries: _struct_pb2.Struct
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    execution_status: _playbook_pb2.TemplateDataExecutionStatus
    last_execution_started_at: _timestamp_pb2.Timestamp
    last_execution_completed_at: _timestamp_pb2.Timestamp
    last_execution_error: str
    def __init__(self, id: _Optional[str] = ..., playbook_header: _Optional[str] = ..., entries: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., execution_status: _Optional[_Union[_playbook_pb2.TemplateDataExecutionStatus, str]] = ..., last_execution_started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_execution_completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_execution_error: _Optional[str] = ...) -> None: ...

class CreatePlaybookTemplateDataRequest(_message.Message):
    __slots__ = ("playbook_header", "entries")
    PLAYBOOK_HEADER_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    playbook_header: str
    entries: _struct_pb2.Struct
    def __init__(self, playbook_header: _Optional[str] = ..., entries: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreatePlaybookTemplateDataResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: PlaybookTemplateData
    def __init__(self, data: _Optional[_Union[PlaybookTemplateData, _Mapping]] = ...) -> None: ...

class GetPlaybookTemplateDataRequest(_message.Message):
    __slots__ = ("data_id",)
    DATA_ID_FIELD_NUMBER: _ClassVar[int]
    data_id: str
    def __init__(self, data_id: _Optional[str] = ...) -> None: ...

class GetPlaybookTemplateDataResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: PlaybookTemplateData
    def __init__(self, data: _Optional[_Union[PlaybookTemplateData, _Mapping]] = ...) -> None: ...

class GetPlaybookTemplateDataByHeaderRequest(_message.Message):
    __slots__ = ("playbook_header", "limit", "offset")
    PLAYBOOK_HEADER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    playbook_header: str
    limit: int
    offset: int
    def __init__(self, playbook_header: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetPlaybookTemplateDataByHeaderResponse(_message.Message):
    __slots__ = ("data_rows", "total_count", "offset", "limit", "has_more")
    DATA_ROWS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    data_rows: _containers.RepeatedCompositeFieldContainer[PlaybookTemplateData]
    total_count: int
    offset: int
    limit: int
    has_more: bool
    def __init__(self, data_rows: _Optional[_Iterable[_Union[PlaybookTemplateData, _Mapping]]] = ..., total_count: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., has_more: bool = ...) -> None: ...

class GetPlaybookTemplateDataWithBatchStatusRequest(_message.Message):
    __slots__ = ("playbook_header", "playbook_id", "batch_run_id", "limit", "offset")
    PLAYBOOK_HEADER_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    playbook_header: str
    playbook_id: str
    batch_run_id: str
    limit: int
    offset: int
    def __init__(self, playbook_header: _Optional[str] = ..., playbook_id: _Optional[str] = ..., batch_run_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetPlaybookTemplateDataWithBatchStatusResponse(_message.Message):
    __slots__ = ("data_rows", "total_count", "offset", "limit", "has_more")
    DATA_ROWS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    data_rows: _containers.RepeatedCompositeFieldContainer[PlaybookTemplateData]
    total_count: int
    offset: int
    limit: int
    has_more: bool
    def __init__(self, data_rows: _Optional[_Iterable[_Union[PlaybookTemplateData, _Mapping]]] = ..., total_count: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., has_more: bool = ...) -> None: ...

class UpdatePlaybookTemplateDataRequest(_message.Message):
    __slots__ = ("data_id", "entries")
    DATA_ID_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    data_id: str
    entries: _struct_pb2.Struct
    def __init__(self, data_id: _Optional[str] = ..., entries: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdatePlaybookTemplateDataResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: PlaybookTemplateData
    def __init__(self, data: _Optional[_Union[PlaybookTemplateData, _Mapping]] = ...) -> None: ...

class DeletePlaybookTemplateDataRequest(_message.Message):
    __slots__ = ("data_id",)
    DATA_ID_FIELD_NUMBER: _ClassVar[int]
    data_id: str
    def __init__(self, data_id: _Optional[str] = ...) -> None: ...

class DeletePlaybookTemplateDataByHeaderRequest(_message.Message):
    __slots__ = ("playbook_header",)
    PLAYBOOK_HEADER_FIELD_NUMBER: _ClassVar[int]
    playbook_header: str
    def __init__(self, playbook_header: _Optional[str] = ...) -> None: ...

class CreateTemplateFromCSVRequest(_message.Message):
    __slots__ = ("file_content", "template_name")
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    file_content: bytes
    template_name: str
    def __init__(self, file_content: _Optional[bytes] = ..., template_name: _Optional[str] = ...) -> None: ...

class CreateTemplateFromCSVResponse(_message.Message):
    __slots__ = ("header_id",)
    HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    header_id: str
    def __init__(self, header_id: _Optional[str] = ...) -> None: ...

class CreateTemplateFromXLSXRequest(_message.Message):
    __slots__ = ("file_content", "template_name")
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    file_content: bytes
    template_name: str
    def __init__(self, file_content: _Optional[bytes] = ..., template_name: _Optional[str] = ...) -> None: ...

class CreateTemplateFromXLSXResponse(_message.Message):
    __slots__ = ("header_id",)
    HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    header_id: str
    def __init__(self, header_id: _Optional[str] = ...) -> None: ...
