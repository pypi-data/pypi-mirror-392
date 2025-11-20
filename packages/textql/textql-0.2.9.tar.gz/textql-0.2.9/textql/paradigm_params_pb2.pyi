from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ParadigmType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNKNOWN: _ClassVar[ParadigmType]
    TYPE_SQL: _ClassVar[ParadigmType]
    TYPE_RESEARCH: _ClassVar[ParadigmType]
    TYPE_ONTOLOGY: _ClassVar[ParadigmType]
    TYPE_BASIC: _ClassVar[ParadigmType]
    TYPE_TABLEAU: _ClassVar[ParadigmType]
    TYPE_EXPERIMENTAL: _ClassVar[ParadigmType]
    TYPE_UNIVERSAL: _ClassVar[ParadigmType]
TYPE_UNKNOWN: ParadigmType
TYPE_SQL: ParadigmType
TYPE_RESEARCH: ParadigmType
TYPE_ONTOLOGY: ParadigmType
TYPE_BASIC: ParadigmType
TYPE_TABLEAU: ParadigmType
TYPE_EXPERIMENTAL: ParadigmType
TYPE_UNIVERSAL: ParadigmType

class ParadigmParams(_message.Message):
    __slots__ = ("web_search_enabled", "sql_enabled", "ontology_enabled", "ontology_editing_enabled", "python_enabled", "powerbi_enabled", "streamlit_enabled", "google_drive_enabled", "auto_approve_enabled", "context_editing_enabled", "form_editor_enabled", "tableau_enabled", "file_upload_enabled")
    WEB_SEARCH_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SQL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_EDITING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PYTHON_ENABLED_FIELD_NUMBER: _ClassVar[int]
    POWERBI_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAMLIT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AUTO_APPROVE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_EDITING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FORM_EDITOR_ENABLED_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILE_UPLOAD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    web_search_enabled: bool
    sql_enabled: bool
    ontology_enabled: bool
    ontology_editing_enabled: bool
    python_enabled: bool
    powerbi_enabled: bool
    streamlit_enabled: bool
    google_drive_enabled: bool
    auto_approve_enabled: bool
    context_editing_enabled: bool
    form_editor_enabled: bool
    tableau_enabled: bool
    file_upload_enabled: bool
    def __init__(self, web_search_enabled: bool = ..., sql_enabled: bool = ..., ontology_enabled: bool = ..., ontology_editing_enabled: bool = ..., python_enabled: bool = ..., powerbi_enabled: bool = ..., streamlit_enabled: bool = ..., google_drive_enabled: bool = ..., auto_approve_enabled: bool = ..., context_editing_enabled: bool = ..., form_editor_enabled: bool = ..., tableau_enabled: bool = ..., file_upload_enabled: bool = ...) -> None: ...
