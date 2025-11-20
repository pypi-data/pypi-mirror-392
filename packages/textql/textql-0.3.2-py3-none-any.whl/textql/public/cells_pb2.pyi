from public import dataset_pb2 as _dataset_pb2
from public import dataframe_pb2 as _dataframe_pb2
from public import ontology_pb2 as _ontology_pb2
from public import powerbi_pb2 as _powerbi_pb2
from public import report_pb2 as _report_pb2
import paradigm_params_pb2 as _paradigm_params_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WebSearchType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNKNOWN: _ClassVar[WebSearchType]
    TYPE_RESEARCH: _ClassVar[WebSearchType]
    TYPE_QUESTION: _ClassVar[WebSearchType]
    TYPE_CONTENTS: _ClassVar[WebSearchType]

class DateRange(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANGE_UNKNOWN: _ClassVar[DateRange]
    RANGE_ALL: _ClassVar[DateRange]
    RANGE_PAST_DAY: _ClassVar[DateRange]
    RANGE_PAST_WEEK: _ClassVar[DateRange]
    RANGE_PAST_MONTH: _ClassVar[DateRange]
    RANGE_PAST_YEAR: _ClassVar[DateRange]

class ContextPromptEditorAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTION_UNKNOWN: _ClassVar[ContextPromptEditorAction]
    ACTION_GET: _ClassVar[ContextPromptEditorAction]
    ACTION_PROPOSE: _ClassVar[ContextPromptEditorAction]
    ACTION_CREATE: _ClassVar[ContextPromptEditorAction]

class ContextPromptChangeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNKNOWN: _ClassVar[ContextPromptChangeStatus]
    STATUS_DRAFT: _ClassVar[ContextPromptChangeStatus]
    STATUS_PENDING: _ClassVar[ContextPromptChangeStatus]
    STATUS_REJECTED: _ClassVar[ContextPromptChangeStatus]
    STATUS_APPLIED: _ClassVar[ContextPromptChangeStatus]

class OntologyEditorAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ONTOLOGY_ACTION_UNKNOWN: _ClassVar[OntologyEditorAction]
    ONTOLOGY_ACTION_LIST: _ClassVar[OntologyEditorAction]
    ONTOLOGY_ACTION_OBJECT: _ClassVar[OntologyEditorAction]
    ONTOLOGY_ACTION_LINK: _ClassVar[OntologyEditorAction]
    ONTOLOGY_ACTION_ATTRIBUTE: _ClassVar[OntologyEditorAction]

class OntologyEditorListType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIST_TYPE_UNKNOWN: _ClassVar[OntologyEditorListType]
    LIST_TYPE_OBJECTS: _ClassVar[OntologyEditorListType]
    LIST_TYPE_LINKS: _ClassVar[OntologyEditorListType]
    LIST_TYPE_ATTRIBUTES: _ClassVar[OntologyEditorListType]
    LIST_TYPE_METRICS: _ClassVar[OntologyEditorListType]

class OntologyEditorOperation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_UNKNOWN: _ClassVar[OntologyEditorOperation]
    OPERATION_CREATE: _ClassVar[OntologyEditorOperation]
    OPERATION_UPDATE: _ClassVar[OntologyEditorOperation]
    OPERATION_DELETE: _ClassVar[OntologyEditorOperation]

class OntologyEditorStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ONTOLOGY_STATUS_UNKNOWN: _ClassVar[OntologyEditorStatus]
    ONTOLOGY_STATUS_DRAFT: _ClassVar[OntologyEditorStatus]
    ONTOLOGY_STATUS_APPLIED: _ClassVar[OntologyEditorStatus]
    ONTOLOGY_STATUS_REJECTED: _ClassVar[OntologyEditorStatus]
    ONTOLOGY_STATUS_ERROR: _ClassVar[OntologyEditorStatus]

class PlaybookEditorAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBOOK_ACTION_UNKNOWN: _ClassVar[PlaybookEditorAction]
    PLAYBOOK_ACTION_LIST: _ClassVar[PlaybookEditorAction]
    PLAYBOOK_ACTION_GET: _ClassVar[PlaybookEditorAction]
    PLAYBOOK_ACTION_CREATE: _ClassVar[PlaybookEditorAction]
    PLAYBOOK_ACTION_UPDATE: _ClassVar[PlaybookEditorAction]
    PLAYBOOK_ACTION_RUN: _ClassVar[PlaybookEditorAction]

class FormEditorAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORM_EDITOR_ACTION_UNKNOWN: _ClassVar[FormEditorAction]
    FORM_EDITOR_ACTION_INFO: _ClassVar[FormEditorAction]
    FORM_EDITOR_ACTION_VIEW: _ClassVar[FormEditorAction]
    FORM_EDITOR_ACTION_CREATE: _ClassVar[FormEditorAction]
    FORM_EDITOR_ACTION_UPDATE: _ClassVar[FormEditorAction]

class EditableFormStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EDITABLE_FORM_STATUS_UNKNOWN: _ClassVar[EditableFormStatus]
    EDITABLE_FORM_STATUS_DRAFT: _ClassVar[EditableFormStatus]
    EDITABLE_FORM_STATUS_MODIFIED: _ClassVar[EditableFormStatus]
    EDITABLE_FORM_STATUS_SUBMITTING: _ClassVar[EditableFormStatus]
    EDITABLE_FORM_STATUS_SUBMITTED: _ClassVar[EditableFormStatus]
    EDITABLE_FORM_STATUS_REJECTED: _ClassVar[EditableFormStatus]

class PlaybookStatusLight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBOOK_STATUS_UNKNOWN: _ClassVar[PlaybookStatusLight]
    PLAYBOOK_STATUS_ACTIVE: _ClassVar[PlaybookStatusLight]
    PLAYBOOK_STATUS_INACTIVE: _ClassVar[PlaybookStatusLight]

class PlaybookReportStyleLight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_STYLE_LIGHT_UNKNOWN: _ClassVar[PlaybookReportStyleLight]
    REPORT_STYLE_LIGHT_EXECUTIVE: _ClassVar[PlaybookReportStyleLight]
    REPORT_STYLE_LIGHT_VERBOSE: _ClassVar[PlaybookReportStyleLight]
    REPORT_STYLE_LIGHT_CONCISE: _ClassVar[PlaybookReportStyleLight]
TYPE_UNKNOWN: WebSearchType
TYPE_RESEARCH: WebSearchType
TYPE_QUESTION: WebSearchType
TYPE_CONTENTS: WebSearchType
RANGE_UNKNOWN: DateRange
RANGE_ALL: DateRange
RANGE_PAST_DAY: DateRange
RANGE_PAST_WEEK: DateRange
RANGE_PAST_MONTH: DateRange
RANGE_PAST_YEAR: DateRange
ACTION_UNKNOWN: ContextPromptEditorAction
ACTION_GET: ContextPromptEditorAction
ACTION_PROPOSE: ContextPromptEditorAction
ACTION_CREATE: ContextPromptEditorAction
STATUS_UNKNOWN: ContextPromptChangeStatus
STATUS_DRAFT: ContextPromptChangeStatus
STATUS_PENDING: ContextPromptChangeStatus
STATUS_REJECTED: ContextPromptChangeStatus
STATUS_APPLIED: ContextPromptChangeStatus
ONTOLOGY_ACTION_UNKNOWN: OntologyEditorAction
ONTOLOGY_ACTION_LIST: OntologyEditorAction
ONTOLOGY_ACTION_OBJECT: OntologyEditorAction
ONTOLOGY_ACTION_LINK: OntologyEditorAction
ONTOLOGY_ACTION_ATTRIBUTE: OntologyEditorAction
LIST_TYPE_UNKNOWN: OntologyEditorListType
LIST_TYPE_OBJECTS: OntologyEditorListType
LIST_TYPE_LINKS: OntologyEditorListType
LIST_TYPE_ATTRIBUTES: OntologyEditorListType
LIST_TYPE_METRICS: OntologyEditorListType
OPERATION_UNKNOWN: OntologyEditorOperation
OPERATION_CREATE: OntologyEditorOperation
OPERATION_UPDATE: OntologyEditorOperation
OPERATION_DELETE: OntologyEditorOperation
ONTOLOGY_STATUS_UNKNOWN: OntologyEditorStatus
ONTOLOGY_STATUS_DRAFT: OntologyEditorStatus
ONTOLOGY_STATUS_APPLIED: OntologyEditorStatus
ONTOLOGY_STATUS_REJECTED: OntologyEditorStatus
ONTOLOGY_STATUS_ERROR: OntologyEditorStatus
PLAYBOOK_ACTION_UNKNOWN: PlaybookEditorAction
PLAYBOOK_ACTION_LIST: PlaybookEditorAction
PLAYBOOK_ACTION_GET: PlaybookEditorAction
PLAYBOOK_ACTION_CREATE: PlaybookEditorAction
PLAYBOOK_ACTION_UPDATE: PlaybookEditorAction
PLAYBOOK_ACTION_RUN: PlaybookEditorAction
FORM_EDITOR_ACTION_UNKNOWN: FormEditorAction
FORM_EDITOR_ACTION_INFO: FormEditorAction
FORM_EDITOR_ACTION_VIEW: FormEditorAction
FORM_EDITOR_ACTION_CREATE: FormEditorAction
FORM_EDITOR_ACTION_UPDATE: FormEditorAction
EDITABLE_FORM_STATUS_UNKNOWN: EditableFormStatus
EDITABLE_FORM_STATUS_DRAFT: EditableFormStatus
EDITABLE_FORM_STATUS_MODIFIED: EditableFormStatus
EDITABLE_FORM_STATUS_SUBMITTING: EditableFormStatus
EDITABLE_FORM_STATUS_SUBMITTED: EditableFormStatus
EDITABLE_FORM_STATUS_REJECTED: EditableFormStatus
PLAYBOOK_STATUS_UNKNOWN: PlaybookStatusLight
PLAYBOOK_STATUS_ACTIVE: PlaybookStatusLight
PLAYBOOK_STATUS_INACTIVE: PlaybookStatusLight
REPORT_STYLE_LIGHT_UNKNOWN: PlaybookReportStyleLight
REPORT_STYLE_LIGHT_EXECUTIVE: PlaybookReportStyleLight
REPORT_STYLE_LIGHT_VERBOSE: PlaybookReportStyleLight
REPORT_STYLE_LIGHT_CONCISE: PlaybookReportStyleLight

class MarkdownCell(_message.Message):
    __slots__ = ("content", "rendered_html")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    RENDERED_HTML_FIELD_NUMBER: _ClassVar[int]
    content: str
    rendered_html: str
    def __init__(self, content: _Optional[str] = ..., rendered_html: _Optional[str] = ...) -> None: ...

class SQLCell(_message.Message):
    __slots__ = ("query", "connector_id", "dataframe", "dataframe_preview")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    query: str
    connector_id: int
    dataframe: _dataframe_pb2.DataFrameWithInfo
    dataframe_preview: str
    def __init__(self, query: _Optional[str] = ..., connector_id: _Optional[int] = ..., dataframe: _Optional[_Union[_dataframe_pb2.DataFrameWithInfo, _Mapping]] = ..., dataframe_preview: _Optional[str] = ...) -> None: ...

class PythonCell(_message.Message):
    __slots__ = ("code", "output", "dataframe_info", "dataframe_preview", "images", "files", "html_screenshots")
    CODE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_INFO_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    HTML_SCREENSHOTS_FIELD_NUMBER: _ClassVar[int]
    code: str
    output: _containers.RepeatedScalarFieldContainer[str]
    dataframe_info: _containers.RepeatedCompositeFieldContainer[_dataframe_pb2.DataFrameInfo]
    dataframe_preview: _containers.RepeatedScalarFieldContainer[str]
    images: _containers.RepeatedCompositeFieldContainer[ImageReference]
    files: _containers.RepeatedCompositeFieldContainer[FileReference]
    html_screenshots: _containers.RepeatedCompositeFieldContainer[ImageReference]
    def __init__(self, code: _Optional[str] = ..., output: _Optional[_Iterable[str]] = ..., dataframe_info: _Optional[_Iterable[_Union[_dataframe_pb2.DataFrameInfo, _Mapping]]] = ..., dataframe_preview: _Optional[_Iterable[str]] = ..., images: _Optional[_Iterable[_Union[ImageReference, _Mapping]]] = ..., files: _Optional[_Iterable[_Union[FileReference, _Mapping]]] = ..., html_screenshots: _Optional[_Iterable[_Union[ImageReference, _Mapping]]] = ...) -> None: ...

class StreamlitCell(_message.Message):
    __slots__ = ("code", "url", "error_message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    url: str
    error_message: str
    def __init__(self, code: _Optional[str] = ..., url: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class MetricsCell(_message.Message):
    __slots__ = ("query", "dataset", "ontology_id", "dataframe", "dataframe_preview", "generated_sql", "query_id", "error_message")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    GENERATED_SQL_FIELD_NUMBER: _ClassVar[int]
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    query: str
    dataset: str
    ontology_id: int
    dataframe: _dataframe_pb2.DataFrameWithInfo
    dataframe_preview: str
    generated_sql: str
    query_id: str
    error_message: str
    def __init__(self, query: _Optional[str] = ..., dataset: _Optional[str] = ..., ontology_id: _Optional[int] = ..., dataframe: _Optional[_Union[_dataframe_pb2.DataFrameWithInfo, _Mapping]] = ..., dataframe_preview: _Optional[str] = ..., generated_sql: _Optional[str] = ..., query_id: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class ImageReference(_message.Message):
    __slots__ = ("name", "url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class FileReference(_message.Message):
    __slots__ = ("name", "url", "file_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    file_type: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ..., file_type: _Optional[str] = ...) -> None: ...

class SQLReference(_message.Message):
    __slots__ = ("tool_id",)
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    tool_id: str
    def __init__(self, tool_id: _Optional[str] = ...) -> None: ...

class AnswerCell(_message.Message):
    __slots__ = ("content", "images", "sql")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    content: str
    images: _containers.RepeatedCompositeFieldContainer[ImageReference]
    sql: _containers.RepeatedCompositeFieldContainer[SQLReference]
    def __init__(self, content: _Optional[str] = ..., images: _Optional[_Iterable[_Union[ImageReference, _Mapping]]] = ..., sql: _Optional[_Iterable[_Union[SQLReference, _Mapping]]] = ...) -> None: ...

class DocumentCell(_message.Message):
    __slots__ = ("name", "url", "preview", "dataset_source_id", "page_count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    DATASET_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    preview: str
    dataset_source_id: str
    page_count: int
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ..., preview: _Optional[str] = ..., dataset_source_id: _Optional[str] = ..., page_count: _Optional[int] = ...) -> None: ...

class TabularFileCell(_message.Message):
    __slots__ = ("file_name", "category", "dataframes", "dataset_source_id")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DATAFRAMES_FIELD_NUMBER: _ClassVar[int]
    DATASET_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    category: _dataset_pb2.TabularFileCategory
    dataframes: _containers.RepeatedCompositeFieldContainer[_dataframe_pb2.DataFrameInfo]
    dataset_source_id: str
    def __init__(self, file_name: _Optional[str] = ..., category: _Optional[_Union[_dataset_pb2.TabularFileCategory, str]] = ..., dataframes: _Optional[_Iterable[_Union[_dataframe_pb2.DataFrameInfo, _Mapping]]] = ..., dataset_source_id: _Optional[str] = ...) -> None: ...

class ImageCell(_message.Message):
    __slots__ = ("name", "url", "mime_type", "width", "height", "size_bytes", "dataset_source_id", "alt_text", "caption")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    DATASET_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ALT_TEXT_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    mime_type: str
    width: int
    height: int
    size_bytes: int
    dataset_source_id: str
    alt_text: str
    caption: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ..., mime_type: _Optional[str] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., size_bytes: _Optional[int] = ..., dataset_source_id: _Optional[str] = ..., alt_text: _Optional[str] = ..., caption: _Optional[str] = ...) -> None: ...

class TextCell(_message.Message):
    __slots__ = ("file_name", "content", "mime_type", "size_bytes", "dataset_source_id", "line_count")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    DATASET_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    LINE_COUNT_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    content: str
    mime_type: str
    size_bytes: int
    dataset_source_id: str
    line_count: int
    def __init__(self, file_name: _Optional[str] = ..., content: _Optional[str] = ..., mime_type: _Optional[str] = ..., size_bytes: _Optional[int] = ..., dataset_source_id: _Optional[str] = ..., line_count: _Optional[int] = ...) -> None: ...

class ExaSearchResult(_message.Message):
    __slots__ = ("title", "url", "text", "author", "published_date", "favicon", "image", "score", "highlights", "highlight_scores", "summary")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_DATE_FIELD_NUMBER: _ClassVar[int]
    FAVICON_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTS_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_SCORES_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    text: str
    author: str
    published_date: str
    favicon: str
    image: str
    score: float
    highlights: _containers.RepeatedScalarFieldContainer[str]
    highlight_scores: _containers.RepeatedScalarFieldContainer[float]
    summary: str
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., text: _Optional[str] = ..., author: _Optional[str] = ..., published_date: _Optional[str] = ..., favicon: _Optional[str] = ..., image: _Optional[str] = ..., score: _Optional[float] = ..., highlights: _Optional[_Iterable[str]] = ..., highlight_scores: _Optional[_Iterable[float]] = ..., summary: _Optional[str] = ...) -> None: ...

class WebSearchCell(_message.Message):
    __slots__ = ("query", "search_type", "date_range", "answer", "exa_results", "cost_dollars")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SEARCH_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    EXA_RESULTS_FIELD_NUMBER: _ClassVar[int]
    COST_DOLLARS_FIELD_NUMBER: _ClassVar[int]
    query: str
    search_type: WebSearchType
    date_range: DateRange
    answer: str
    exa_results: _containers.RepeatedCompositeFieldContainer[ExaSearchResult]
    cost_dollars: float
    def __init__(self, query: _Optional[str] = ..., search_type: _Optional[_Union[WebSearchType, str]] = ..., date_range: _Optional[_Union[DateRange, str]] = ..., answer: _Optional[str] = ..., exa_results: _Optional[_Iterable[_Union[ExaSearchResult, _Mapping]]] = ..., cost_dollars: _Optional[float] = ...) -> None: ...

class ReportCell(_message.Message):
    __slots__ = ("subject", "summary", "blocks", "html_preview", "chat_id", "report_id")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    HTML_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    subject: str
    summary: str
    blocks: _containers.RepeatedCompositeFieldContainer[_report_pb2.ReportBlock]
    html_preview: str
    chat_id: str
    report_id: str
    def __init__(self, subject: _Optional[str] = ..., summary: _Optional[str] = ..., blocks: _Optional[_Iterable[_Union[_report_pb2.ReportBlock, _Mapping]]] = ..., html_preview: _Optional[str] = ..., chat_id: _Optional[str] = ..., report_id: _Optional[str] = ...) -> None: ...

class SummaryCell(_message.Message):
    __slots__ = ("summary",)
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    summary: str
    def __init__(self, summary: _Optional[str] = ...) -> None: ...

class StatusCell(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class TableauCell(_message.Message):
    __slots__ = ("dataset_id", "message_blocks")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    message_blocks: _containers.RepeatedCompositeFieldContainer[TableauMessageBlock]
    def __init__(self, dataset_id: _Optional[str] = ..., message_blocks: _Optional[_Iterable[_Union[TableauMessageBlock, _Mapping]]] = ...) -> None: ...

class TableauMessageBlock(_message.Message):
    __slots__ = ("content", "image_base64", "pdf_base64")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_BASE64_FIELD_NUMBER: _ClassVar[int]
    PDF_BASE64_FIELD_NUMBER: _ClassVar[int]
    content: str
    image_base64: str
    pdf_base64: str
    def __init__(self, content: _Optional[str] = ..., image_base64: _Optional[str] = ..., pdf_base64: _Optional[str] = ...) -> None: ...

class TableauSQLCell(_message.Message):
    __slots__ = ("tableau_datasource_luid", "query", "dataframe", "dataframe_preview")
    TABLEAU_DATASOURCE_LUID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    tableau_datasource_luid: str
    query: str
    dataframe: _dataframe_pb2.DataFrameWithInfo
    dataframe_preview: str
    def __init__(self, tableau_datasource_luid: _Optional[str] = ..., query: _Optional[str] = ..., dataframe: _Optional[_Union[_dataframe_pb2.DataFrameWithInfo, _Mapping]] = ..., dataframe_preview: _Optional[str] = ...) -> None: ...

class TableauSearchFieldsCell(_message.Message):
    __slots__ = ("search_term", "result_text")
    SEARCH_TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_TEXT_FIELD_NUMBER: _ClassVar[int]
    search_term: str
    result_text: str
    def __init__(self, search_term: _Optional[str] = ..., result_text: _Optional[str] = ...) -> None: ...

class PowerBIMessageBlock(_message.Message):
    __slots__ = ("content", "image_base64")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_BASE64_FIELD_NUMBER: _ClassVar[int]
    content: str
    image_base64: str
    def __init__(self, content: _Optional[str] = ..., image_base64: _Optional[str] = ...) -> None: ...

class PowerBICell(_message.Message):
    __slots__ = ("dataset_id", "report_ids", "powerbi_dataset_ids", "message_blocks")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_IDS_FIELD_NUMBER: _ClassVar[int]
    POWERBI_DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    report_ids: _containers.RepeatedScalarFieldContainer[str]
    powerbi_dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    message_blocks: _containers.RepeatedCompositeFieldContainer[PowerBIMessageBlock]
    def __init__(self, dataset_id: _Optional[str] = ..., report_ids: _Optional[_Iterable[str]] = ..., powerbi_dataset_ids: _Optional[_Iterable[str]] = ..., message_blocks: _Optional[_Iterable[_Union[PowerBIMessageBlock, _Mapping]]] = ...) -> None: ...

class PowerBIDAXCell(_message.Message):
    __slots__ = ("dataset_id", "dax_query", "dataframe", "dataframe_preview")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DAX_QUERY_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dax_query: str
    dataframe: _dataframe_pb2.DataFrameWithInfo
    dataframe_preview: str
    def __init__(self, dataset_id: _Optional[str] = ..., dax_query: _Optional[str] = ..., dataframe: _Optional[_Union[_dataframe_pb2.DataFrameWithInfo, _Mapping]] = ..., dataframe_preview: _Optional[str] = ...) -> None: ...

class ContextPromptEditorEditPair(_message.Message):
    __slots__ = ("old_string", "new_string")
    OLD_STRING_FIELD_NUMBER: _ClassVar[int]
    NEW_STRING_FIELD_NUMBER: _ClassVar[int]
    old_string: str
    new_string: str
    def __init__(self, old_string: _Optional[str] = ..., new_string: _Optional[str] = ...) -> None: ...

class ContextPromptEditorCell(_message.Message):
    __slots__ = ("action", "current_context", "proposed_context", "diff", "status", "error_message", "context_id")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CURRENT_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    PROPOSED_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    DIFF_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ID_FIELD_NUMBER: _ClassVar[int]
    action: ContextPromptEditorAction
    current_context: str
    proposed_context: str
    diff: str
    status: ContextPromptChangeStatus
    error_message: str
    context_id: str
    def __init__(self, action: _Optional[_Union[ContextPromptEditorAction, str]] = ..., current_context: _Optional[str] = ..., proposed_context: _Optional[str] = ..., diff: _Optional[str] = ..., status: _Optional[_Union[ContextPromptChangeStatus, str]] = ..., error_message: _Optional[str] = ..., context_id: _Optional[str] = ...) -> None: ...

class OntologyEditorListFilter(_message.Message):
    __slots__ = ("object_id",)
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    def __init__(self, object_id: _Optional[str] = ...) -> None: ...

class OntologyEditorCell(_message.Message):
    __slots__ = ("action", "list_type", "operation", "status", "list_filter", "list_count", "list_objects", "list_attributes", "list_relations", "list_metrics", "created_object", "created_attributes", "updated_object", "deleted_object", "created_attribute", "updated_attribute", "deleted_attribute", "created_link", "updated_link", "deleted_link", "created_metric", "updated_metric", "deleted_metric")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    LIST_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FILTER_FIELD_NUMBER: _ClassVar[int]
    LIST_COUNT_FIELD_NUMBER: _ClassVar[int]
    LIST_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    LIST_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    LIST_RELATIONS_FIELD_NUMBER: _ClassVar[int]
    LIST_METRICS_FIELD_NUMBER: _ClassVar[int]
    CREATED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    CREATED_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    DELETED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    CREATED_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    DELETED_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    CREATED_LINK_FIELD_NUMBER: _ClassVar[int]
    UPDATED_LINK_FIELD_NUMBER: _ClassVar[int]
    DELETED_LINK_FIELD_NUMBER: _ClassVar[int]
    CREATED_METRIC_FIELD_NUMBER: _ClassVar[int]
    UPDATED_METRIC_FIELD_NUMBER: _ClassVar[int]
    DELETED_METRIC_FIELD_NUMBER: _ClassVar[int]
    action: OntologyEditorAction
    list_type: OntologyEditorListType
    operation: OntologyEditorOperation
    status: OntologyEditorStatus
    list_filter: OntologyEditorListFilter
    list_count: int
    list_objects: _containers.RepeatedCompositeFieldContainer[_ontology_pb2.OntologyObject]
    list_attributes: _containers.RepeatedCompositeFieldContainer[_ontology_pb2.OntologyAttribute]
    list_relations: _containers.RepeatedCompositeFieldContainer[_ontology_pb2.OntologyRelation]
    list_metrics: _containers.RepeatedCompositeFieldContainer[_ontology_pb2.OntologyMetric]
    created_object: _ontology_pb2.OntologyObject
    created_attributes: _containers.RepeatedCompositeFieldContainer[_ontology_pb2.OntologyAttribute]
    updated_object: _ontology_pb2.OntologyObject
    deleted_object: _ontology_pb2.OntologyObject
    created_attribute: _ontology_pb2.OntologyAttribute
    updated_attribute: _ontology_pb2.OntologyAttribute
    deleted_attribute: _ontology_pb2.OntologyAttribute
    created_link: _ontology_pb2.OntologyRelation
    updated_link: _ontology_pb2.OntologyRelation
    deleted_link: _ontology_pb2.OntologyRelation
    created_metric: _ontology_pb2.OntologyMetric
    updated_metric: _ontology_pb2.OntologyMetric
    deleted_metric: _ontology_pb2.OntologyMetric
    def __init__(self, action: _Optional[_Union[OntologyEditorAction, str]] = ..., list_type: _Optional[_Union[OntologyEditorListType, str]] = ..., operation: _Optional[_Union[OntologyEditorOperation, str]] = ..., status: _Optional[_Union[OntologyEditorStatus, str]] = ..., list_filter: _Optional[_Union[OntologyEditorListFilter, _Mapping]] = ..., list_count: _Optional[int] = ..., list_objects: _Optional[_Iterable[_Union[_ontology_pb2.OntologyObject, _Mapping]]] = ..., list_attributes: _Optional[_Iterable[_Union[_ontology_pb2.OntologyAttribute, _Mapping]]] = ..., list_relations: _Optional[_Iterable[_Union[_ontology_pb2.OntologyRelation, _Mapping]]] = ..., list_metrics: _Optional[_Iterable[_Union[_ontology_pb2.OntologyMetric, _Mapping]]] = ..., created_object: _Optional[_Union[_ontology_pb2.OntologyObject, _Mapping]] = ..., created_attributes: _Optional[_Iterable[_Union[_ontology_pb2.OntologyAttribute, _Mapping]]] = ..., updated_object: _Optional[_Union[_ontology_pb2.OntologyObject, _Mapping]] = ..., deleted_object: _Optional[_Union[_ontology_pb2.OntologyObject, _Mapping]] = ..., created_attribute: _Optional[_Union[_ontology_pb2.OntologyAttribute, _Mapping]] = ..., updated_attribute: _Optional[_Union[_ontology_pb2.OntologyAttribute, _Mapping]] = ..., deleted_attribute: _Optional[_Union[_ontology_pb2.OntologyAttribute, _Mapping]] = ..., created_link: _Optional[_Union[_ontology_pb2.OntologyRelation, _Mapping]] = ..., updated_link: _Optional[_Union[_ontology_pb2.OntologyRelation, _Mapping]] = ..., deleted_link: _Optional[_Union[_ontology_pb2.OntologyRelation, _Mapping]] = ..., created_metric: _Optional[_Union[_ontology_pb2.OntologyMetric, _Mapping]] = ..., updated_metric: _Optional[_Union[_ontology_pb2.OntologyMetric, _Mapping]] = ..., deleted_metric: _Optional[_Union[_ontology_pb2.OntologyMetric, _Mapping]] = ...) -> None: ...

class MCPToolCell(_message.Message):
    __slots__ = ("server_name", "tool_name", "arguments_json", "content_json", "is_error", "error_message", "execution_time_ms")
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_JSON_FIELD_NUMBER: _ClassVar[int]
    CONTENT_JSON_FIELD_NUMBER: _ClassVar[int]
    IS_ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    server_name: str
    tool_name: str
    arguments_json: str
    content_json: str
    is_error: bool
    error_message: str
    execution_time_ms: int
    def __init__(self, server_name: _Optional[str] = ..., tool_name: _Optional[str] = ..., arguments_json: _Optional[str] = ..., content_json: _Optional[str] = ..., is_error: bool = ..., error_message: _Optional[str] = ..., execution_time_ms: _Optional[int] = ...) -> None: ...

class PreviewCell(_message.Message):
    __slots__ = ("target", "preview_type", "name", "url", "content", "error")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    target: str
    preview_type: str
    name: str
    url: str
    content: str
    error: str
    def __init__(self, target: _Optional[str] = ..., preview_type: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ..., content: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class FormEditorCell(_message.Message):
    __slots__ = ("action", "form_snapshot", "form", "form_id")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    FORM_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    FORM_FIELD_NUMBER: _ClassVar[int]
    FORM_ID_FIELD_NUMBER: _ClassVar[int]
    action: FormEditorAction
    form_snapshot: EditableForm
    form: EditableForm
    form_id: str
    def __init__(self, action: _Optional[_Union[FormEditorAction, str]] = ..., form_snapshot: _Optional[_Union[EditableForm, _Mapping]] = ..., form: _Optional[_Union[EditableForm, _Mapping]] = ..., form_id: _Optional[str] = ...) -> None: ...

class EditableForm(_message.Message):
    __slots__ = ("form_name", "fields", "status", "id", "submit_error", "submit_result", "validation_error")
    FORM_NAME_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_ERROR_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_RESULT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_ERROR_FIELD_NUMBER: _ClassVar[int]
    form_name: str
    fields: _struct_pb2.Struct
    status: EditableFormStatus
    id: str
    submit_error: str
    submit_result: str
    validation_error: str
    def __init__(self, form_name: _Optional[str] = ..., fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., status: _Optional[_Union[EditableFormStatus, str]] = ..., id: _Optional[str] = ..., submit_error: _Optional[str] = ..., submit_result: _Optional[str] = ..., validation_error: _Optional[str] = ...) -> None: ...

class ConnectorRef(_message.Message):
    __slots__ = ("id", "name", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    type: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class OrgMemberRef(_message.Message):
    __slots__ = ("email", "name")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class SlackChannelRef(_message.Message):
    __slots__ = ("channel_id", "name")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    channel_id: str
    name: str
    def __init__(self, channel_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class SlackUserRef(_message.Message):
    __slots__ = ("user_id", "name")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    def __init__(self, user_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class PlaybookFieldChange(_message.Message):
    __slots__ = ("field_name", "old_value", "new_value")
    FIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    OLD_VALUE_FIELD_NUMBER: _ClassVar[int]
    NEW_VALUE_FIELD_NUMBER: _ClassVar[int]
    field_name: str
    old_value: str
    new_value: str
    def __init__(self, field_name: _Optional[str] = ..., old_value: _Optional[str] = ..., new_value: _Optional[str] = ...) -> None: ...

class PlaybookInfo(_message.Message):
    __slots__ = ("id", "name", "prompt", "owner_id", "owner_email", "created_at", "updated_at", "cron_string", "datasets", "email_addresses", "slack_channel_id", "tagged_slack_user_ids", "status", "connector_id", "paradigm_type", "report_output_style", "is_subscribed", "connector_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CRON_STRING_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    SLACK_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    TAGGED_SLACK_USER_IDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORT_OUTPUT_STYLE_FIELD_NUMBER: _ClassVar[int]
    IS_SUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    prompt: str
    owner_id: str
    owner_email: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    cron_string: str
    datasets: _containers.RepeatedCompositeFieldContainer[_dataset_pb2.Dataset]
    email_addresses: _containers.RepeatedScalarFieldContainer[str]
    slack_channel_id: str
    tagged_slack_user_ids: _containers.RepeatedScalarFieldContainer[str]
    status: PlaybookStatusLight
    connector_id: int
    paradigm_type: _paradigm_params_pb2.ParadigmType
    report_output_style: PlaybookReportStyleLight
    is_subscribed: bool
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., prompt: _Optional[str] = ..., owner_id: _Optional[str] = ..., owner_email: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cron_string: _Optional[str] = ..., datasets: _Optional[_Iterable[_Union[_dataset_pb2.Dataset, _Mapping]]] = ..., email_addresses: _Optional[_Iterable[str]] = ..., slack_channel_id: _Optional[str] = ..., tagged_slack_user_ids: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[PlaybookStatusLight, str]] = ..., connector_id: _Optional[int] = ..., paradigm_type: _Optional[_Union[_paradigm_params_pb2.ParadigmType, str]] = ..., report_output_style: _Optional[_Union[PlaybookReportStyleLight, str]] = ..., is_subscribed: bool = ..., connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class PlaybookEditorCell(_message.Message):
    __slots__ = ("action", "playbooks", "error_message", "total_count", "slack_channels", "slack_users", "connectors", "org_members", "has_slack", "field_changes")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOKS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    SLACK_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SLACK_USERS_FIELD_NUMBER: _ClassVar[int]
    CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    ORG_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    HAS_SLACK_FIELD_NUMBER: _ClassVar[int]
    FIELD_CHANGES_FIELD_NUMBER: _ClassVar[int]
    action: PlaybookEditorAction
    playbooks: _containers.RepeatedCompositeFieldContainer[PlaybookInfo]
    error_message: str
    total_count: int
    slack_channels: _containers.RepeatedCompositeFieldContainer[SlackChannelRef]
    slack_users: _containers.RepeatedCompositeFieldContainer[SlackUserRef]
    connectors: _containers.RepeatedCompositeFieldContainer[ConnectorRef]
    org_members: _containers.RepeatedCompositeFieldContainer[OrgMemberRef]
    has_slack: bool
    field_changes: _containers.RepeatedCompositeFieldContainer[PlaybookFieldChange]
    def __init__(self, action: _Optional[_Union[PlaybookEditorAction, str]] = ..., playbooks: _Optional[_Iterable[_Union[PlaybookInfo, _Mapping]]] = ..., error_message: _Optional[str] = ..., total_count: _Optional[int] = ..., slack_channels: _Optional[_Iterable[_Union[SlackChannelRef, _Mapping]]] = ..., slack_users: _Optional[_Iterable[_Union[SlackUserRef, _Mapping]]] = ..., connectors: _Optional[_Iterable[_Union[ConnectorRef, _Mapping]]] = ..., org_members: _Optional[_Iterable[_Union[OrgMemberRef, _Mapping]]] = ..., has_slack: bool = ..., field_changes: _Optional[_Iterable[_Union[PlaybookFieldChange, _Mapping]]] = ...) -> None: ...

class GoogleDriveFile(_message.Message):
    __slots__ = ("id", "name", "mime_type", "size", "modified_time", "web_view_link")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_TIME_FIELD_NUMBER: _ClassVar[int]
    WEB_VIEW_LINK_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    mime_type: str
    size: int
    modified_time: str
    web_view_link: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., mime_type: _Optional[str] = ..., size: _Optional[int] = ..., modified_time: _Optional[str] = ..., web_view_link: _Optional[str] = ...) -> None: ...

class GoogleDriveSearchCell(_message.Message):
    __slots__ = ("files", "dataframe_preview", "error_message", "file_count")
    FILES_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[GoogleDriveFile]
    dataframe_preview: str
    error_message: str
    file_count: int
    def __init__(self, files: _Optional[_Iterable[_Union[GoogleDriveFile, _Mapping]]] = ..., dataframe_preview: _Optional[str] = ..., error_message: _Optional[str] = ..., file_count: _Optional[int] = ...) -> None: ...

class GoogleDriveContentCell(_message.Message):
    __slots__ = ("file_name", "content_type", "content", "file_id", "error_message")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    content_type: str
    content: str
    file_id: str
    error_message: str
    def __init__(self, file_name: _Optional[str] = ..., content_type: _Optional[str] = ..., content: _Optional[str] = ..., file_id: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class PreviewCellRef(_message.Message):
    __slots__ = ("target", "preview_type", "name", "url")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    target: str
    preview_type: str
    name: str
    url: str
    def __init__(self, target: _Optional[str] = ..., preview_type: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class ReportHistoryInfo(_message.Message):
    __slots__ = ("id", "chat_id", "cell_id", "created_at", "subject", "summary", "blocks", "read_at", "preview_cells", "html_preview")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_CELLS_FIELD_NUMBER: _ClassVar[int]
    HTML_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    id: str
    chat_id: str
    cell_id: str
    created_at: _timestamp_pb2.Timestamp
    subject: str
    summary: str
    blocks: _containers.RepeatedCompositeFieldContainer[_report_pb2.ReportBlock]
    read_at: _timestamp_pb2.Timestamp
    preview_cells: _containers.RepeatedCompositeFieldContainer[PreviewCellRef]
    html_preview: str
    def __init__(self, id: _Optional[str] = ..., chat_id: _Optional[str] = ..., cell_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., subject: _Optional[str] = ..., summary: _Optional[str] = ..., blocks: _Optional[_Iterable[_Union[_report_pb2.ReportBlock, _Mapping]]] = ..., read_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., preview_cells: _Optional[_Iterable[_Union[PreviewCellRef, _Mapping]]] = ..., html_preview: _Optional[str] = ...) -> None: ...

class ReportHistoryCell(_message.Message):
    __slots__ = ("reports", "total_count", "error_message")
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[ReportHistoryInfo]
    total_count: int
    error_message: str
    def __init__(self, reports: _Optional[_Iterable[_Union[ReportHistoryInfo, _Mapping]]] = ..., total_count: _Optional[int] = ..., error_message: _Optional[str] = ...) -> None: ...
