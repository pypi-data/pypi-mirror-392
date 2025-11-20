from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageVariant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMAGE_VARIANT_CIRCULAR: _ClassVar[ImageVariant]
    IMAGE_VARIANT_ROUNDED: _ClassVar[ImageVariant]
    IMAGE_VARIANT_PILL: _ClassVar[ImageVariant]
    IMAGE_VARIANT_NONE: _ClassVar[ImageVariant]
IMAGE_VARIANT_CIRCULAR: ImageVariant
IMAGE_VARIANT_ROUNDED: ImageVariant
IMAGE_VARIANT_PILL: ImageVariant
IMAGE_VARIANT_NONE: ImageVariant

class HeroBlock(_message.Message):
    __slots__ = ("image_url", "image_alt")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ALT_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    image_alt: str
    def __init__(self, image_url: _Optional[str] = ..., image_alt: _Optional[str] = ...) -> None: ...

class TextBlock(_message.Message):
    __slots__ = ("heading", "content")
    HEADING_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    heading: str
    content: str
    def __init__(self, heading: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ImageBlock(_message.Message):
    __slots__ = ("image_url", "image_alt", "variant")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ALT_FIELD_NUMBER: _ClassVar[int]
    VARIANT_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    image_alt: str
    variant: ImageVariant
    def __init__(self, image_url: _Optional[str] = ..., image_alt: _Optional[str] = ..., variant: _Optional[_Union[ImageVariant, str]] = ...) -> None: ...

class ListBlock(_message.Message):
    __slots__ = ("heading", "items")
    HEADING_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    heading: str
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, heading: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ...) -> None: ...

class ImageTextBlock(_message.Message):
    __slots__ = ("image_url", "image_alt", "variant", "heading", "content")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ALT_FIELD_NUMBER: _ClassVar[int]
    VARIANT_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    image_alt: str
    variant: ImageVariant
    heading: str
    content: str
    def __init__(self, image_url: _Optional[str] = ..., image_alt: _Optional[str] = ..., variant: _Optional[_Union[ImageVariant, str]] = ..., heading: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class CardBlock(_message.Message):
    __slots__ = ("blocks",)
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    blocks: _containers.RepeatedCompositeFieldContainer[ReportBlock]
    def __init__(self, blocks: _Optional[_Iterable[_Union[ReportBlock, _Mapping]]] = ...) -> None: ...

class DividerBlock(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SpacerBlock(_message.Message):
    __slots__ = ("height",)
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    height: int
    def __init__(self, height: _Optional[int] = ...) -> None: ...

class ReportBlock(_message.Message):
    __slots__ = ("hero", "text", "image", "list", "image_text", "card", "divider", "spacer")
    HERO_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    IMAGE_TEXT_FIELD_NUMBER: _ClassVar[int]
    CARD_FIELD_NUMBER: _ClassVar[int]
    DIVIDER_FIELD_NUMBER: _ClassVar[int]
    SPACER_FIELD_NUMBER: _ClassVar[int]
    hero: HeroBlock
    text: TextBlock
    image: ImageBlock
    list: ListBlock
    image_text: ImageTextBlock
    card: CardBlock
    divider: DividerBlock
    spacer: SpacerBlock
    def __init__(self, hero: _Optional[_Union[HeroBlock, _Mapping]] = ..., text: _Optional[_Union[TextBlock, _Mapping]] = ..., image: _Optional[_Union[ImageBlock, _Mapping]] = ..., list: _Optional[_Union[ListBlock, _Mapping]] = ..., image_text: _Optional[_Union[ImageTextBlock, _Mapping]] = ..., card: _Optional[_Union[CardBlock, _Mapping]] = ..., divider: _Optional[_Union[DividerBlock, _Mapping]] = ..., spacer: _Optional[_Union[SpacerBlock, _Mapping]] = ...) -> None: ...
