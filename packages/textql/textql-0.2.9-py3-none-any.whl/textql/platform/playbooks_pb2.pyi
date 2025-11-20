from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from public import playbook_pb2 as _playbook_pb2
from public import chat_pb2 as _chat_pb2
from public import paradigm_pb2 as _paradigm_pb2
from public import identity_pb2 as _identity_pb2
import paradigm_params_pb2 as _paradigm_params_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetPlaybookRequest(_message.Message):
    __slots__ = ("playbook_id", "limit", "offset")
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    limit: int
    offset: int
    def __init__(self, playbook_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetPlaybookResponse(_message.Message):
    __slots__ = ("playbook", "reports", "total_reports_count")
    PLAYBOOK_FIELD_NUMBER: _ClassVar[int]
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REPORTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    playbook: _playbook_pb2.Playbook
    reports: _containers.RepeatedCompositeFieldContainer[_playbook_pb2.PlaybookReport]
    total_reports_count: int
    def __init__(self, playbook: _Optional[_Union[_playbook_pb2.Playbook, _Mapping]] = ..., reports: _Optional[_Iterable[_Union[_playbook_pb2.PlaybookReport, _Mapping]]] = ..., total_reports_count: _Optional[int] = ...) -> None: ...

class ListPlaybooksRequest(_message.Message):
    __slots__ = ("member_only", "limit", "offset", "search_term", "status_filter", "creator_member_id", "sort_by", "sort_direction", "subscribed_first")
    MEMBER_ONLY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SEARCH_TERM_FIELD_NUMBER: _ClassVar[int]
    STATUS_FILTER_FIELD_NUMBER: _ClassVar[int]
    CREATOR_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_FIRST_FIELD_NUMBER: _ClassVar[int]
    member_only: bool
    limit: int
    offset: int
    search_term: str
    status_filter: _playbook_pb2.PlaybookStatus
    creator_member_id: str
    sort_by: _playbook_pb2.PlaybookSortField
    sort_direction: _playbook_pb2.SortDirection
    subscribed_first: bool
    def __init__(self, member_only: bool = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., search_term: _Optional[str] = ..., status_filter: _Optional[_Union[_playbook_pb2.PlaybookStatus, str]] = ..., creator_member_id: _Optional[str] = ..., sort_by: _Optional[_Union[_playbook_pb2.PlaybookSortField, str]] = ..., sort_direction: _Optional[_Union[_playbook_pb2.SortDirection, str]] = ..., subscribed_first: bool = ...) -> None: ...

class ListPlaybooksResponse(_message.Message):
    __slots__ = ("playbooks", "total_count")
    PLAYBOOKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    playbooks: _containers.RepeatedCompositeFieldContainer[_playbook_pb2.Playbook]
    total_count: int
    def __init__(self, playbooks: _Optional[_Iterable[_Union[_playbook_pb2.Playbook, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreatePlaybookRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreatePlaybookResponse(_message.Message):
    __slots__ = ("playbook", "created_at")
    PLAYBOOK_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    playbook: _playbook_pb2.Playbook
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, playbook: _Optional[_Union[_playbook_pb2.Playbook, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdatePlaybookRequest(_message.Message):
    __slots__ = ("playbook_id", "name", "prompt", "status", "trigger_type", "cron_string", "dataset_ids", "connector_id", "reference_report_id", "paradigm_options", "paradigm_type", "email_addresses", "slack_channel_id", "tagged_slack_user_ids", "report_output_style", "template_header_id", "selected_template_data_ids", "max_concurrent_templates", "auto_optimize_concurrency", "connector_ids")
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_TYPE_FIELD_NUMBER: _ClassVar[int]
    CRON_STRING_FIELD_NUMBER: _ClassVar[int]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_TYPE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    SLACK_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    TAGGED_SLACK_USER_IDS_FIELD_NUMBER: _ClassVar[int]
    REPORT_OUTPUT_STYLE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_HEADER_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTED_TEMPLATE_DATA_IDS_FIELD_NUMBER: _ClassVar[int]
    MAX_CONCURRENT_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    AUTO_OPTIMIZE_CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    name: str
    prompt: str
    status: _playbook_pb2.PlaybookStatus
    trigger_type: _playbook_pb2.PlaybookTriggerType
    cron_string: str
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    connector_id: int
    reference_report_id: str
    paradigm_options: _paradigm_pb2.ParadigmOptions
    paradigm_type: _paradigm_params_pb2.ParadigmType
    email_addresses: _containers.RepeatedScalarFieldContainer[str]
    slack_channel_id: str
    tagged_slack_user_ids: _containers.RepeatedScalarFieldContainer[str]
    report_output_style: _playbook_pb2.PlaybookReportStyle
    template_header_id: str
    selected_template_data_ids: _containers.RepeatedScalarFieldContainer[str]
    max_concurrent_templates: int
    auto_optimize_concurrency: bool
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, playbook_id: _Optional[str] = ..., name: _Optional[str] = ..., prompt: _Optional[str] = ..., status: _Optional[_Union[_playbook_pb2.PlaybookStatus, str]] = ..., trigger_type: _Optional[_Union[_playbook_pb2.PlaybookTriggerType, str]] = ..., cron_string: _Optional[str] = ..., dataset_ids: _Optional[_Iterable[str]] = ..., connector_id: _Optional[int] = ..., reference_report_id: _Optional[str] = ..., paradigm_options: _Optional[_Union[_paradigm_pb2.ParadigmOptions, _Mapping]] = ..., paradigm_type: _Optional[_Union[_paradigm_params_pb2.ParadigmType, str]] = ..., email_addresses: _Optional[_Iterable[str]] = ..., slack_channel_id: _Optional[str] = ..., tagged_slack_user_ids: _Optional[_Iterable[str]] = ..., report_output_style: _Optional[_Union[_playbook_pb2.PlaybookReportStyle, str]] = ..., template_header_id: _Optional[str] = ..., selected_template_data_ids: _Optional[_Iterable[str]] = ..., max_concurrent_templates: _Optional[int] = ..., auto_optimize_concurrency: bool = ..., connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class UpdatePlaybookResponse(_message.Message):
    __slots__ = ("playbook", "updated_fields", "updated_at")
    PLAYBOOK_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    playbook: _playbook_pb2.Playbook
    updated_fields: _containers.RepeatedScalarFieldContainer[str]
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, playbook: _Optional[_Union[_playbook_pb2.Playbook, _Mapping]] = ..., updated_fields: _Optional[_Iterable[str]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeployPlaybookRequest(_message.Message):
    __slots__ = ("playbook_id",)
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    def __init__(self, playbook_id: _Optional[str] = ...) -> None: ...

class DeployPlaybookResponse(_message.Message):
    __slots__ = ("playbook_id", "deployed_at")
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYED_AT_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    deployed_at: _timestamp_pb2.Timestamp
    def __init__(self, playbook_id: _Optional[str] = ..., deployed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeletePlaybookRequest(_message.Message):
    __slots__ = ("playbook_id",)
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    def __init__(self, playbook_id: _Optional[str] = ...) -> None: ...

class DeletePlaybookResponse(_message.Message):
    __slots__ = ("playbook_id", "deleted_at")
    PLAYBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    playbook_id: str
    deleted_at: _timestamp_pb2.Timestamp
    def __init__(self, playbook_id: _Optional[str] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
