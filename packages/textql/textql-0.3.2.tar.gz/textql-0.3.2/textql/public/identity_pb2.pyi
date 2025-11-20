from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Session(_message.Message):
    __slots__ = ("member_id", "organization_id", "roles")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    organization_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, member_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class MemberPreview(_message.Message):
    __slots__ = ("member_id", "member_email", "member_name", "member_picture_url")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PICTURE_URL_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    member_email: str
    member_name: str
    member_picture_url: str
    def __init__(self, member_id: _Optional[str] = ..., member_email: _Optional[str] = ..., member_name: _Optional[str] = ..., member_picture_url: _Optional[str] = ...) -> None: ...
