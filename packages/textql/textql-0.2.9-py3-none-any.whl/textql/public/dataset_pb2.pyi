from google.protobuf import timestamp_pb2 as _timestamp_pb2
from public import dataframe_pb2 as _dataframe_pb2
from public import identity_pb2 as _identity_pb2
from public import tableau_pb2 as _tableau_pb2
from public import powerbi_pb2 as _powerbi_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatasetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNKNOWN: _ClassVar[DatasetType]
    TYPE_TABULAR: _ClassVar[DatasetType]
    TYPE_DATAFRAME: _ClassVar[DatasetType]
    TYPE_DOCUMENT: _ClassVar[DatasetType]
    TYPE_TABLEAU: _ClassVar[DatasetType]
    TYPE_IMAGE: _ClassVar[DatasetType]
    TYPE_TEXT: _ClassVar[DatasetType]
    TYPE_POWERBI: _ClassVar[DatasetType]

class DatasetPermission(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PERMISSION_UNKNOWN: _ClassVar[DatasetPermission]
    PERMISSION_READ: _ClassVar[DatasetPermission]
    PERMISSION_EDIT: _ClassVar[DatasetPermission]
    PERMISSION_ADMIN: _ClassVar[DatasetPermission]

class TabularFileCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CATEGORY_UNKNOWN: _ClassVar[TabularFileCategory]
    CATEGORY_CSV: _ClassVar[TabularFileCategory]
    CATEGORY_TSV: _ClassVar[TabularFileCategory]
    CATEGORY_XLSX: _ClassVar[TabularFileCategory]
    CATEGORY_XLS: _ClassVar[TabularFileCategory]
    CATEGORY_PARQUET: _ClassVar[TabularFileCategory]
    CATEGORY_ODS: _ClassVar[TabularFileCategory]

class DatasetsSort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_UNKNOWN: _ClassVar[DatasetsSort]
    SORT_LATEST: _ClassVar[DatasetsSort]
    SORT_OLDEST: _ClassVar[DatasetsSort]
    SORT_RELEVANT: _ClassVar[DatasetsSort]

class ExportFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMAT_UNKNOWN: _ClassVar[ExportFormat]
    FORMAT_CSV: _ClassVar[ExportFormat]
    FORMAT_EXCEL: _ClassVar[ExportFormat]
    FORMAT_PARQUET: _ClassVar[ExportFormat]
TYPE_UNKNOWN: DatasetType
TYPE_TABULAR: DatasetType
TYPE_DATAFRAME: DatasetType
TYPE_DOCUMENT: DatasetType
TYPE_TABLEAU: DatasetType
TYPE_IMAGE: DatasetType
TYPE_TEXT: DatasetType
TYPE_POWERBI: DatasetType
PERMISSION_UNKNOWN: DatasetPermission
PERMISSION_READ: DatasetPermission
PERMISSION_EDIT: DatasetPermission
PERMISSION_ADMIN: DatasetPermission
CATEGORY_UNKNOWN: TabularFileCategory
CATEGORY_CSV: TabularFileCategory
CATEGORY_TSV: TabularFileCategory
CATEGORY_XLSX: TabularFileCategory
CATEGORY_XLS: TabularFileCategory
CATEGORY_PARQUET: TabularFileCategory
CATEGORY_ODS: TabularFileCategory
SORT_UNKNOWN: DatasetsSort
SORT_LATEST: DatasetsSort
SORT_OLDEST: DatasetsSort
SORT_RELEVANT: DatasetsSort
FORMAT_UNKNOWN: ExportFormat
FORMAT_CSV: ExportFormat
FORMAT_EXCEL: ExportFormat
FORMAT_PARQUET: ExportFormat

class DatasetFolder(_message.Message):
    __slots__ = ("path", "owner", "created_at")
    PATH_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    path: str
    owner: _identity_pb2.MemberPreview
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, path: _Optional[str] = ..., owner: _Optional[_Union[_identity_pb2.MemberPreview, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Dataset(_message.Message):
    __slots__ = ("id", "type", "name", "version", "path", "owner", "user_permissions", "created_at", "updated_at", "expires_at", "ephemeral", "tabular_file", "document", "dataframe", "tableau_data", "powerbi_data")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    USER_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    EPHEMERAL_FIELD_NUMBER: _ClassVar[int]
    TABULAR_FILE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_DATA_FIELD_NUMBER: _ClassVar[int]
    POWERBI_DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: DatasetType
    name: str
    version: int
    path: str
    owner: _identity_pb2.MemberPreview
    user_permissions: DatasetPermission
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    ephemeral: bool
    tabular_file: TabularFile
    document: Document
    dataframe: SandboxDataFrame
    tableau_data: TableauData
    powerbi_data: PowerBIData
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[DatasetType, str]] = ..., name: _Optional[str] = ..., version: _Optional[int] = ..., path: _Optional[str] = ..., owner: _Optional[_Union[_identity_pb2.MemberPreview, _Mapping]] = ..., user_permissions: _Optional[_Union[DatasetPermission, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ephemeral: bool = ..., tabular_file: _Optional[_Union[TabularFile, _Mapping]] = ..., document: _Optional[_Union[Document, _Mapping]] = ..., dataframe: _Optional[_Union[SandboxDataFrame, _Mapping]] = ..., tableau_data: _Optional[_Union[TableauData, _Mapping]] = ..., powerbi_data: _Optional[_Union[PowerBIData, _Mapping]] = ...) -> None: ...

class TabularFile(_message.Message):
    __slots__ = ("category", "row_count", "column_count", "sheet_count")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ROW_COUNT_FIELD_NUMBER: _ClassVar[int]
    COLUMN_COUNT_FIELD_NUMBER: _ClassVar[int]
    SHEET_COUNT_FIELD_NUMBER: _ClassVar[int]
    category: TabularFileCategory
    row_count: int
    column_count: int
    sheet_count: int
    def __init__(self, category: _Optional[_Union[TabularFileCategory, str]] = ..., row_count: _Optional[int] = ..., column_count: _Optional[int] = ..., sheet_count: _Optional[int] = ...) -> None: ...

class Document(_message.Message):
    __slots__ = ("preview_url", "page_count")
    PREVIEW_URL_FIELD_NUMBER: _ClassVar[int]
    PAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    preview_url: str
    page_count: int
    def __init__(self, preview_url: _Optional[str] = ..., page_count: _Optional[int] = ...) -> None: ...

class SandboxDataFrame(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _dataframe_pb2.DataFrameInfo
    def __init__(self, info: _Optional[_Union[_dataframe_pb2.DataFrameInfo, _Mapping]] = ...) -> None: ...

class TableauData(_message.Message):
    __slots__ = ("connector_id", "project_id", "project_name", "views", "datasources")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    VIEWS_FIELD_NUMBER: _ClassVar[int]
    DATASOURCES_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    project_id: str
    project_name: str
    views: _containers.RepeatedCompositeFieldContainer[_tableau_pb2.TableauView]
    datasources: _containers.RepeatedCompositeFieldContainer[_tableau_pb2.TableauDatasource]
    def __init__(self, connector_id: _Optional[int] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., views: _Optional[_Iterable[_Union[_tableau_pb2.TableauView, _Mapping]]] = ..., datasources: _Optional[_Iterable[_Union[_tableau_pb2.TableauDatasource, _Mapping]]] = ...) -> None: ...

class PowerBIData(_message.Message):
    __slots__ = ("connector_id", "report_ids", "dataset_ids")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_IDS_FIELD_NUMBER: _ClassVar[int]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    report_ids: _containers.RepeatedScalarFieldContainer[str]
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, connector_id: _Optional[int] = ..., report_ids: _Optional[_Iterable[str]] = ..., dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateFolderRequest(_message.Message):
    __slots__ = ("parent_path", "name")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    parent_path: _containers.RepeatedScalarFieldContainer[str]
    name: str
    def __init__(self, parent_path: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ...) -> None: ...

class CreateFolderResponse(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, path: _Optional[_Iterable[str]] = ...) -> None: ...

class GetFoldersRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class GetFoldersResponse(_message.Message):
    __slots__ = ("folders",)
    FOLDERS_FIELD_NUMBER: _ClassVar[int]
    folders: _containers.RepeatedCompositeFieldContainer[DatasetFolder]
    def __init__(self, folders: _Optional[_Iterable[_Union[DatasetFolder, _Mapping]]] = ...) -> None: ...

class CreateUploadPresignUrlRequest(_message.Message):
    __slots__ = ("type", "file_name", "folder_path", "ephemeral", "expires_in_days")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_PATH_FIELD_NUMBER: _ClassVar[int]
    EPHEMERAL_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    type: DatasetType
    file_name: str
    folder_path: _containers.RepeatedScalarFieldContainer[str]
    ephemeral: bool
    expires_in_days: int
    def __init__(self, type: _Optional[_Union[DatasetType, str]] = ..., file_name: _Optional[str] = ..., folder_path: _Optional[_Iterable[str]] = ..., ephemeral: bool = ..., expires_in_days: _Optional[int] = ...) -> None: ...

class CreateUploadPresignUrlResponse(_message.Message):
    __slots__ = ("dataset_id", "dataset_version", "presign_url")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRESIGN_URL_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dataset_version: int
    presign_url: str
    def __init__(self, dataset_id: _Optional[str] = ..., dataset_version: _Optional[int] = ..., presign_url: _Optional[str] = ...) -> None: ...

class ProcessUploadPresignUrlRequest(_message.Message):
    __slots__ = ("dataset_id", "dataset_version")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_VERSION_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dataset_version: int
    def __init__(self, dataset_id: _Optional[str] = ..., dataset_version: _Optional[int] = ...) -> None: ...

class ProcessUploadPresignUrlResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class GetDatasetRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class GetDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class GetDatasetsRequest(_message.Message):
    __slots__ = ("types", "owner_only", "include_subfolders", "path", "search_param", "sort", "limit", "cursor")
    TYPES_FIELD_NUMBER: _ClassVar[int]
    OWNER_ONLY_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SUBFOLDERS_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PARAM_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    types: _containers.RepeatedScalarFieldContainer[DatasetType]
    owner_only: bool
    include_subfolders: bool
    path: str
    search_param: str
    sort: DatasetsSort
    limit: int
    cursor: str
    def __init__(self, types: _Optional[_Iterable[_Union[DatasetType, str]]] = ..., owner_only: bool = ..., include_subfolders: bool = ..., path: _Optional[str] = ..., search_param: _Optional[str] = ..., sort: _Optional[_Union[DatasetsSort, str]] = ..., limit: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class GetDatasetsResponse(_message.Message):
    __slots__ = ("datasets",)
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[Dataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[Dataset, _Mapping]]] = ...) -> None: ...

class GetDatasetsByIdsRequest(_message.Message):
    __slots__ = ("dataset_ids",)
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetDatasetsByIdsResponse(_message.Message):
    __slots__ = ("datasets",)
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[Dataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[Dataset, _Mapping]]] = ...) -> None: ...

class ExportDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "preferred_format", "version_id")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_FORMAT_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    preferred_format: ExportFormat
    version_id: int
    def __init__(self, dataset_id: _Optional[str] = ..., preferred_format: _Optional[_Union[ExportFormat, str]] = ..., version_id: _Optional[int] = ...) -> None: ...

class ExportDatasetResponse(_message.Message):
    __slots__ = ("presigned_url",)
    PRESIGNED_URL_FIELD_NUMBER: _ClassVar[int]
    presigned_url: str
    def __init__(self, presigned_url: _Optional[str] = ...) -> None: ...

class GetDatasetValuesRequest(_message.Message):
    __slots__ = ("dataset_id", "version_id", "limit", "page", "sheet")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    SHEET_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    version_id: int
    limit: int
    page: int
    sheet: int
    def __init__(self, dataset_id: _Optional[str] = ..., version_id: _Optional[int] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ..., sheet: _Optional[int] = ...) -> None: ...

class GetDatasetValuesResponse(_message.Message):
    __slots__ = ("df", "num_cols", "num_rows")
    DF_FIELD_NUMBER: _ClassVar[int]
    NUM_COLS_FIELD_NUMBER: _ClassVar[int]
    NUM_ROWS_FIELD_NUMBER: _ClassVar[int]
    df: _dataframe_pb2.DataFrame
    num_cols: int
    num_rows: int
    def __init__(self, df: _Optional[_Union[_dataframe_pb2.DataFrame, _Mapping]] = ..., num_cols: _Optional[int] = ..., num_rows: _Optional[int] = ...) -> None: ...

class GetDatasetStatsRequest(_message.Message):
    __slots__ = ("dataset_id", "version_id")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    version_id: int
    def __init__(self, dataset_id: _Optional[str] = ..., version_id: _Optional[int] = ...) -> None: ...

class GetDatasetStatsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateTableauDatasetRequest(_message.Message):
    __slots__ = ("connector_id", "name", "folder_path", "project_id", "project_name", "views", "datasources")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_PATH_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    VIEWS_FIELD_NUMBER: _ClassVar[int]
    DATASOURCES_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    name: str
    folder_path: _containers.RepeatedScalarFieldContainer[str]
    project_id: str
    project_name: str
    views: _containers.RepeatedCompositeFieldContainer[_tableau_pb2.TableauView]
    datasources: _containers.RepeatedCompositeFieldContainer[_tableau_pb2.TableauDatasource]
    def __init__(self, connector_id: _Optional[int] = ..., name: _Optional[str] = ..., folder_path: _Optional[_Iterable[str]] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., views: _Optional[_Iterable[_Union[_tableau_pb2.TableauView, _Mapping]]] = ..., datasources: _Optional[_Iterable[_Union[_tableau_pb2.TableauDatasource, _Mapping]]] = ...) -> None: ...

class CreateTableauDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class CreatePowerBIDatasetRequest(_message.Message):
    __slots__ = ("connector_id", "name", "folder_path", "workspace_id", "workspace_name", "reports", "datasets")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_PATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    name: str
    folder_path: _containers.RepeatedScalarFieldContainer[str]
    workspace_id: str
    workspace_name: str
    reports: _containers.RepeatedCompositeFieldContainer[_powerbi_pb2.PowerBIReport]
    datasets: _containers.RepeatedCompositeFieldContainer[_powerbi_pb2.PowerBIDataset]
    def __init__(self, connector_id: _Optional[int] = ..., name: _Optional[str] = ..., folder_path: _Optional[_Iterable[str]] = ..., workspace_id: _Optional[str] = ..., workspace_name: _Optional[str] = ..., reports: _Optional[_Iterable[_Union[_powerbi_pb2.PowerBIReport, _Mapping]]] = ..., datasets: _Optional[_Iterable[_Union[_powerbi_pb2.PowerBIDataset, _Mapping]]] = ...) -> None: ...

class CreatePowerBIDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class UpdateDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "name")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    name: str
    def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class DeleteDatasetRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class DeleteDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
