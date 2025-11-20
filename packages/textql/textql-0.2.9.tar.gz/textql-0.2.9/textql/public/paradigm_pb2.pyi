import paradigm_params_pb2 as _paradigm_params_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Paradigm(_message.Message):
    __slots__ = ("type", "version", "options")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    type: _paradigm_params_pb2.ParadigmType
    version: int
    options: ParadigmOptions
    def __init__(self, type: _Optional[_Union[_paradigm_params_pb2.ParadigmType, str]] = ..., version: _Optional[int] = ..., options: _Optional[_Union[ParadigmOptions, _Mapping]] = ...) -> None: ...

class ParadigmOptions(_message.Message):
    __slots__ = ("sql", "research", "ontology", "basic", "tableau", "experimental", "universal")
    SQL_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    BASIC_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_FIELD_NUMBER: _ClassVar[int]
    UNIVERSAL_FIELD_NUMBER: _ClassVar[int]
    sql: SqlOptions
    research: ResearchOptions
    ontology: OntologyOptions
    basic: BasicOptions
    tableau: TableauOptions
    experimental: ExperimentalOptions
    universal: UniversalOptions
    def __init__(self, sql: _Optional[_Union[SqlOptions, _Mapping]] = ..., research: _Optional[_Union[ResearchOptions, _Mapping]] = ..., ontology: _Optional[_Union[OntologyOptions, _Mapping]] = ..., basic: _Optional[_Union[BasicOptions, _Mapping]] = ..., tableau: _Optional[_Union[TableauOptions, _Mapping]] = ..., experimental: _Optional[_Union[ExperimentalOptions, _Mapping]] = ..., universal: _Optional[_Union[UniversalOptions, _Mapping]] = ...) -> None: ...

class SqlOptions(_message.Message):
    __slots__ = ("connector_ids",)
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class ResearchOptions(_message.Message):
    __slots__ = ("connector_ids", "background_color", "logo")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_COLOR_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    background_color: str
    logo: str
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., background_color: _Optional[str] = ..., logo: _Optional[str] = ...) -> None: ...

class ExperimentalOptions(_message.Message):
    __slots__ = ("connector_ids", "auto_approve_enabled")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    AUTO_APPROVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    auto_approve_enabled: bool
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., auto_approve_enabled: bool = ...) -> None: ...

class BasicOptions(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OntologyOptions(_message.Message):
    __slots__ = ("connector_ids", "ontology_ids")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_IDS_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    ontology_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., ontology_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class TableauOptions(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class UniversalOptions(_message.Message):
    __slots__ = ("connector_ids", "dataset_id", "web_search_enabled", "sql_enabled", "ontology_enabled", "ontology_editing_enabled", "auto_approve_enabled", "python_enabled", "streamlit_enabled", "google_drive_enabled", "powerbi_enabled", "context_editing_enabled", "form_editor_enabled")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    WEB_SEARCH_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SQL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_EDITING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AUTO_APPROVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PYTHON_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAMLIT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    POWERBI_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_EDITING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FORM_EDITOR_ENABLED_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    dataset_id: str
    web_search_enabled: bool
    sql_enabled: bool
    ontology_enabled: bool
    ontology_editing_enabled: bool
    auto_approve_enabled: bool
    python_enabled: bool
    streamlit_enabled: bool
    google_drive_enabled: bool
    powerbi_enabled: bool
    context_editing_enabled: bool
    form_editor_enabled: bool
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., dataset_id: _Optional[str] = ..., web_search_enabled: bool = ..., sql_enabled: bool = ..., ontology_enabled: bool = ..., ontology_editing_enabled: bool = ..., auto_approve_enabled: bool = ..., python_enabled: bool = ..., streamlit_enabled: bool = ..., google_drive_enabled: bool = ..., powerbi_enabled: bool = ..., context_editing_enabled: bool = ..., form_editor_enabled: bool = ...) -> None: ...

class GoogleDriveOptions(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...
