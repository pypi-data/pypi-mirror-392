from public import connector_pb2 as _connector_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListConnectorsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListConnectorsResponse(_message.Message):
    __slots__ = ("connectors",)
    CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    connectors: _containers.RepeatedCompositeFieldContainer[_connector_pb2.Connector]
    def __init__(self, connectors: _Optional[_Iterable[_Union[_connector_pb2.Connector, _Mapping]]] = ...) -> None: ...
