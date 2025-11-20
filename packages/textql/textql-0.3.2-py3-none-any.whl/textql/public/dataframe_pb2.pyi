from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryDataFrameRequest(_message.Message):
    __slots__ = ("chat_id", "df_name", "page", "limit")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    DF_NAME_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    df_name: str
    page: int
    limit: int
    def __init__(self, chat_id: _Optional[str] = ..., df_name: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class QueryDataFrameResponse(_message.Message):
    __slots__ = ("df",)
    DF_FIELD_NUMBER: _ClassVar[int]
    df: DataFrame
    def __init__(self, df: _Optional[_Union[DataFrame, _Mapping]] = ...) -> None: ...

class DataFrameInfo(_message.Message):
    __slots__ = ("name", "external", "num_rows", "num_cols", "memory_usage")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_FIELD_NUMBER: _ClassVar[int]
    NUM_ROWS_FIELD_NUMBER: _ClassVar[int]
    NUM_COLS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    external: bool
    num_rows: int
    num_cols: int
    memory_usage: int
    def __init__(self, name: _Optional[str] = ..., external: bool = ..., num_rows: _Optional[int] = ..., num_cols: _Optional[int] = ..., memory_usage: _Optional[int] = ...) -> None: ...

class DataFrameField(_message.Message):
    __slots__ = ("column_name", "column_type", "column_index")
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_TYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_INDEX_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    column_type: str
    column_index: int
    def __init__(self, column_name: _Optional[str] = ..., column_type: _Optional[str] = ..., column_index: _Optional[int] = ...) -> None: ...

class DataFrameColumn(_message.Message):
    __slots__ = ("column_index", "doubles", "floats", "strings", "timestamps", "int32", "uint32", "int64", "uint64", "bools", "bytes")
    COLUMN_INDEX_FIELD_NUMBER: _ClassVar[int]
    DOUBLES_FIELD_NUMBER: _ClassVar[int]
    FLOATS_FIELD_NUMBER: _ClassVar[int]
    STRINGS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    INT32_FIELD_NUMBER: _ClassVar[int]
    UINT32_FIELD_NUMBER: _ClassVar[int]
    INT64_FIELD_NUMBER: _ClassVar[int]
    UINT64_FIELD_NUMBER: _ClassVar[int]
    BOOLS_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    column_index: int
    doubles: DoubleValues
    floats: FloatValues
    strings: StringValues
    timestamps: TimestampValues
    int32: Int32Values
    uint32: Uint32Values
    int64: Int64Values
    uint64: Uint64Values
    bools: BoolValues
    bytes: ByteValues
    def __init__(self, column_index: _Optional[int] = ..., doubles: _Optional[_Union[DoubleValues, _Mapping]] = ..., floats: _Optional[_Union[FloatValues, _Mapping]] = ..., strings: _Optional[_Union[StringValues, _Mapping]] = ..., timestamps: _Optional[_Union[TimestampValues, _Mapping]] = ..., int32: _Optional[_Union[Int32Values, _Mapping]] = ..., uint32: _Optional[_Union[Uint32Values, _Mapping]] = ..., int64: _Optional[_Union[Int64Values, _Mapping]] = ..., uint64: _Optional[_Union[Uint64Values, _Mapping]] = ..., bools: _Optional[_Union[BoolValues, _Mapping]] = ..., bytes: _Optional[_Union[ByteValues, _Mapping]] = ...) -> None: ...

class DataFrameRecord(_message.Message):
    __slots__ = ("columns",)
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[DataFrameColumn]
    def __init__(self, columns: _Optional[_Iterable[_Union[DataFrameColumn, _Mapping]]] = ...) -> None: ...

class DataFrame(_message.Message):
    __slots__ = ("schema", "records")
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    schema: _containers.RepeatedCompositeFieldContainer[DataFrameField]
    records: _containers.RepeatedCompositeFieldContainer[DataFrameRecord]
    def __init__(self, schema: _Optional[_Iterable[_Union[DataFrameField, _Mapping]]] = ..., records: _Optional[_Iterable[_Union[DataFrameRecord, _Mapping]]] = ...) -> None: ...

class DataFrameWithInfo(_message.Message):
    __slots__ = ("df", "info", "preview")
    DF_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    df: DataFrame
    info: DataFrameInfo
    preview: bool
    def __init__(self, df: _Optional[_Union[DataFrame, _Mapping]] = ..., info: _Optional[_Union[DataFrameInfo, _Mapping]] = ..., preview: bool = ...) -> None: ...

class Int64Values(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class Int32Values(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class Uint64Values(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class Uint32Values(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class DoubleValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class FloatValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class StringValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class BoolValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, values: _Optional[_Iterable[bool]] = ...) -> None: ...

class ByteValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, values: _Optional[_Iterable[bytes]] = ...) -> None: ...

class TimestampValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[_timestamp_pb2.Timestamp]
    def __init__(self, values: _Optional[_Iterable[_Union[_timestamp_pb2.Timestamp, _Mapping]]] = ...) -> None: ...
