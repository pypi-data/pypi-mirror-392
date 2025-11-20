from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextPrompt(_message.Message):
    __slots__ = ("id", "name", "prompt", "is_org", "active", "assigned_roles", "assigned_datasets", "assigned_connectors", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IS_ORG_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_ROLES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_DATASETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    prompt: str
    is_org: bool
    active: bool
    assigned_roles: _containers.RepeatedScalarFieldContainer[str]
    assigned_datasets: _containers.RepeatedScalarFieldContainer[str]
    assigned_connectors: _containers.RepeatedScalarFieldContainer[int]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., prompt: _Optional[str] = ..., is_org: bool = ..., active: bool = ..., assigned_roles: _Optional[_Iterable[str]] = ..., assigned_datasets: _Optional[_Iterable[str]] = ..., assigned_connectors: _Optional[_Iterable[int]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateContextPromptRequest(_message.Message):
    __slots__ = ("name", "prompt", "is_org", "initial_role_ids", "initial_datasets", "initial_connectors")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IS_ORG_FIELD_NUMBER: _ClassVar[int]
    INITIAL_ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_DATASETS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    name: str
    prompt: str
    is_org: bool
    initial_role_ids: _containers.RepeatedScalarFieldContainer[str]
    initial_datasets: _containers.RepeatedScalarFieldContainer[str]
    initial_connectors: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, name: _Optional[str] = ..., prompt: _Optional[str] = ..., is_org: bool = ..., initial_role_ids: _Optional[_Iterable[str]] = ..., initial_datasets: _Optional[_Iterable[str]] = ..., initial_connectors: _Optional[_Iterable[int]] = ...) -> None: ...

class CreateContextPromptResponse(_message.Message):
    __slots__ = ("success", "error", "context_prompt")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PROMPT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    context_prompt: ContextPrompt
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., context_prompt: _Optional[_Union[ContextPrompt, _Mapping]] = ...) -> None: ...

class UpdateContextPromptRequest(_message.Message):
    __slots__ = ("id", "name", "prompt", "is_org")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IS_ORG_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    prompt: str
    is_org: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., prompt: _Optional[str] = ..., is_org: bool = ...) -> None: ...

class UpdateContextPromptResponse(_message.Message):
    __slots__ = ("success", "error", "context_prompt")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PROMPT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    context_prompt: ContextPrompt
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., context_prompt: _Optional[_Union[ContextPrompt, _Mapping]] = ...) -> None: ...

class DeleteContextPromptRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteContextPromptResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class ListAllOrgContextPromptsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAllOrgContextPromptsResponse(_message.Message):
    __slots__ = ("context_prompts",)
    CONTEXT_PROMPTS_FIELD_NUMBER: _ClassVar[int]
    context_prompts: _containers.RepeatedCompositeFieldContainer[ContextPrompt]
    def __init__(self, context_prompts: _Optional[_Iterable[_Union[ContextPrompt, _Mapping]]] = ...) -> None: ...

class AssignContextPromptToRolesRequest(_message.Message):
    __slots__ = ("context_prompt_id", "role_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    role_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, context_prompt_id: _Optional[str] = ..., role_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AssignContextPromptToRolesResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class RemoveContextPromptFromRolesRequest(_message.Message):
    __slots__ = ("context_prompt_id", "role_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    role_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, context_prompt_id: _Optional[str] = ..., role_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveContextPromptFromRolesResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetContextPromptsByRoleRequest(_message.Message):
    __slots__ = ("role_id",)
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    def __init__(self, role_id: _Optional[str] = ...) -> None: ...

class GetContextPromptsByRoleResponse(_message.Message):
    __slots__ = ("context_prompts",)
    CONTEXT_PROMPTS_FIELD_NUMBER: _ClassVar[int]
    context_prompts: _containers.RepeatedCompositeFieldContainer[ContextPrompt]
    def __init__(self, context_prompts: _Optional[_Iterable[_Union[ContextPrompt, _Mapping]]] = ...) -> None: ...

class AssignDatasetsToContextPromptRequest(_message.Message):
    __slots__ = ("context_prompt_id", "dataset_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, context_prompt_id: _Optional[str] = ..., dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AssignDatasetsToContextPromptResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class RemoveDatasetsFromContextPromptRequest(_message.Message):
    __slots__ = ("context_prompt_id", "dataset_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, context_prompt_id: _Optional[str] = ..., dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveDatasetsFromContextPromptResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetContextPromptsByDatasetRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class GetContextPromptsByDatasetResponse(_message.Message):
    __slots__ = ("context_prompts",)
    CONTEXT_PROMPTS_FIELD_NUMBER: _ClassVar[int]
    context_prompts: _containers.RepeatedCompositeFieldContainer[ContextPrompt]
    def __init__(self, context_prompts: _Optional[_Iterable[_Union[ContextPrompt, _Mapping]]] = ...) -> None: ...

class AssignContextPromptToConnectorsRequest(_message.Message):
    __slots__ = ("context_prompt_id", "connector_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, context_prompt_id: _Optional[str] = ..., connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class AssignContextPromptToConnectorsResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class RemoveContextPromptFromConnectorsRequest(_message.Message):
    __slots__ = ("context_prompt_id", "connector_ids")
    CONTEXT_PROMPT_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_IDS_FIELD_NUMBER: _ClassVar[int]
    context_prompt_id: str
    connector_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, context_prompt_id: _Optional[str] = ..., connector_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class RemoveContextPromptFromConnectorsResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetContextPromptsByConnectorRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetContextPromptsByConnectorResponse(_message.Message):
    __slots__ = ("context_prompts",)
    CONTEXT_PROMPTS_FIELD_NUMBER: _ClassVar[int]
    context_prompts: _containers.RepeatedCompositeFieldContainer[ContextPrompt]
    def __init__(self, context_prompts: _Optional[_Iterable[_Union[ContextPrompt, _Mapping]]] = ...) -> None: ...

class ToggleContextPromptActiveRequest(_message.Message):
    __slots__ = ("id", "active")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    active: bool
    def __init__(self, id: _Optional[str] = ..., active: bool = ...) -> None: ...

class ToggleContextPromptActiveResponse(_message.Message):
    __slots__ = ("success", "error", "context_prompt")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PROMPT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    context_prompt: ContextPrompt
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., context_prompt: _Optional[_Union[ContextPrompt, _Mapping]] = ...) -> None: ...
