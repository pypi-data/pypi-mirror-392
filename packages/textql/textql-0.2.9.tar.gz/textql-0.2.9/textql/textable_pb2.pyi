from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadToSandboxRequest(_message.Message):
    __slots__ = ("source", "csv_data", "sql_data", "tableau_data")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CSV_DATA_FIELD_NUMBER: _ClassVar[int]
    SQL_DATA_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_DATA_FIELD_NUMBER: _ClassVar[int]
    source: str
    csv_data: CSVRequest
    sql_data: SQLRequest
    tableau_data: TableauRequest
    def __init__(self, source: _Optional[str] = ..., csv_data: _Optional[_Union[CSVRequest, _Mapping]] = ..., sql_data: _Optional[_Union[SQLRequest, _Mapping]] = ..., tableau_data: _Optional[_Union[TableauRequest, _Mapping]] = ...) -> None: ...

class LoadToSandboxResponse(_message.Message):
    __slots__ = ("name", "head", "size", "loaded_in_full", "preview", "error")
    NAME_FIELD_NUMBER: _ClassVar[int]
    HEAD_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LOADED_IN_FULL_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    name: str
    head: str
    size: int
    loaded_in_full: bool
    preview: str
    error: str
    def __init__(self, name: _Optional[str] = ..., head: _Optional[str] = ..., size: _Optional[int] = ..., loaded_in_full: bool = ..., preview: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class QueryTextableRequest(_message.Message):
    __slots__ = ("source", "csv_data", "sql_data", "tableau_data", "include_stats")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CSV_DATA_FIELD_NUMBER: _ClassVar[int]
    SQL_DATA_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_DATA_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_STATS_FIELD_NUMBER: _ClassVar[int]
    source: str
    csv_data: CSVRequest
    sql_data: SQLRequest
    tableau_data: TableauRequest
    include_stats: bool
    def __init__(self, source: _Optional[str] = ..., csv_data: _Optional[_Union[CSVRequest, _Mapping]] = ..., sql_data: _Optional[_Union[SQLRequest, _Mapping]] = ..., tableau_data: _Optional[_Union[TableauRequest, _Mapping]] = ..., include_stats: bool = ...) -> None: ...

class QueryTextableResponse(_message.Message):
    __slots__ = ("column_names", "column_types", "values", "length", "stats")
    COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    COLUMN_TYPES_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    column_names: _containers.RepeatedScalarFieldContainer[str]
    column_types: _containers.RepeatedScalarFieldContainer[str]
    values: _containers.RepeatedCompositeFieldContainer[Row]
    length: int
    stats: _containers.RepeatedCompositeFieldContainer[ColumnStats]
    def __init__(self, column_names: _Optional[_Iterable[str]] = ..., column_types: _Optional[_Iterable[str]] = ..., values: _Optional[_Iterable[_Union[Row, _Mapping]]] = ..., length: _Optional[int] = ..., stats: _Optional[_Iterable[_Union[ColumnStats, _Mapping]]] = ...) -> None: ...

class Row(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, values: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...

class RetrieveStatsRequest(_message.Message):
    __slots__ = ("source", "csv_data", "sql_data", "tableau_data")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CSV_DATA_FIELD_NUMBER: _ClassVar[int]
    SQL_DATA_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_DATA_FIELD_NUMBER: _ClassVar[int]
    source: str
    csv_data: CSVRequest
    sql_data: SQLRequest
    tableau_data: TableauRequest
    def __init__(self, source: _Optional[str] = ..., csv_data: _Optional[_Union[CSVRequest, _Mapping]] = ..., sql_data: _Optional[_Union[SQLRequest, _Mapping]] = ..., tableau_data: _Optional[_Union[TableauRequest, _Mapping]] = ...) -> None: ...

class StatsResult(_message.Message):
    __slots__ = ("length", "stats")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    length: int
    stats: _containers.RepeatedCompositeFieldContainer[ColumnStats]
    def __init__(self, length: _Optional[int] = ..., stats: _Optional[_Iterable[_Union[ColumnStats, _Mapping]]] = ...) -> None: ...

class CheckTextableRequest(_message.Message):
    __slots__ = ("source", "csv_data", "sql_data", "tableau_data", "include_stats")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CSV_DATA_FIELD_NUMBER: _ClassVar[int]
    SQL_DATA_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_DATA_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_STATS_FIELD_NUMBER: _ClassVar[int]
    source: str
    csv_data: CSVRequest
    sql_data: SQLRequest
    tableau_data: TableauRequest
    include_stats: bool
    def __init__(self, source: _Optional[str] = ..., csv_data: _Optional[_Union[CSVRequest, _Mapping]] = ..., sql_data: _Optional[_Union[SQLRequest, _Mapping]] = ..., tableau_data: _Optional[_Union[TableauRequest, _Mapping]] = ..., include_stats: bool = ...) -> None: ...

class CheckTextableResponse(_message.Message):
    __slots__ = ("column_names", "column_types", "length", "stats")
    COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    COLUMN_TYPES_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    column_names: _containers.RepeatedScalarFieldContainer[str]
    column_types: _containers.RepeatedScalarFieldContainer[str]
    length: int
    stats: _containers.RepeatedCompositeFieldContainer[ColumnStats]
    def __init__(self, column_names: _Optional[_Iterable[str]] = ..., column_types: _Optional[_Iterable[str]] = ..., length: _Optional[int] = ..., stats: _Optional[_Iterable[_Union[ColumnStats, _Mapping]]] = ...) -> None: ...

class CSVRequest(_message.Message):
    __slots__ = ("url", "limit", "page", "histogram_bucket_size", "timeout", "data_frame_name")
    URL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_BUCKET_SIZE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DATA_FRAME_NAME_FIELD_NUMBER: _ClassVar[int]
    url: str
    limit: int
    page: int
    histogram_bucket_size: int
    timeout: str
    data_frame_name: str
    def __init__(self, url: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ..., histogram_bucket_size: _Optional[int] = ..., timeout: _Optional[str] = ..., data_frame_name: _Optional[str] = ...) -> None: ...

class SQLRequest(_message.Message):
    __slots__ = ("query", "deployment_type", "deployment", "force_exact_query", "limit", "page", "histogram_bucket_size", "timeout", "data_frame_name")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    FORCE_EXACT_QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_BUCKET_SIZE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DATA_FRAME_NAME_FIELD_NUMBER: _ClassVar[int]
    query: str
    deployment_type: str
    deployment: Deployment
    force_exact_query: bool
    limit: int
    page: int
    histogram_bucket_size: int
    timeout: str
    data_frame_name: str
    def __init__(self, query: _Optional[str] = ..., deployment_type: _Optional[str] = ..., deployment: _Optional[_Union[Deployment, _Mapping]] = ..., force_exact_query: bool = ..., limit: _Optional[int] = ..., page: _Optional[int] = ..., histogram_bucket_size: _Optional[int] = ..., timeout: _Optional[str] = ..., data_frame_name: _Optional[str] = ...) -> None: ...

class TableauRequest(_message.Message):
    __slots__ = ("deployment", "view_id", "limit", "page", "histogram_bucket_size", "timeout", "data_frame_name")
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_BUCKET_SIZE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DATA_FRAME_NAME_FIELD_NUMBER: _ClassVar[int]
    deployment: Deployment
    view_id: str
    limit: int
    page: int
    histogram_bucket_size: int
    timeout: str
    data_frame_name: str
    def __init__(self, deployment: _Optional[_Union[Deployment, _Mapping]] = ..., view_id: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ..., histogram_bucket_size: _Optional[int] = ..., timeout: _Optional[str] = ..., data_frame_name: _Optional[str] = ...) -> None: ...

class Deployment(_message.Message):
    __slots__ = ("dialect",)
    DIALECT_FIELD_NUMBER: _ClassVar[int]
    dialect: str
    def __init__(self, dialect: _Optional[str] = ...) -> None: ...

class ColumnStats(_message.Message):
    __slots__ = ("name", "type", "min", "max", "mean", "median", "histogram")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    MEAN_FIELD_NUMBER: _ClassVar[int]
    MEDIAN_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    min: float
    max: float
    mean: float
    median: float
    histogram: _containers.RepeatedCompositeFieldContainer[HistogramBucket]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., min: _Optional[float] = ..., max: _Optional[float] = ..., mean: _Optional[float] = ..., median: _Optional[float] = ..., histogram: _Optional[_Iterable[_Union[HistogramBucket, _Mapping]]] = ...) -> None: ...

class HistogramBucket(_message.Message):
    __slots__ = ("low", "high", "count")
    LOW_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    low: float
    high: float
    count: int
    def __init__(self, low: _Optional[float] = ..., high: _Optional[float] = ..., count: _Optional[int] = ...) -> None: ...
