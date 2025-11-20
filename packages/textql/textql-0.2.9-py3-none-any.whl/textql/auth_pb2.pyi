from google.protobuf import timestamp_pb2 as _timestamp_pb2
import paradigm_params_pb2 as _paradigm_params_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Theme(_message.Message):
    __slots__ = ("bg", "header_bg", "card_bg", "primary_accent", "card_accent", "heading", "text", "card_heading", "card_text", "logo_url")
    BG_FIELD_NUMBER: _ClassVar[int]
    HEADER_BG_FIELD_NUMBER: _ClassVar[int]
    CARD_BG_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_ACCENT_FIELD_NUMBER: _ClassVar[int]
    CARD_ACCENT_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CARD_HEADING_FIELD_NUMBER: _ClassVar[int]
    CARD_TEXT_FIELD_NUMBER: _ClassVar[int]
    LOGO_URL_FIELD_NUMBER: _ClassVar[int]
    bg: str
    header_bg: str
    card_bg: str
    primary_accent: str
    card_accent: str
    heading: str
    text: str
    card_heading: str
    card_text: str
    logo_url: str
    def __init__(self, bg: _Optional[str] = ..., header_bg: _Optional[str] = ..., card_bg: _Optional[str] = ..., primary_accent: _Optional[str] = ..., card_accent: _Optional[str] = ..., heading: _Optional[str] = ..., text: _Optional[str] = ..., card_heading: _Optional[str] = ..., card_text: _Optional[str] = ..., logo_url: _Optional[str] = ...) -> None: ...

class Organization(_message.Message):
    __slots__ = ("org_id", "slack_team_id", "slack_key", "default_connector_id", "limit_data_visibility", "require_attached", "organization_name", "created_at", "updated_at", "organization_logo_url", "email_allowed_domains", "allowed_auth_methods", "theme", "org_meta", "inject_whole_ontology_disable_search", "onboarding_video_link", "warning", "public_preview", "chat_v5_cutover", "credit_cap", "credit_cap_effective_date", "default_paradigm_mode", "secrets_enabled", "email_polling_enabled", "logo_url", "brand_name", "paradigm_params", "default_llm_model", "preferred_provider", "tool_restrictions", "console_access", "default_connector_ids")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    SLACK_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    SLACK_KEY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_DATA_VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ATTACHED_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_LOGO_URL_FIELD_NUMBER: _ClassVar[int]
    EMAIL_ALLOWED_DOMAINS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_AUTH_METHODS_FIELD_NUMBER: _ClassVar[int]
    THEME_FIELD_NUMBER: _ClassVar[int]
    ORG_META_FIELD_NUMBER: _ClassVar[int]
    INJECT_WHOLE_ONTOLOGY_DISABLE_SEARCH_FIELD_NUMBER: _ClassVar[int]
    ONBOARDING_VIDEO_LINK_FIELD_NUMBER: _ClassVar[int]
    WARNING_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    CHAT_V5_CUTOVER_FIELD_NUMBER: _ClassVar[int]
    CREDIT_CAP_FIELD_NUMBER: _ClassVar[int]
    CREDIT_CAP_EFFECTIVE_DATE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PARADIGM_MODE_FIELD_NUMBER: _ClassVar[int]
    SECRETS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    EMAIL_POLLING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    LOGO_URL_FIELD_NUMBER: _ClassVar[int]
    BRAND_NAME_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_PARAMS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_LLM_MODEL_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_ACCESS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    slack_team_id: str
    slack_key: str
    default_connector_id: int
    limit_data_visibility: bool
    require_attached: bool
    organization_name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    organization_logo_url: str
    email_allowed_domains: _containers.RepeatedScalarFieldContainer[str]
    allowed_auth_methods: _containers.RepeatedScalarFieldContainer[str]
    theme: Theme
    org_meta: str
    inject_whole_ontology_disable_search: bool
    onboarding_video_link: str
    warning: str
    public_preview: bool
    chat_v5_cutover: bool
    credit_cap: int
    credit_cap_effective_date: _timestamp_pb2.Timestamp
    default_paradigm_mode: _paradigm_params_pb2.ParadigmType
    secrets_enabled: bool
    email_polling_enabled: bool
    logo_url: str
    brand_name: str
    paradigm_params: _paradigm_params_pb2.ParadigmParams
    default_llm_model: int
    preferred_provider: str
    tool_restrictions: _paradigm_params_pb2.ParadigmParams
    console_access: bool
    default_connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, org_id: _Optional[str] = ..., slack_team_id: _Optional[str] = ..., slack_key: _Optional[str] = ..., default_connector_id: _Optional[int] = ..., limit_data_visibility: bool = ..., require_attached: bool = ..., organization_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., organization_logo_url: _Optional[str] = ..., email_allowed_domains: _Optional[_Iterable[str]] = ..., allowed_auth_methods: _Optional[_Iterable[str]] = ..., theme: _Optional[_Union[Theme, _Mapping]] = ..., org_meta: _Optional[str] = ..., inject_whole_ontology_disable_search: bool = ..., onboarding_video_link: _Optional[str] = ..., warning: _Optional[str] = ..., public_preview: bool = ..., chat_v5_cutover: bool = ..., credit_cap: _Optional[int] = ..., credit_cap_effective_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., default_paradigm_mode: _Optional[_Union[_paradigm_params_pb2.ParadigmType, str]] = ..., secrets_enabled: bool = ..., email_polling_enabled: bool = ..., logo_url: _Optional[str] = ..., brand_name: _Optional[str] = ..., paradigm_params: _Optional[_Union[_paradigm_params_pb2.ParadigmParams, _Mapping]] = ..., default_llm_model: _Optional[int] = ..., preferred_provider: _Optional[str] = ..., tool_restrictions: _Optional[_Union[_paradigm_params_pb2.ParadigmParams, _Mapping]] = ..., console_access: bool = ..., default_connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class Member(_message.Message):
    __slots__ = ("id", "org_id", "member_id", "role", "preferred_first_name", "preferred_last_name", "show_code", "profile_image_url", "email_address", "name", "is_admin", "selected_connector_id", "roles", "created_at", "updated_at", "paradigm_params", "email_verified", "selected_connector_ids", "user_message_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    SHOW_CODE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    EMAIL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ADMIN_FIELD_NUMBER: _ClassVar[int]
    SELECTED_CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_PARAMS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    SELECTED_CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    USER_MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: int
    org_id: str
    member_id: str
    role: str
    preferred_first_name: str
    preferred_last_name: str
    show_code: bool
    profile_image_url: str
    email_address: str
    name: str
    is_admin: bool
    selected_connector_id: int
    roles: _containers.RepeatedScalarFieldContainer[str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    paradigm_params: _paradigm_params_pb2.ParadigmParams
    email_verified: bool
    selected_connector_ids: _containers.RepeatedScalarFieldContainer[int]
    user_message_count: int
    def __init__(self, id: _Optional[int] = ..., org_id: _Optional[str] = ..., member_id: _Optional[str] = ..., role: _Optional[str] = ..., preferred_first_name: _Optional[str] = ..., preferred_last_name: _Optional[str] = ..., show_code: bool = ..., profile_image_url: _Optional[str] = ..., email_address: _Optional[str] = ..., name: _Optional[str] = ..., is_admin: bool = ..., selected_connector_id: _Optional[int] = ..., roles: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., paradigm_params: _Optional[_Union[_paradigm_params_pb2.ParadigmParams, _Mapping]] = ..., email_verified: bool = ..., selected_connector_ids: _Optional[_Iterable[int]] = ..., user_message_count: _Optional[int] = ...) -> None: ...

class Token(_message.Message):
    __slots__ = ("token", "user_id", "expires_at")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    token: str
    user_id: str
    expires_at: _timestamp_pb2.Timestamp
    def __init__(self, token: _Optional[str] = ..., user_id: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OIDCConfig(_message.Message):
    __slots__ = ("org_id", "display_name", "issuer_url", "client_id", "client_secret", "scopes", "provider_type", "attribute_mapping")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ISSUER_URL_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_MAPPING_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    display_name: str
    issuer_url: str
    client_id: str
    client_secret: str
    scopes: str
    provider_type: str
    attribute_mapping: str
    def __init__(self, org_id: _Optional[str] = ..., display_name: _Optional[str] = ..., issuer_url: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ..., scopes: _Optional[str] = ..., provider_type: _Optional[str] = ..., attribute_mapping: _Optional[str] = ...) -> None: ...

class StartSessionRequest(_message.Message):
    __slots__ = ("long_term_access_token", "org_id")
    LONG_TERM_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    long_term_access_token: str
    org_id: str
    def __init__(self, long_term_access_token: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class SessionResponse(_message.Message):
    __slots__ = ("member", "organization", "session_token")
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    member: Member
    organization: Organization
    session_token: str
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ..., organization: _Optional[_Union[Organization, _Mapping]] = ..., session_token: _Optional[str] = ...) -> None: ...

class CreateOrgRequest(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class CreateOrgResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class FindOrgsBySlugRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class FindOrgsBySlugResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[Organization, _Mapping]]] = ...) -> None: ...

class UpdateOrgRequest(_message.Message):
    __slots__ = ("organization", "session_token")
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    session_token: str
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ..., session_token: _Optional[str] = ...) -> None: ...

class UpdateOrgResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class GetOrgByIdRequest(_message.Message):
    __slots__ = ("org_id",)
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    def __init__(self, org_id: _Optional[str] = ...) -> None: ...

class GetOrgByIdResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class RenewSessionRequest(_message.Message):
    __slots__ = ("session_token",)
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    session_token: str
    def __init__(self, session_token: _Optional[str] = ...) -> None: ...

class RenewLongTermAccessTokenRequest(_message.Message):
    __slots__ = ("long_term_access_token",)
    LONG_TERM_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    long_term_access_token: str
    def __init__(self, long_term_access_token: _Optional[str] = ...) -> None: ...

class LongTermAccessTokenResponse(_message.Message):
    __slots__ = ("long_term_access_token",)
    LONG_TERM_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    long_term_access_token: str
    def __init__(self, long_term_access_token: _Optional[str] = ...) -> None: ...

class CreateOrgMemberRequest(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class CreateOrgMemberResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class FindMembersInOrgRequest(_message.Message):
    __slots__ = ("org_id",)
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    def __init__(self, org_id: _Optional[str] = ...) -> None: ...

class FindMembersInOrgResponse(_message.Message):
    __slots__ = ("members",)
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[Member]
    def __init__(self, members: _Optional[_Iterable[_Union[Member, _Mapping]]] = ...) -> None: ...

class EmailInviteMemberRequest(_message.Message):
    __slots__ = ("org_id", "email", "role", "session_token")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    email: str
    role: str
    session_token: str
    def __init__(self, org_id: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[str] = ..., session_token: _Optional[str] = ...) -> None: ...

class EmailInviteMemberResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetOrgMemberByMemberIdRequest(_message.Message):
    __slots__ = ("member_id", "session_token")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    session_token: str
    def __init__(self, member_id: _Optional[str] = ..., session_token: _Optional[str] = ...) -> None: ...

class GetOrgMemberByMemberIdResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class DeleteMemberRequest(_message.Message):
    __slots__ = ("member_id", "session_token", "hard_delete")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    HARD_DELETE_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    session_token: str
    hard_delete: bool
    def __init__(self, member_id: _Optional[str] = ..., session_token: _Optional[str] = ..., hard_delete: bool = ...) -> None: ...

class DeleteMemberResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DeleteOrganizationRequest(_message.Message):
    __slots__ = ("session_token",)
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    session_token: str
    def __init__(self, session_token: _Optional[str] = ...) -> None: ...

class DeleteOrganizationResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
