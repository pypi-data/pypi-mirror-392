from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(_message.Message):
    __slots__ = ("id", "org_id", "name", "description", "is_system", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    name: str
    description: str
    is_system: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_system: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("id", "resource", "action", "description", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource: str
    action: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., resource: _Optional[str] = ..., action: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ObjectAccess(_message.Message):
    __slots__ = ("id", "org_id", "object_type", "object_id", "created_by", "is_public", "member_id", "role_id", "access_type", "granted_by", "expires_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    GRANTED_BY_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    object_type: str
    object_id: str
    created_by: str
    is_public: bool
    member_id: str
    role_id: str
    access_type: str
    granted_by: str
    expires_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., created_by: _Optional[str] = ..., is_public: bool = ..., member_id: _Optional[str] = ..., role_id: _Optional[str] = ..., access_type: _Optional[str] = ..., granted_by: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateRoleRequest(_message.Message):
    __slots__ = ("name", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class CreateRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: Role
    def __init__(self, role: _Optional[_Union[Role, _Mapping]] = ...) -> None: ...

class GetRoleRequest(_message.Message):
    __slots__ = ("role_id",)
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    def __init__(self, role_id: _Optional[str] = ...) -> None: ...

class GetRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: Role
    def __init__(self, role: _Optional[_Union[Role, _Mapping]] = ...) -> None: ...

class ListRolesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class UpdateRoleRequest(_message.Message):
    __slots__ = ("role_id", "name", "description")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    name: str
    description: str
    def __init__(self, role_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: Role
    def __init__(self, role: _Optional[_Union[Role, _Mapping]] = ...) -> None: ...

class DeleteRoleRequest(_message.Message):
    __slots__ = ("role_id",)
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    def __init__(self, role_id: _Optional[str] = ...) -> None: ...

class DeleteRoleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListPermissionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPermissionsResponse(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...

class GetRolePermissionsRequest(_message.Message):
    __slots__ = ("role_id",)
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    def __init__(self, role_id: _Optional[str] = ...) -> None: ...

class GetRolePermissionsResponse(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...

class AssignPermissionToRoleRequest(_message.Message):
    __slots__ = ("role_id", "permission_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    permission_id: str
    def __init__(self, role_id: _Optional[str] = ..., permission_id: _Optional[str] = ...) -> None: ...

class AssignPermissionToRoleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RemovePermissionFromRoleRequest(_message.Message):
    __slots__ = ("role_id", "permission_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    permission_id: str
    def __init__(self, role_id: _Optional[str] = ..., permission_id: _Optional[str] = ...) -> None: ...

class RemovePermissionFromRoleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class AssignRoleToMemberRequest(_message.Message):
    __slots__ = ("member_id", "role_id")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    role_id: str
    def __init__(self, member_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class AssignRoleToMemberResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RemoveRoleFromMemberRequest(_message.Message):
    __slots__ = ("member_id", "role_id")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    role_id: str
    def __init__(self, member_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class RemoveRoleFromMemberResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetMemberRolesRequest(_message.Message):
    __slots__ = ("member_ids",)
    MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    member_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, member_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetMemberRolesResponse(_message.Message):
    __slots__ = ("member_roles",)
    class MemberRolesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MemberRoles
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MemberRoles, _Mapping]] = ...) -> None: ...
    MEMBER_ROLES_FIELD_NUMBER: _ClassVar[int]
    member_roles: _containers.MessageMap[str, MemberRoles]
    def __init__(self, member_roles: _Optional[_Mapping[str, MemberRoles]] = ...) -> None: ...

class MemberRoles(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class GetCurrentMemberRolesAndPermissionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentMemberRolesAndPermissionsResponse(_message.Message):
    __slots__ = ("roles", "permissions")
    ROLES_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...

class ShareObjectRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "member_id", "access_type", "expires_at", "is_public")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    member_id: str
    access_type: str
    expires_at: _timestamp_pb2.Timestamp
    is_public: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., member_id: _Optional[str] = ..., access_type: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_public: bool = ...) -> None: ...

class ShareObjectResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ShareObjectWithRoleRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "role_id", "access_type", "expires_at", "is_public")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    role_id: str
    access_type: str
    expires_at: _timestamp_pb2.Timestamp
    is_public: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., role_id: _Optional[str] = ..., access_type: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_public: bool = ...) -> None: ...

class ShareObjectWithRoleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RevokeObjectAccessRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "member_id", "role_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    member_id: str
    role_id: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., member_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class RevokeObjectAccessResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetObjectAccessRequest(_message.Message):
    __slots__ = ("object_type", "object_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...

class GetObjectAccessResponse(_message.Message):
    __slots__ = ("access_entries",)
    ACCESS_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    access_entries: _containers.RepeatedCompositeFieldContainer[ObjectAccess]
    def __init__(self, access_entries: _Optional[_Iterable[_Union[ObjectAccess, _Mapping]]] = ...) -> None: ...

class HasObjectAccessRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "member_id", "role_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    member_id: str
    role_id: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., member_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class HasObjectAccessResponse(_message.Message):
    __slots__ = ("has_access",)
    HAS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    has_access: bool
    def __init__(self, has_access: bool = ...) -> None: ...

class UpdateObjectVisibilityRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "is_public")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    is_public: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., is_public: bool = ...) -> None: ...

class UpdateObjectVisibilityResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UpdateObjectAccessRequest(_message.Message):
    __slots__ = ("access_id", "access_type", "expires_at")
    ACCESS_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    access_id: str
    access_type: str
    expires_at: _timestamp_pb2.Timestamp
    def __init__(self, access_id: _Optional[str] = ..., access_type: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdateObjectAccessResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GenerateShareLinkRequest(_message.Message):
    __slots__ = ("object_type", "object_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...

class GenerateShareLinkResponse(_message.Message):
    __slots__ = ("share_link",)
    SHARE_LINK_FIELD_NUMBER: _ClassVar[int]
    share_link: str
    def __init__(self, share_link: _Optional[str] = ...) -> None: ...

class AccessRequest(_message.Message):
    __slots__ = ("id", "org_id", "object_type", "object_id", "member_id", "requested_access_type", "justification", "request_message", "status", "reviewed_by", "rejection_reason", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    JUSTIFICATION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REVIEWED_BY_FIELD_NUMBER: _ClassVar[int]
    REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    object_type: str
    object_id: str
    member_id: str
    requested_access_type: str
    justification: str
    request_message: str
    status: str
    reviewed_by: str
    rejection_reason: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., member_id: _Optional[str] = ..., requested_access_type: _Optional[str] = ..., justification: _Optional[str] = ..., request_message: _Optional[str] = ..., status: _Optional[str] = ..., reviewed_by: _Optional[str] = ..., rejection_reason: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RequestAccessRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "requested_access_type", "justification", "request_message")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    JUSTIFICATION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    requested_access_type: str
    justification: str
    request_message: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., requested_access_type: _Optional[str] = ..., justification: _Optional[str] = ..., request_message: _Optional[str] = ...) -> None: ...

class RequestAccessResponse(_message.Message):
    __slots__ = ("success", "request_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    request_id: str
    def __init__(self, success: bool = ..., request_id: _Optional[str] = ...) -> None: ...

class ListAccessRequestsRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "status")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    status: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class ListAccessRequestsResponse(_message.Message):
    __slots__ = ("requests",)
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[AccessRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[AccessRequest, _Mapping]]] = ...) -> None: ...

class ApproveAccessRequestRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class ApproveAccessRequestResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RejectAccessRequestRequest(_message.Message):
    __slots__ = ("request_id", "rejection_reason")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    rejection_reason: str
    def __init__(self, request_id: _Optional[str] = ..., rejection_reason: _Optional[str] = ...) -> None: ...

class RejectAccessRequestResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ApiKey(_message.Message):
    __slots__ = ("id", "member_id", "client_id", "created_at", "api_key_short")
    ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    API_KEY_SHORT_FIELD_NUMBER: _ClassVar[int]
    id: str
    member_id: str
    client_id: str
    created_at: _timestamp_pb2.Timestamp
    api_key_short: str
    def __init__(self, id: _Optional[str] = ..., member_id: _Optional[str] = ..., client_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., api_key_short: _Optional[str] = ...) -> None: ...

class CreateApiKeyRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateApiKeyResponse(_message.Message):
    __slots__ = ("api_key", "api_key_hash")
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    API_KEY_HASH_FIELD_NUMBER: _ClassVar[int]
    api_key: ApiKey
    api_key_hash: str
    def __init__(self, api_key: _Optional[_Union[ApiKey, _Mapping]] = ..., api_key_hash: _Optional[str] = ...) -> None: ...

class ListApiKeysRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListApiKeysResponse(_message.Message):
    __slots__ = ("api_keys",)
    API_KEYS_FIELD_NUMBER: _ClassVar[int]
    api_keys: _containers.RepeatedCompositeFieldContainer[ApiKey]
    def __init__(self, api_keys: _Optional[_Iterable[_Union[ApiKey, _Mapping]]] = ...) -> None: ...

class UpdateApiKeyRequest(_message.Message):
    __slots__ = ("api_key_id", "client_id")
    API_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    api_key_id: str
    client_id: str
    def __init__(self, api_key_id: _Optional[str] = ..., client_id: _Optional[str] = ...) -> None: ...

class UpdateApiKeyResponse(_message.Message):
    __slots__ = ("api_key",)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: ApiKey
    def __init__(self, api_key: _Optional[_Union[ApiKey, _Mapping]] = ...) -> None: ...

class DeleteApiKeyRequest(_message.Message):
    __slots__ = ("api_key_id",)
    API_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    api_key_id: str
    def __init__(self, api_key_id: _Optional[str] = ...) -> None: ...

class DeleteApiKeyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetEmbedUserApiKeyRequest(_message.Message):
    __slots__ = ("member_id",)
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    def __init__(self, member_id: _Optional[str] = ...) -> None: ...

class GetEmbedUserApiKeyResponse(_message.Message):
    __slots__ = ("api_key_base64", "api_key_short", "service_account_email")
    API_KEY_BASE64_FIELD_NUMBER: _ClassVar[int]
    API_KEY_SHORT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    api_key_base64: str
    api_key_short: str
    service_account_email: str
    def __init__(self, api_key_base64: _Optional[str] = ..., api_key_short: _Optional[str] = ..., service_account_email: _Optional[str] = ...) -> None: ...

class CreateServiceAccountRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateServiceAccountResponse(_message.Message):
    __slots__ = ("member_id", "email", "api_key_base64", "api_key_short", "api_key_obj")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    API_KEY_BASE64_FIELD_NUMBER: _ClassVar[int]
    API_KEY_SHORT_FIELD_NUMBER: _ClassVar[int]
    API_KEY_OBJ_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    email: str
    api_key_base64: str
    api_key_short: str
    api_key_obj: ApiKey
    def __init__(self, member_id: _Optional[str] = ..., email: _Optional[str] = ..., api_key_base64: _Optional[str] = ..., api_key_short: _Optional[str] = ..., api_key_obj: _Optional[_Union[ApiKey, _Mapping]] = ...) -> None: ...
