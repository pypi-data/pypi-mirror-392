from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class ExecResponse(_message.Message):
    __slots__ = ("output", "error", "dataFrameIds")
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATAFRAMEIDS_FIELD_NUMBER: _ClassVar[int]
    output: _containers.RepeatedScalarFieldContainer[str]
    error: str
    dataFrameIds: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, output: _Optional[_Iterable[str]] = ..., error: _Optional[str] = ..., dataFrameIds: _Optional[_Iterable[int]] = ...) -> None: ...

class SandboxStatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class QuerySQLRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class QuerySQLResponse(_message.Message):
    __slots__ = ("result", "error")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    result: str
    error: str
    def __init__(self, result: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class DataRow(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class LoadDataRequest(_message.Message):
    __slots__ = ("columnNames", "columnTypes", "rows")
    COLUMNNAMES_FIELD_NUMBER: _ClassVar[int]
    COLUMNTYPES_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    columnNames: _containers.RepeatedScalarFieldContainer[str]
    columnTypes: _containers.RepeatedScalarFieldContainer[str]
    rows: _containers.RepeatedCompositeFieldContainer[DataRow]
    def __init__(self, columnNames: _Optional[_Iterable[str]] = ..., columnTypes: _Optional[_Iterable[str]] = ..., rows: _Optional[_Iterable[_Union[DataRow, _Mapping]]] = ...) -> None: ...

class LoadFileRequest(_message.Message):
    __slots__ = ("fileLocations", "fileTypes", "hasHeader", "dataFrameNames")
    FILELOCATIONS_FIELD_NUMBER: _ClassVar[int]
    FILETYPES_FIELD_NUMBER: _ClassVar[int]
    HASHEADER_FIELD_NUMBER: _ClassVar[int]
    DATAFRAMENAMES_FIELD_NUMBER: _ClassVar[int]
    fileLocations: _containers.RepeatedScalarFieldContainer[str]
    fileTypes: _containers.RepeatedScalarFieldContainer[str]
    hasHeader: _containers.RepeatedScalarFieldContainer[bool]
    dataFrameNames: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fileLocations: _Optional[_Iterable[str]] = ..., fileTypes: _Optional[_Iterable[str]] = ..., hasHeader: _Optional[_Iterable[bool]] = ..., dataFrameNames: _Optional[_Iterable[str]] = ...) -> None: ...

class LoadDataResponse(_message.Message):
    __slots__ = ("dataframe", "name", "preview", "size", "error", "head")
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    HEAD_FIELD_NUMBER: _ClassVar[int]
    dataframe: str
    name: str
    preview: str
    size: int
    error: str
    head: str
    def __init__(self, dataframe: _Optional[str] = ..., name: _Optional[str] = ..., preview: _Optional[str] = ..., size: _Optional[int] = ..., error: _Optional[str] = ..., head: _Optional[str] = ...) -> None: ...
