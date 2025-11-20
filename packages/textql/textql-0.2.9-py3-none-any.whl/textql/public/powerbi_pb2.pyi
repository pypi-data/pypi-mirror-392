from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestPowerBIConnectionRequest(_message.Message):
    __slots__ = ("connector_id", "tenant_id", "client_id", "client_secret")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    tenant_id: str
    client_id: str
    client_secret: str
    def __init__(self, connector_id: _Optional[int] = ..., tenant_id: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ...) -> None: ...

class TestPowerBIConnectionResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class PowerBIWorkspace(_message.Message):
    __slots__ = ("id", "name", "is_read_only", "is_on_premium")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_READ_ONLY_FIELD_NUMBER: _ClassVar[int]
    IS_ON_PREMIUM_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    is_read_only: bool
    is_on_premium: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., is_read_only: bool = ..., is_on_premium: bool = ...) -> None: ...

class ListPowerBIWorkspacesRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class ListPowerBIWorkspacesResponse(_message.Message):
    __slots__ = ("workspaces",)
    WORKSPACES_FIELD_NUMBER: _ClassVar[int]
    workspaces: _containers.RepeatedCompositeFieldContainer[PowerBIWorkspace]
    def __init__(self, workspaces: _Optional[_Iterable[_Union[PowerBIWorkspace, _Mapping]]] = ...) -> None: ...

class PowerBIDataset(_message.Message):
    __slots__ = ("id", "name", "add_rows_api_enabled", "configured_by", "is_refreshable", "is_effective_identity_required", "is_effective_identity_roles_required", "is_on_prem_gateway_required", "created_date", "table_names")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADD_ROWS_API_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONFIGURED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_REFRESHABLE_FIELD_NUMBER: _ClassVar[int]
    IS_EFFECTIVE_IDENTITY_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    IS_EFFECTIVE_IDENTITY_ROLES_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    IS_ON_PREM_GATEWAY_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    CREATED_DATE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAMES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    add_rows_api_enabled: bool
    configured_by: str
    is_refreshable: bool
    is_effective_identity_required: bool
    is_effective_identity_roles_required: bool
    is_on_prem_gateway_required: bool
    created_date: _timestamp_pb2.Timestamp
    table_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., add_rows_api_enabled: bool = ..., configured_by: _Optional[str] = ..., is_refreshable: bool = ..., is_effective_identity_required: bool = ..., is_effective_identity_roles_required: bool = ..., is_on_prem_gateway_required: bool = ..., created_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., table_names: _Optional[_Iterable[str]] = ...) -> None: ...

class ListPowerBIDatasetsRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ...) -> None: ...

class ListPowerBIDatasetsResponse(_message.Message):
    __slots__ = ("datasets",)
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[PowerBIDataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[PowerBIDataset, _Mapping]]] = ...) -> None: ...

class PowerBIReport(_message.Message):
    __slots__ = ("id", "name", "web_url", "embed_url", "dataset_id", "created_by", "created_date")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    EMBED_URL_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_DATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    web_url: str
    embed_url: str
    dataset_id: str
    created_by: str
    created_date: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., web_url: _Optional[str] = ..., embed_url: _Optional[str] = ..., dataset_id: _Optional[str] = ..., created_by: _Optional[str] = ..., created_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListPowerBIReportsRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ...) -> None: ...

class ListPowerBIReportsResponse(_message.Message):
    __slots__ = ("reports",)
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[PowerBIReport]
    def __init__(self, reports: _Optional[_Iterable[_Union[PowerBIReport, _Mapping]]] = ...) -> None: ...

class ExportPowerBIReportImageRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id", "report_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    report_id: str
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ..., report_id: _Optional[str] = ...) -> None: ...

class ExportPowerBIReportImageResponse(_message.Message):
    __slots__ = ("image_data", "image_url")
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    image_data: bytes
    image_url: str
    def __init__(self, image_data: _Optional[bytes] = ..., image_url: _Optional[str] = ...) -> None: ...

class GeneratePowerBIEmbedTokenRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id", "report_id", "dataset_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    report_id: str
    dataset_id: str
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ..., report_id: _Optional[str] = ..., dataset_id: _Optional[str] = ...) -> None: ...

class GeneratePowerBIEmbedTokenResponse(_message.Message):
    __slots__ = ("token", "token_id", "expiration")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    token: str
    token_id: str
    expiration: _timestamp_pb2.Timestamp
    def __init__(self, token: _Optional[str] = ..., token_id: _Optional[str] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SyncPowerBIItemsRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id", "workspace_name", "reports", "datasets")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    workspace_name: str
    reports: _containers.RepeatedCompositeFieldContainer[PowerBIReport]
    datasets: _containers.RepeatedCompositeFieldContainer[PowerBIDataset]
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ..., workspace_name: _Optional[str] = ..., reports: _Optional[_Iterable[_Union[PowerBIReport, _Mapping]]] = ..., datasets: _Optional[_Iterable[_Union[PowerBIDataset, _Mapping]]] = ...) -> None: ...

class SyncPowerBIItemsResponse(_message.Message):
    __slots__ = ("success", "error", "synced_report_ids", "synced_dataset_ids")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SYNCED_REPORT_IDS_FIELD_NUMBER: _ClassVar[int]
    SYNCED_DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    synced_report_ids: _containers.RepeatedScalarFieldContainer[str]
    synced_dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., synced_report_ids: _Optional[_Iterable[str]] = ..., synced_dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UnsyncPowerBIItemsRequest(_message.Message):
    __slots__ = ("connector_id", "report_ids", "dataset_ids")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_IDS_FIELD_NUMBER: _ClassVar[int]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    report_ids: _containers.RepeatedScalarFieldContainer[str]
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, connector_id: _Optional[int] = ..., report_ids: _Optional[_Iterable[str]] = ..., dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UnsyncPowerBIItemsResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetSyncedPowerBIItemsRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetSyncedPowerBIItemsResponse(_message.Message):
    __slots__ = ("reports", "datasets")
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[SyncedPowerBIReport]
    datasets: _containers.RepeatedCompositeFieldContainer[SyncedPowerBIDataset]
    def __init__(self, reports: _Optional[_Iterable[_Union[SyncedPowerBIReport, _Mapping]]] = ..., datasets: _Optional[_Iterable[_Union[SyncedPowerBIDataset, _Mapping]]] = ...) -> None: ...

class SyncedPowerBIReport(_message.Message):
    __slots__ = ("report", "workspace_id", "workspace_name", "synced_at")
    REPORT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SYNCED_AT_FIELD_NUMBER: _ClassVar[int]
    report: PowerBIReport
    workspace_id: str
    workspace_name: str
    synced_at: _timestamp_pb2.Timestamp
    def __init__(self, report: _Optional[_Union[PowerBIReport, _Mapping]] = ..., workspace_id: _Optional[str] = ..., workspace_name: _Optional[str] = ..., synced_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SyncedPowerBIDataset(_message.Message):
    __slots__ = ("dataset", "workspace_id", "workspace_name", "synced_at")
    DATASET_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SYNCED_AT_FIELD_NUMBER: _ClassVar[int]
    dataset: PowerBIDataset
    workspace_id: str
    workspace_name: str
    synced_at: _timestamp_pb2.Timestamp
    def __init__(self, dataset: _Optional[_Union[PowerBIDataset, _Mapping]] = ..., workspace_id: _Optional[str] = ..., workspace_name: _Optional[str] = ..., synced_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetPowerBIDatasetPreviewRequest(_message.Message):
    __slots__ = ("connector_id", "workspace_id", "dataset_id", "dataset_name", "limit")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workspace_id: str
    dataset_id: str
    dataset_name: str
    limit: int
    def __init__(self, connector_id: _Optional[int] = ..., workspace_id: _Optional[str] = ..., dataset_id: _Optional[str] = ..., dataset_name: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class PowerBITablePreview(_message.Message):
    __slots__ = ("table_name", "arrow_data", "total_rows", "error")
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    ARROW_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    table_name: str
    arrow_data: bytes
    total_rows: int
    error: str
    def __init__(self, table_name: _Optional[str] = ..., arrow_data: _Optional[bytes] = ..., total_rows: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class GetPowerBIDatasetPreviewResponse(_message.Message):
    __slots__ = ("table_previews", "success", "error")
    TABLE_PREVIEWS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    table_previews: _containers.RepeatedCompositeFieldContainer[PowerBITablePreview]
    success: bool
    error: str
    def __init__(self, table_previews: _Optional[_Iterable[_Union[PowerBITablePreview, _Mapping]]] = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...
