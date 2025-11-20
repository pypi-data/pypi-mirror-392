from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableauItemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ITEM_TYPE_UNKNOWN: _ClassVar[TableauItemType]
    ITEM_TYPE_PROJECT: _ClassVar[TableauItemType]
    ITEM_TYPE_WORKBOOK: _ClassVar[TableauItemType]
    ITEM_TYPE_VIEW: _ClassVar[TableauItemType]
    ITEM_TYPE_DATASOURCE: _ClassVar[TableauItemType]
ITEM_TYPE_UNKNOWN: TableauItemType
ITEM_TYPE_PROJECT: TableauItemType
ITEM_TYPE_WORKBOOK: TableauItemType
ITEM_TYPE_VIEW: TableauItemType
ITEM_TYPE_DATASOURCE: TableauItemType

class TestTableauConnectionRequest(_message.Message):
    __slots__ = ("connector_id", "server_url", "site_name", "pat_name", "pat_secret")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_URL_FIELD_NUMBER: _ClassVar[int]
    SITE_NAME_FIELD_NUMBER: _ClassVar[int]
    PAT_NAME_FIELD_NUMBER: _ClassVar[int]
    PAT_SECRET_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    server_url: str
    site_name: str
    pat_name: str
    pat_secret: str
    def __init__(self, connector_id: _Optional[int] = ..., server_url: _Optional[str] = ..., site_name: _Optional[str] = ..., pat_name: _Optional[str] = ..., pat_secret: _Optional[str] = ...) -> None: ...

class TestTableauConnectionResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class TableauProject(_message.Message):
    __slots__ = ("id", "name", "description", "created_at", "updated_at", "content_permissions", "parent_project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    PARENT_PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    content_permissions: str
    parent_project_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., content_permissions: _Optional[str] = ..., parent_project_id: _Optional[str] = ...) -> None: ...

class ListTableauProjectsRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class ListTableauProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[TableauProject]
    def __init__(self, projects: _Optional[_Iterable[_Union[TableauProject, _Mapping]]] = ...) -> None: ...

class TableauWorkbook(_message.Message):
    __slots__ = ("id", "name", "project_name", "project_id", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    project_name: str
    project_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListTableauWorkbooksRequest(_message.Message):
    __slots__ = ("connector_id", "project_id", "project_name")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    project_id: str
    project_name: str
    def __init__(self, connector_id: _Optional[int] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class ListTableauWorkbooksResponse(_message.Message):
    __slots__ = ("workbooks",)
    WORKBOOKS_FIELD_NUMBER: _ClassVar[int]
    workbooks: _containers.RepeatedCompositeFieldContainer[TableauWorkbook]
    def __init__(self, workbooks: _Optional[_Iterable[_Union[TableauWorkbook, _Mapping]]] = ...) -> None: ...

class TableauView(_message.Message):
    __slots__ = ("id", "name", "content_url", "workbook_id", "workbook_name", "created_at", "updated_at", "embed_url")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_URL_FIELD_NUMBER: _ClassVar[int]
    WORKBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    WORKBOOK_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    EMBED_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    content_url: str
    workbook_id: str
    workbook_name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    embed_url: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., content_url: _Optional[str] = ..., workbook_id: _Optional[str] = ..., workbook_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., embed_url: _Optional[str] = ...) -> None: ...

class ListTableauViewsRequest(_message.Message):
    __slots__ = ("connector_id", "workbook_id", "workbook_name")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    WORKBOOK_NAME_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    workbook_id: str
    workbook_name: str
    def __init__(self, connector_id: _Optional[int] = ..., workbook_id: _Optional[str] = ..., workbook_name: _Optional[str] = ...) -> None: ...

class ListTableauViewsResponse(_message.Message):
    __slots__ = ("views",)
    VIEWS_FIELD_NUMBER: _ClassVar[int]
    views: _containers.RepeatedCompositeFieldContainer[TableauView]
    def __init__(self, views: _Optional[_Iterable[_Union[TableauView, _Mapping]]] = ...) -> None: ...

class TableauDatasource(_message.Message):
    __slots__ = ("id", "name", "type", "created_at", "updated_at", "is_published", "project_id", "project_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    is_published: bool
    project_id: str
    project_name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_published: bool = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class ListTableauDatasourcesRequest(_message.Message):
    __slots__ = ("connector_id", "project_id", "workbook_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    WORKBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    project_id: str
    workbook_id: str
    def __init__(self, connector_id: _Optional[int] = ..., project_id: _Optional[str] = ..., workbook_id: _Optional[str] = ...) -> None: ...

class ListTableauDatasourcesResponse(_message.Message):
    __slots__ = ("datasources",)
    DATASOURCES_FIELD_NUMBER: _ClassVar[int]
    datasources: _containers.RepeatedCompositeFieldContainer[TableauDatasource]
    def __init__(self, datasources: _Optional[_Iterable[_Union[TableauDatasource, _Mapping]]] = ...) -> None: ...

class TableauStarredItem(_message.Message):
    __slots__ = ("connector_id", "item_type", "item_id", "item_name", "created_at")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    item_type: TableauItemType
    item_id: str
    item_name: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, connector_id: _Optional[int] = ..., item_type: _Optional[_Union[TableauItemType, str]] = ..., item_id: _Optional[str] = ..., item_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class StarTableauItemRequest(_message.Message):
    __slots__ = ("connector_id", "item_type", "item_id", "item_name")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    item_type: TableauItemType
    item_id: str
    item_name: str
    def __init__(self, connector_id: _Optional[int] = ..., item_type: _Optional[_Union[TableauItemType, str]] = ..., item_id: _Optional[str] = ..., item_name: _Optional[str] = ...) -> None: ...

class StarTableauItemResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UnstarTableauItemRequest(_message.Message):
    __slots__ = ("connector_id", "item_type", "item_id")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    item_type: TableauItemType
    item_id: str
    def __init__(self, connector_id: _Optional[int] = ..., item_type: _Optional[_Union[TableauItemType, str]] = ..., item_id: _Optional[str] = ...) -> None: ...

class UnstarTableauItemResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetStarredTableauItemsRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetStarredTableauItemsResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[TableauStarredItem]
    def __init__(self, items: _Optional[_Iterable[_Union[TableauStarredItem, _Mapping]]] = ...) -> None: ...

class GetCollectionThumbnailRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class GetCollectionThumbnailResponse(_message.Message):
    __slots__ = ("image_url",)
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    def __init__(self, image_url: _Optional[str] = ...) -> None: ...
