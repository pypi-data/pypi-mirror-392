from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ACUUsageChatCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACU_USAGE_CHAT_CATEGORY_UNKNOWN: _ClassVar[ACUUsageChatCategory]
    ACU_USAGE_CHAT_CATEGORY_CHAT: _ClassVar[ACUUsageChatCategory]
    ACU_USAGE_CHAT_CATEGORY_PLAYBOOK: _ClassVar[ACUUsageChatCategory]
    ACU_USAGE_CHAT_CATEGORY_SLACK: _ClassVar[ACUUsageChatCategory]

class ACUUsageUsageCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACU_USAGE_USAGE_CATEGORY_UNKNOWN: _ClassVar[ACUUsageUsageCategory]
    ACU_USAGE_USAGE_CATEGORY_SANDBOX: _ClassVar[ACUUsageUsageCategory]
    ACU_USAGE_USAGE_CATEGORY_TOKENS: _ClassVar[ACUUsageUsageCategory]
    ACU_USAGE_USAGE_CATEGORY_TOOLS: _ClassVar[ACUUsageUsageCategory]

class DateTruncInterval(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATE_TRUNC_INTERVAL_UNKNOWN: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_MICROSECONDS: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_MILLISECONDS: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_SECOND: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_MINUTE: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_HOUR: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_DAY: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_WEEK: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_MONTH: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_QUARTER: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_YEAR: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_DECADE: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_CENTURY: _ClassVar[DateTruncInterval]
    DATE_TRUNC_INTERVAL_MILLENNIUM: _ClassVar[DateTruncInterval]
ACU_USAGE_CHAT_CATEGORY_UNKNOWN: ACUUsageChatCategory
ACU_USAGE_CHAT_CATEGORY_CHAT: ACUUsageChatCategory
ACU_USAGE_CHAT_CATEGORY_PLAYBOOK: ACUUsageChatCategory
ACU_USAGE_CHAT_CATEGORY_SLACK: ACUUsageChatCategory
ACU_USAGE_USAGE_CATEGORY_UNKNOWN: ACUUsageUsageCategory
ACU_USAGE_USAGE_CATEGORY_SANDBOX: ACUUsageUsageCategory
ACU_USAGE_USAGE_CATEGORY_TOKENS: ACUUsageUsageCategory
ACU_USAGE_USAGE_CATEGORY_TOOLS: ACUUsageUsageCategory
DATE_TRUNC_INTERVAL_UNKNOWN: DateTruncInterval
DATE_TRUNC_INTERVAL_MICROSECONDS: DateTruncInterval
DATE_TRUNC_INTERVAL_MILLISECONDS: DateTruncInterval
DATE_TRUNC_INTERVAL_SECOND: DateTruncInterval
DATE_TRUNC_INTERVAL_MINUTE: DateTruncInterval
DATE_TRUNC_INTERVAL_HOUR: DateTruncInterval
DATE_TRUNC_INTERVAL_DAY: DateTruncInterval
DATE_TRUNC_INTERVAL_WEEK: DateTruncInterval
DATE_TRUNC_INTERVAL_MONTH: DateTruncInterval
DATE_TRUNC_INTERVAL_QUARTER: DateTruncInterval
DATE_TRUNC_INTERVAL_YEAR: DateTruncInterval
DATE_TRUNC_INTERVAL_DECADE: DateTruncInterval
DATE_TRUNC_INTERVAL_CENTURY: DateTruncInterval
DATE_TRUNC_INTERVAL_MILLENNIUM: DateTruncInterval

class GetACUUsageRequest(_message.Message):
    __slots__ = ("to", "interval")
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    to: _timestamp_pb2.Timestamp
    interval: DateTruncInterval
    def __init__(self, to: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., interval: _Optional[_Union[DateTruncInterval, str]] = ..., **kwargs) -> None: ...

class GetACUUsageResponse(_message.Message):
    __slots__ = ("usage",)
    USAGE_FIELD_NUMBER: _ClassVar[int]
    usage: _containers.RepeatedCompositeFieldContainer[ACUUsage]
    def __init__(self, usage: _Optional[_Iterable[_Union[ACUUsage, _Mapping]]] = ...) -> None: ...

class ACUUsageWithCategory(_message.Message):
    __slots__ = ("acus", "chat_category", "usage_category")
    ACUS_FIELD_NUMBER: _ClassVar[int]
    CHAT_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    USAGE_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    acus: float
    chat_category: ACUUsageChatCategory
    usage_category: ACUUsageUsageCategory
    def __init__(self, acus: _Optional[float] = ..., chat_category: _Optional[_Union[ACUUsageChatCategory, str]] = ..., usage_category: _Optional[_Union[ACUUsageUsageCategory, str]] = ...) -> None: ...

class ACUUsage(_message.Message):
    __slots__ = ("org_id", "timestamp", "usage")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    timestamp: _timestamp_pb2.Timestamp
    usage: _containers.RepeatedCompositeFieldContainer[ACUUsageWithCategory]
    def __init__(self, org_id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., usage: _Optional[_Iterable[_Union[ACUUsageWithCategory, _Mapping]]] = ...) -> None: ...
