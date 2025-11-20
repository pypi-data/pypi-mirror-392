import auth_pb2 as _auth_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
import paradigm_params_pb2 as _paradigm_params_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateDefaultConnectorRequest(_message.Message):
    __slots__ = ("connector_ids", "paradigm_params")
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    PARADIGM_PARAMS_FIELD_NUMBER: _ClassVar[int]
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    paradigm_params: _paradigm_params_pb2.ParadigmParams
    def __init__(self, connector_ids: _Optional[_Iterable[int]] = ..., paradigm_params: _Optional[_Union[_paradigm_params_pb2.ParadigmParams, _Mapping]] = ...) -> None: ...

class UpdateDefaultConnectorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LoginEmailStartRequest(_message.Message):
    __slots__ = ("email", "custom_callback_url", "custom_subject", "custom_body_html", "custom_sender_name", "autojoin_token")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CALLBACK_URL_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_BODY_HTML_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTOJOIN_TOKEN_FIELD_NUMBER: _ClassVar[int]
    email: str
    custom_callback_url: str
    custom_subject: str
    custom_body_html: str
    custom_sender_name: str
    autojoin_token: str
    def __init__(self, email: _Optional[str] = ..., custom_callback_url: _Optional[str] = ..., custom_subject: _Optional[str] = ..., custom_body_html: _Optional[str] = ..., custom_sender_name: _Optional[str] = ..., autojoin_token: _Optional[str] = ...) -> None: ...

class LoginEmailStartResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ValidateIntermediaryTokenRequest(_message.Message):
    __slots__ = ("intermediary_token",)
    INTERMEDIARY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    intermediary_token: str
    def __init__(self, intermediary_token: _Optional[str] = ...) -> None: ...

class ValidateIntermediaryTokenResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_auth_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_auth_pb2.Organization, _Mapping]]] = ...) -> None: ...

class ValidateLongTermTokenRequest(_message.Message):
    __slots__ = ("long_term_access_token",)
    LONG_TERM_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    long_term_access_token: str
    def __init__(self, long_term_access_token: _Optional[str] = ...) -> None: ...

class ValidateLongTermTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeIntermediaryTokenRequest(_message.Message):
    __slots__ = ("intermediary_token", "organization_id")
    INTERMEDIARY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    intermediary_token: str
    organization_id: str
    def __init__(self, intermediary_token: _Optional[str] = ..., organization_id: _Optional[str] = ...) -> None: ...

class GetOIDCAuthUrlRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class GetOIDCAuthUrlResponse(_message.Message):
    __slots__ = ("auth_url",)
    AUTH_URL_FIELD_NUMBER: _ClassVar[int]
    auth_url: str
    def __init__(self, auth_url: _Optional[str] = ...) -> None: ...

class HandleOIDCCallbackRequest(_message.Message):
    __slots__ = ("code", "state")
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    code: str
    state: str
    def __init__(self, code: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class HandleOIDCCallbackResponse(_message.Message):
    __slots__ = ("success", "intermediary_token", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIARY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    intermediary_token: str
    error: str
    def __init__(self, success: bool = ..., intermediary_token: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CreateSSOOrganizationRequest(_message.Message):
    __slots__ = ("name", "icon", "oidc_issuer", "oidc_client_id", "oidc_client_secret")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    OIDC_ISSUER_FIELD_NUMBER: _ClassVar[int]
    OIDC_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    OIDC_CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    name: str
    icon: str
    oidc_issuer: str
    oidc_client_id: str
    oidc_client_secret: str
    def __init__(self, name: _Optional[str] = ..., icon: _Optional[str] = ..., oidc_issuer: _Optional[str] = ..., oidc_client_id: _Optional[str] = ..., oidc_client_secret: _Optional[str] = ...) -> None: ...

class CreateSSOOrganizationResponse(_message.Message):
    __slots__ = ("success", "organization", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    organization: _auth_pb2.Organization
    error: str
    def __init__(self, success: bool = ..., organization: _Optional[_Union[_auth_pb2.Organization, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class ListOrganizationsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListOrganizationsResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_auth_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_auth_pb2.Organization, _Mapping]]] = ...) -> None: ...

class GetMemberRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMemberResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _auth_pb2.Member
    def __init__(self, member: _Optional[_Union[_auth_pb2.Member, _Mapping]] = ...) -> None: ...

class ExchangeSessionRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class ExchangeSessionResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _auth_pb2.Member
    def __init__(self, member: _Optional[_Union[_auth_pb2.Member, _Mapping]] = ...) -> None: ...

class GetOrganizationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _auth_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_auth_pb2.Organization, _Mapping]] = ...) -> None: ...

class GetMemberInOrgByIdRequest(_message.Message):
    __slots__ = ("member_id", "org_id")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    org_id: str
    def __init__(self, member_id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetMemberInOrgByIdResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _auth_pb2.Member
    def __init__(self, member: _Optional[_Union[_auth_pb2.Member, _Mapping]] = ...) -> None: ...

class GetOIDCConfigRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class GetOIDCConfigResponse(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _auth_pb2.OIDCConfig
    def __init__(self, config: _Optional[_Union[_auth_pb2.OIDCConfig, _Mapping]] = ...) -> None: ...

class SaveOIDCConfigRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _auth_pb2.OIDCConfig
    def __init__(self, config: _Optional[_Union[_auth_pb2.OIDCConfig, _Mapping]] = ...) -> None: ...

class SaveOIDCConfigResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class CheckDomainForOIDCRequest(_message.Message):
    __slots__ = ("email_domain",)
    EMAIL_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    email_domain: str
    def __init__(self, email_domain: _Optional[str] = ...) -> None: ...

class CheckDomainForOIDCResponse(_message.Message):
    __slots__ = ("use_oidc", "organization_id")
    USE_OIDC_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    use_oidc: bool
    organization_id: str
    def __init__(self, use_oidc: bool = ..., organization_id: _Optional[str] = ...) -> None: ...

class GetGoogleOAuthUrlRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetGoogleOAuthUrlResponse(_message.Message):
    __slots__ = ("auth_url",)
    AUTH_URL_FIELD_NUMBER: _ClassVar[int]
    auth_url: str
    def __init__(self, auth_url: _Optional[str] = ...) -> None: ...

class HandleGoogleOAuthCallbackRequest(_message.Message):
    __slots__ = ("code", "state")
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    code: str
    state: str
    def __init__(self, code: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class HandleGoogleOAuthCallbackResponse(_message.Message):
    __slots__ = ("success", "intermediary_token", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIARY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    intermediary_token: str
    error: str
    def __init__(self, success: bool = ..., intermediary_token: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class UpdateOrgThemeRequest(_message.Message):
    __slots__ = ("org_id", "theme")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    THEME_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    theme: _auth_pb2.Theme
    def __init__(self, org_id: _Optional[str] = ..., theme: _Optional[_Union[_auth_pb2.Theme, _Mapping]] = ...) -> None: ...

class UpdateOrgThemeResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _auth_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_auth_pb2.Organization, _Mapping]] = ...) -> None: ...

class UpdateOrgToolRestrictionsRequest(_message.Message):
    __slots__ = ("org_id", "tool_restrictions")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    tool_restrictions: _paradigm_params_pb2.ParadigmParams
    def __init__(self, org_id: _Optional[str] = ..., tool_restrictions: _Optional[_Union[_paradigm_params_pb2.ParadigmParams, _Mapping]] = ...) -> None: ...

class UpdateOrgToolRestrictionsResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _auth_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_auth_pb2.Organization, _Mapping]] = ...) -> None: ...

class CreateLogoUploadPresignUrlRequest(_message.Message):
    __slots__ = ("org_id", "file_name")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    file_name: str
    def __init__(self, org_id: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...

class CreateLogoUploadPresignUrlResponse(_message.Message):
    __slots__ = ("upload_id", "presign_url")
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PRESIGN_URL_FIELD_NUMBER: _ClassVar[int]
    upload_id: str
    presign_url: str
    def __init__(self, upload_id: _Optional[str] = ..., presign_url: _Optional[str] = ...) -> None: ...

class ProcessLogoUploadPresignUrlRequest(_message.Message):
    __slots__ = ("org_id", "upload_id", "update_theme", "update_org_logo")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATE_THEME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ORG_LOGO_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    upload_id: str
    update_theme: bool
    update_org_logo: bool
    def __init__(self, org_id: _Optional[str] = ..., upload_id: _Optional[str] = ..., update_theme: bool = ..., update_org_logo: bool = ...) -> None: ...

class ProcessLogoUploadPresignUrlResponse(_message.Message):
    __slots__ = ("logo_url", "organization")
    LOGO_URL_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    logo_url: str
    organization: _auth_pb2.Organization
    def __init__(self, logo_url: _Optional[str] = ..., organization: _Optional[_Union[_auth_pb2.Organization, _Mapping]] = ...) -> None: ...

class UploadMemberImageRequest(_message.Message):
    __slots__ = ("member_id", "image_data", "file_name")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    image_data: bytes
    file_name: str
    def __init__(self, member_id: _Optional[str] = ..., image_data: _Optional[bytes] = ..., file_name: _Optional[str] = ...) -> None: ...

class UploadMemberImageResponse(_message.Message):
    __slots__ = ("image_url",)
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    def __init__(self, image_url: _Optional[str] = ...) -> None: ...

class GenerateMagicLinkForUserRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class GenerateMagicLinkForUserResponse(_message.Message):
    __slots__ = ("magic_link",)
    MAGIC_LINK_FIELD_NUMBER: _ClassVar[int]
    magic_link: str
    def __init__(self, magic_link: _Optional[str] = ...) -> None: ...

class CreateDemoAccountRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateDemoAccountResponse(_message.Message):
    __slots__ = ("long_term_access_token", "organization_id", "organization_name")
    LONG_TERM_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    long_term_access_token: str
    organization_id: str
    organization_name: str
    def __init__(self, long_term_access_token: _Optional[str] = ..., organization_id: _Optional[str] = ..., organization_name: _Optional[str] = ...) -> None: ...

class GetConsoleAuthTokenRequest(_message.Message):
    __slots__ = ("debug_level",)
    DEBUG_LEVEL_FIELD_NUMBER: _ClassVar[int]
    debug_level: int
    def __init__(self, debug_level: _Optional[int] = ...) -> None: ...

class GetConsoleAuthTokenResponse(_message.Message):
    __slots__ = ("intermediary_token", "console_url")
    INTERMEDIARY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_URL_FIELD_NUMBER: _ClassVar[int]
    intermediary_token: str
    console_url: str
    def __init__(self, intermediary_token: _Optional[str] = ..., console_url: _Optional[str] = ...) -> None: ...
