from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OntologyAttributeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ONTOLOGY_ATTRIBUTE_TYPE_UNSPECIFIED: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_STRING: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_NUMBER: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_INT: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_BOOLEAN: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_DATE: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_DATE_TIME: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_TIMESTAMP: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_ENUM: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_JSON: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_JSONB: _ClassVar[OntologyAttributeType]
    ONTOLOGY_ATTRIBUTE_TYPE_UUID: _ClassVar[OntologyAttributeType]

class RelationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RELATION_TYPE_UNSPECIFIED: _ClassVar[RelationType]
    RELATION_TYPE_ONE_TO_MANY: _ClassVar[RelationType]
    RELATION_TYPE_MANY_TO_ONE: _ClassVar[RelationType]
    RELATION_TYPE_ONE_TO_ONE: _ClassVar[RelationType]
    RELATION_TYPE_MANY_TO_MANY: _ClassVar[RelationType]

class MetricAggregation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METRIC_AGGREGATION_SUM: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_COUNT: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_AVG: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_MIN: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_MAX: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_COUNT_DISTINCT: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_MEDIAN: _ClassVar[MetricAggregation]
    METRIC_AGGREGATION_ARRAY_AGG: _ClassVar[MetricAggregation]
ONTOLOGY_ATTRIBUTE_TYPE_UNSPECIFIED: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_STRING: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_NUMBER: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_INT: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_BOOLEAN: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_DATE: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_DATE_TIME: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_TIMESTAMP: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_ENUM: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_JSON: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_JSONB: OntologyAttributeType
ONTOLOGY_ATTRIBUTE_TYPE_UUID: OntologyAttributeType
RELATION_TYPE_UNSPECIFIED: RelationType
RELATION_TYPE_ONE_TO_MANY: RelationType
RELATION_TYPE_MANY_TO_ONE: RelationType
RELATION_TYPE_ONE_TO_ONE: RelationType
RELATION_TYPE_MANY_TO_MANY: RelationType
METRIC_AGGREGATION_SUM: MetricAggregation
METRIC_AGGREGATION_COUNT: MetricAggregation
METRIC_AGGREGATION_AVG: MetricAggregation
METRIC_AGGREGATION_MIN: MetricAggregation
METRIC_AGGREGATION_MAX: MetricAggregation
METRIC_AGGREGATION_COUNT_DISTINCT: MetricAggregation
METRIC_AGGREGATION_MEDIAN: MetricAggregation
METRIC_AGGREGATION_ARRAY_AGG: MetricAggregation

class TableName(_message.Message):
    __slots__ = ("schema", "table", "database")
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    schema: str
    table: str
    database: str
    def __init__(self, schema: _Optional[str] = ..., table: _Optional[str] = ..., database: _Optional[str] = ...) -> None: ...

class AttributeRef(_message.Message):
    __slots__ = ("attribute_ref",)
    ATTRIBUTE_REF_FIELD_NUMBER: _ClassVar[int]
    attribute_ref: str
    def __init__(self, attribute_ref: _Optional[str] = ...) -> None: ...

class ObjectRef(_message.Message):
    __slots__ = ("object_ref",)
    OBJECT_REF_FIELD_NUMBER: _ClassVar[int]
    object_ref: str
    def __init__(self, object_ref: _Optional[str] = ...) -> None: ...

class GraphPosition(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class GraphProperties(_message.Message):
    __slots__ = ("position", "icon", "color")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    position: GraphPosition
    icon: str
    color: str
    def __init__(self, position: _Optional[_Union[GraphPosition, _Mapping]] = ..., icon: _Optional[str] = ..., color: _Optional[str] = ...) -> None: ...

class AttributeData(_message.Message):
    __slots__ = ("unlinked", "linked")
    UNLINKED_FIELD_NUMBER: _ClassVar[int]
    LINKED_FIELD_NUMBER: _ClassVar[int]
    unlinked: UnlinkedAttributeData
    linked: LinkedAttributeData
    def __init__(self, unlinked: _Optional[_Union[UnlinkedAttributeData, _Mapping]] = ..., linked: _Optional[_Union[LinkedAttributeData, _Mapping]] = ...) -> None: ...

class UnlinkedAttributeData(_message.Message):
    __slots__ = ("column_name",)
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    def __init__(self, column_name: _Optional[str] = ...) -> None: ...

class LinkedAttributeData(_message.Message):
    __slots__ = ("relation_id", "target_attribute_id")
    RELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    relation_id: str
    target_attribute_id: str
    def __init__(self, relation_id: _Optional[str] = ..., target_attribute_id: _Optional[str] = ...) -> None: ...

class IntermediateJoin(_message.Message):
    __slots__ = ("table_name", "left_column", "right_column")
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LEFT_COLUMN_FIELD_NUMBER: _ClassVar[int]
    RIGHT_COLUMN_FIELD_NUMBER: _ClassVar[int]
    table_name: str
    left_column: str
    right_column: str
    def __init__(self, table_name: _Optional[str] = ..., left_column: _Optional[str] = ..., right_column: _Optional[str] = ...) -> None: ...

class OntologyObject(_message.Message):
    __slots__ = ("id", "name", "description", "backing_table", "backing_query", "primary_key_attribute", "title_attribute", "interesting_attributes", "graph_properties", "access_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    BACKING_TABLE_FIELD_NUMBER: _ClassVar[int]
    BACKING_QUERY_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_KEY_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    TITLE_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    INTERESTING_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    GRAPH_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    backing_table: TableName
    backing_query: str
    primary_key_attribute: AttributeRef
    title_attribute: AttributeRef
    interesting_attributes: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    graph_properties: GraphProperties
    access_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., backing_table: _Optional[_Union[TableName, _Mapping]] = ..., backing_query: _Optional[str] = ..., primary_key_attribute: _Optional[_Union[AttributeRef, _Mapping]] = ..., title_attribute: _Optional[_Union[AttributeRef, _Mapping]] = ..., interesting_attributes: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., graph_properties: _Optional[_Union[GraphProperties, _Mapping]] = ..., access_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OntologyAttribute(_message.Message):
    __slots__ = ("id", "object_id", "name", "description", "type", "is_inherent", "is_measure", "is_dimension", "data", "access_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_INHERENT_FIELD_NUMBER: _ClassVar[int]
    IS_MEASURE_FIELD_NUMBER: _ClassVar[int]
    IS_DIMENSION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_id: str
    name: str
    description: str
    type: OntologyAttributeType
    is_inherent: bool
    is_measure: bool
    is_dimension: bool
    data: AttributeData
    access_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., object_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[OntologyAttributeType, str]] = ..., is_inherent: bool = ..., is_measure: bool = ..., is_dimension: bool = ..., data: _Optional[_Union[AttributeData, _Mapping]] = ..., access_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OntologyMetric(_message.Message):
    __slots__ = ("id", "name", "description", "object_id", "attribute", "formula", "time_dimension", "breakdowns", "aggregation", "lod", "access_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    TIME_DIMENSION_FIELD_NUMBER: _ClassVar[int]
    BREAKDOWNS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    LOD_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    object_id: str
    attribute: AttributeRef
    formula: str
    time_dimension: AttributeRef
    breakdowns: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    aggregation: MetricAggregation
    lod: _containers.RepeatedScalarFieldContainer[str]
    access_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., object_id: _Optional[str] = ..., attribute: _Optional[_Union[AttributeRef, _Mapping]] = ..., formula: _Optional[str] = ..., time_dimension: _Optional[_Union[AttributeRef, _Mapping]] = ..., breakdowns: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., aggregation: _Optional[_Union[MetricAggregation, str]] = ..., lod: _Optional[_Iterable[str]] = ..., access_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OntologyRelation(_message.Message):
    __slots__ = ("id", "name", "description", "type", "object_a", "object_b", "join_key_a", "join_key_b", "intermediate_join", "join_formula")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_A_FIELD_NUMBER: _ClassVar[int]
    OBJECT_B_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEY_A_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEY_B_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_JOIN_FIELD_NUMBER: _ClassVar[int]
    JOIN_FORMULA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    type: RelationType
    object_a: ObjectRef
    object_b: ObjectRef
    join_key_a: AttributeRef
    join_key_b: AttributeRef
    intermediate_join: IntermediateJoin
    join_formula: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[RelationType, str]] = ..., object_a: _Optional[_Union[ObjectRef, _Mapping]] = ..., object_b: _Optional[_Union[ObjectRef, _Mapping]] = ..., join_key_a: _Optional[_Union[AttributeRef, _Mapping]] = ..., join_key_b: _Optional[_Union[AttributeRef, _Mapping]] = ..., intermediate_join: _Optional[_Union[IntermediateJoin, _Mapping]] = ..., join_formula: _Optional[str] = ...) -> None: ...

class Ontology(_message.Message):
    __slots__ = ("id", "name", "description", "connector_id", "connector_name", "is_example", "objects", "attributes", "metrics", "relations", "measures", "dimensions", "temporary_core_fact_object", "filter_rules")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    MEASURES_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_CORE_FACT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    FILTER_RULES_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    description: str
    connector_id: int
    connector_name: str
    is_example: bool
    objects: _containers.RepeatedCompositeFieldContainer[OntologyObject]
    attributes: _containers.RepeatedCompositeFieldContainer[OntologyAttribute]
    metrics: _containers.RepeatedCompositeFieldContainer[OntologyMetric]
    relations: _containers.RepeatedCompositeFieldContainer[OntologyRelation]
    measures: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    dimensions: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    temporary_core_fact_object: ObjectRef
    filter_rules: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., connector_id: _Optional[int] = ..., connector_name: _Optional[str] = ..., is_example: bool = ..., objects: _Optional[_Iterable[_Union[OntologyObject, _Mapping]]] = ..., attributes: _Optional[_Iterable[_Union[OntologyAttribute, _Mapping]]] = ..., metrics: _Optional[_Iterable[_Union[OntologyMetric, _Mapping]]] = ..., relations: _Optional[_Iterable[_Union[OntologyRelation, _Mapping]]] = ..., measures: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., dimensions: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., temporary_core_fact_object: _Optional[_Union[ObjectRef, _Mapping]] = ..., filter_rules: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ...) -> None: ...

class CreateOntologyRequest(_message.Message):
    __slots__ = ("connector_id", "name", "description", "objects", "attributes", "metrics", "relations", "measures", "dimensions", "temporary_core_fact_object")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    MEASURES_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_CORE_FACT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    name: str
    description: str
    objects: _containers.RepeatedCompositeFieldContainer[OntologyObject]
    attributes: _containers.RepeatedCompositeFieldContainer[OntologyAttribute]
    metrics: _containers.RepeatedCompositeFieldContainer[OntologyMetric]
    relations: _containers.RepeatedCompositeFieldContainer[OntologyRelation]
    measures: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    dimensions: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    temporary_core_fact_object: ObjectRef
    def __init__(self, connector_id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., objects: _Optional[_Iterable[_Union[OntologyObject, _Mapping]]] = ..., attributes: _Optional[_Iterable[_Union[OntologyAttribute, _Mapping]]] = ..., metrics: _Optional[_Iterable[_Union[OntologyMetric, _Mapping]]] = ..., relations: _Optional[_Iterable[_Union[OntologyRelation, _Mapping]]] = ..., measures: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., dimensions: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., temporary_core_fact_object: _Optional[_Union[ObjectRef, _Mapping]] = ...) -> None: ...

class CreateOntologyResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class GetOntologyRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetOntologyResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class GetOntologyByIdRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class GetOntologyByIdResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class GetOntologiesRequest(_message.Message):
    __slots__ = ("include_examples",)
    INCLUDE_EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    include_examples: bool
    def __init__(self, include_examples: bool = ...) -> None: ...

class GetOntologiesResponse(_message.Message):
    __slots__ = ("ontologies",)
    ONTOLOGIES_FIELD_NUMBER: _ClassVar[int]
    ontologies: _containers.RepeatedCompositeFieldContainer[Ontology]
    def __init__(self, ontologies: _Optional[_Iterable[_Union[Ontology, _Mapping]]] = ...) -> None: ...

class UpdateOntologyNameRequest(_message.Message):
    __slots__ = ("ontology_id", "name")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    name: str
    def __init__(self, ontology_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateOntologyNameResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class UpdateOntologyDescriptionRequest(_message.Message):
    __slots__ = ("ontology_id", "description")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    description: str
    def __init__(self, ontology_id: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateOntologyDescriptionResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class DeleteOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class DeleteOntologyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CreateObjectRequest(_message.Message):
    __slots__ = ("ontology_id", "object", "attributes", "temporary_core_fact_object")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_CORE_FACT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    object: OntologyObject
    attributes: _containers.RepeatedCompositeFieldContainer[OntologyAttribute]
    temporary_core_fact_object: ObjectRef
    def __init__(self, ontology_id: _Optional[int] = ..., object: _Optional[_Union[OntologyObject, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[OntologyAttribute, _Mapping]]] = ..., temporary_core_fact_object: _Optional[_Union[ObjectRef, _Mapping]] = ...) -> None: ...

class CreateObjectResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class UpdateObjectRequest(_message.Message):
    __slots__ = ("ontology_id", "object_id", "object", "attributes", "measures", "dimensions", "temporary_core_fact_object")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    MEASURES_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_CORE_FACT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    object_id: str
    object: OntologyObject
    attributes: _containers.RepeatedCompositeFieldContainer[OntologyAttribute]
    measures: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    dimensions: _containers.RepeatedCompositeFieldContainer[AttributeRef]
    temporary_core_fact_object: ObjectRef
    def __init__(self, ontology_id: _Optional[int] = ..., object_id: _Optional[str] = ..., object: _Optional[_Union[OntologyObject, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[OntologyAttribute, _Mapping]]] = ..., measures: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., dimensions: _Optional[_Iterable[_Union[AttributeRef, _Mapping]]] = ..., temporary_core_fact_object: _Optional[_Union[ObjectRef, _Mapping]] = ...) -> None: ...

class UpdateObjectResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class DeleteObjectRequest(_message.Message):
    __slots__ = ("ontology_id", "object_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    object_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., object_id: _Optional[str] = ...) -> None: ...

class DeleteObjectResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class GetObjectByIdRequest(_message.Message):
    __slots__ = ("object_id",)
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    def __init__(self, object_id: _Optional[str] = ...) -> None: ...

class GetObjectByIdResponse(_message.Message):
    __slots__ = ("object", "ontology", "attributes")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    object: OntologyObject
    ontology: Ontology
    attributes: _containers.RepeatedCompositeFieldContainer[OntologyAttribute]
    def __init__(self, object: _Optional[_Union[OntologyObject, _Mapping]] = ..., ontology: _Optional[_Union[Ontology, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[OntologyAttribute, _Mapping]]] = ...) -> None: ...

class UpdateObjectGraphPropertiesRequest(_message.Message):
    __slots__ = ("ontology_id", "updates")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    updates: _containers.RepeatedCompositeFieldContainer[ObjectGraphPropertiesUpdate]
    def __init__(self, ontology_id: _Optional[int] = ..., updates: _Optional[_Iterable[_Union[ObjectGraphPropertiesUpdate, _Mapping]]] = ...) -> None: ...

class ObjectGraphPropertiesUpdate(_message.Message):
    __slots__ = ("object_id", "graph_properties")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    graph_properties: GraphProperties
    def __init__(self, object_id: _Optional[str] = ..., graph_properties: _Optional[_Union[GraphProperties, _Mapping]] = ...) -> None: ...

class UpdateObjectGraphPropertiesResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CreateAttributeRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute: OntologyAttribute
    def __init__(self, ontology_id: _Optional[int] = ..., attribute: _Optional[_Union[OntologyAttribute, _Mapping]] = ...) -> None: ...

class CreateAttributeResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class UpdateAttributeRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id", "attribute")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    attribute: OntologyAttribute
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ..., attribute: _Optional[_Union[OntologyAttribute, _Mapping]] = ...) -> None: ...

class UpdateAttributeResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class DeleteAttributeRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ...) -> None: ...

class DeleteAttributeResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class GetAttributeByIdRequest(_message.Message):
    __slots__ = ("attribute_id",)
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    attribute_id: str
    def __init__(self, attribute_id: _Optional[str] = ...) -> None: ...

class GetAttributeByIdResponse(_message.Message):
    __slots__ = ("attribute",)
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    attribute: OntologyAttribute
    def __init__(self, attribute: _Optional[_Union[OntologyAttribute, _Mapping]] = ...) -> None: ...

class CreateMetricRequest(_message.Message):
    __slots__ = ("ontology_id", "metrics")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    metrics: _containers.RepeatedCompositeFieldContainer[OntologyMetric]
    def __init__(self, ontology_id: _Optional[int] = ..., metrics: _Optional[_Iterable[_Union[OntologyMetric, _Mapping]]] = ...) -> None: ...

class CreateMetricResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class UpdateMetricRequest(_message.Message):
    __slots__ = ("ontology_id", "metric_id", "metric")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    metric_id: str
    metric: OntologyMetric
    def __init__(self, ontology_id: _Optional[int] = ..., metric_id: _Optional[str] = ..., metric: _Optional[_Union[OntologyMetric, _Mapping]] = ...) -> None: ...

class UpdateMetricResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class DeleteMetricRequest(_message.Message):
    __slots__ = ("ontology_id", "metric_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    metric_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., metric_id: _Optional[str] = ...) -> None: ...

class DeleteMetricResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class CreateRelationRequest(_message.Message):
    __slots__ = ("ontology_id", "relation")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    relation: OntologyRelation
    def __init__(self, ontology_id: _Optional[int] = ..., relation: _Optional[_Union[OntologyRelation, _Mapping]] = ...) -> None: ...

class CreateRelationResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class UpdateRelationRequest(_message.Message):
    __slots__ = ("ontology_id", "relation_id", "relation")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    relation_id: str
    relation: OntologyRelation
    def __init__(self, ontology_id: _Optional[int] = ..., relation_id: _Optional[str] = ..., relation: _Optional[_Union[OntologyRelation, _Mapping]] = ...) -> None: ...

class UpdateRelationResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class DeleteRelationRequest(_message.Message):
    __slots__ = ("ontology_id", "relation_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    relation_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., relation_id: _Optional[str] = ...) -> None: ...

class DeleteRelationResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: Ontology
    def __init__(self, ontology: _Optional[_Union[Ontology, _Mapping]] = ...) -> None: ...

class CreateFilterRuleRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ...) -> None: ...

class CreateFilterRuleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DeleteFilterRuleRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ...) -> None: ...

class DeleteFilterRuleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetFilterRuleRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ...) -> None: ...

class GetFilterRuleResponse(_message.Message):
    __slots__ = ("has_rule",)
    HAS_RULE_FIELD_NUMBER: _ClassVar[int]
    has_rule: bool
    def __init__(self, has_rule: bool = ...) -> None: ...

class UpdateObjectAccessTimeRequest(_message.Message):
    __slots__ = ("ontology_id", "object_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    object_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., object_id: _Optional[str] = ...) -> None: ...

class UpdateObjectAccessTimeResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UpdateAttributeAccessTimeRequest(_message.Message):
    __slots__ = ("ontology_id", "attribute_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    attribute_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., attribute_id: _Optional[str] = ...) -> None: ...

class UpdateAttributeAccessTimeResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UpdateMetricAccessTimeRequest(_message.Message):
    __slots__ = ("ontology_id", "metric_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    metric_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., metric_id: _Optional[str] = ...) -> None: ...

class UpdateMetricAccessTimeResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class SaveMetricQueryRequest(_message.Message):
    __slots__ = ("ontology_id", "name", "query", "query_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    name: str
    query: _struct_pb2.Struct
    query_id: str
    def __init__(self, ontology_id: _Optional[int] = ..., name: _Optional[str] = ..., query: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., query_id: _Optional[str] = ...) -> None: ...

class SaveMetricQueryResponse(_message.Message):
    __slots__ = ("query_id",)
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    query_id: str
    def __init__(self, query_id: _Optional[str] = ...) -> None: ...

class GetMetricQueryRequest(_message.Message):
    __slots__ = ("query_id",)
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    query_id: str
    def __init__(self, query_id: _Optional[str] = ...) -> None: ...

class GetMetricQueryResponse(_message.Message):
    __slots__ = ("id", "name", "query", "ontology_id", "created_at", "updated_at", "access_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    query: _struct_pb2.Struct
    ontology_id: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    access_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., query: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., ontology_id: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., access_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetMetricQueriesRequest(_message.Message):
    __slots__ = ("query_ids", "verify_ownership")
    QUERY_IDS_FIELD_NUMBER: _ClassVar[int]
    VERIFY_OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    query_ids: _containers.RepeatedScalarFieldContainer[str]
    verify_ownership: bool
    def __init__(self, query_ids: _Optional[_Iterable[str]] = ..., verify_ownership: bool = ...) -> None: ...

class GetMetricQueriesResponse(_message.Message):
    __slots__ = ("queries",)
    QUERIES_FIELD_NUMBER: _ClassVar[int]
    queries: _containers.RepeatedCompositeFieldContainer[GetMetricQueryResponse]
    def __init__(self, queries: _Optional[_Iterable[_Union[GetMetricQueryResponse, _Mapping]]] = ...) -> None: ...

class DeleteMetricQueryRequest(_message.Message):
    __slots__ = ("query_id",)
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    query_id: str
    def __init__(self, query_id: _Optional[str] = ...) -> None: ...

class DeleteMetricQueryResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CreateObjectViewSettingsRequest(_message.Message):
    __slots__ = ("object_id", "settings")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    settings: _struct_pb2.Struct
    def __init__(self, object_id: _Optional[str] = ..., settings: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateObjectViewSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _struct_pb2.Struct
    def __init__(self, settings: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetObjectViewSettingsRequest(_message.Message):
    __slots__ = ("object_id",)
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    def __init__(self, object_id: _Optional[str] = ...) -> None: ...

class GetObjectViewSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _struct_pb2.Struct
    def __init__(self, settings: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateObjectViewSettingsRequest(_message.Message):
    __slots__ = ("object_id", "settings")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    settings: _struct_pb2.Struct
    def __init__(self, object_id: _Optional[str] = ..., settings: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateObjectViewSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _struct_pb2.Struct
    def __init__(self, settings: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class TestResult(_message.Message):
    __slots__ = ("name", "status", "message")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[TestResult.Status]
        STATUS_SUCCESS: _ClassVar[TestResult.Status]
        STATUS_ERROR: _ClassVar[TestResult.Status]
        STATUS_SKIPPED: _ClassVar[TestResult.Status]
    STATUS_UNSPECIFIED: TestResult.Status
    STATUS_SUCCESS: TestResult.Status
    STATUS_ERROR: TestResult.Status
    STATUS_SKIPPED: TestResult.Status
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    status: TestResult.Status
    message: str
    def __init__(self, name: _Optional[str] = ..., status: _Optional[_Union[TestResult.Status, str]] = ..., message: _Optional[str] = ...) -> None: ...

class TestOntologyObjectsRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class TestOntologyObjectsResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[TestResult]
    def __init__(self, results: _Optional[_Iterable[_Union[TestResult, _Mapping]]] = ...) -> None: ...

class TestOntologyAttributesRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class TestOntologyAttributesResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[TestResult]
    def __init__(self, results: _Optional[_Iterable[_Union[TestResult, _Mapping]]] = ...) -> None: ...

class ExportOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class ExportOntologyResponse(_message.Message):
    __slots__ = ("ontology",)
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    ontology: _struct_pb2.Struct
    def __init__(self, ontology: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ImportOntologyRequest(_message.Message):
    __slots__ = ("ontology_id", "ontology", "connector_id")
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ONTOLOGY_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    ontology: _struct_pb2.Struct
    connector_id: int
    def __init__(self, ontology_id: _Optional[int] = ..., ontology: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., connector_id: _Optional[int] = ...) -> None: ...

class ImportOntologyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ClearOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class ClearOntologyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RegisterExampleOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class RegisterExampleOntologyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UnregisterExampleOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class UnregisterExampleOntologyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GenerateSamplesForOntologyRequest(_message.Message):
    __slots__ = ("ontology_id",)
    ONTOLOGY_ID_FIELD_NUMBER: _ClassVar[int]
    ontology_id: int
    def __init__(self, ontology_id: _Optional[int] = ...) -> None: ...

class GenerateSamplesForOntologyResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetTableRowCountRequest(_message.Message):
    __slots__ = ("object_id", "connector_id")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    connector_id: int
    def __init__(self, object_id: _Optional[str] = ..., connector_id: _Optional[int] = ...) -> None: ...

class GetTableRowCountResponse(_message.Message):
    __slots__ = ("row_count", "success")
    ROW_COUNT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    row_count: int
    success: bool
    def __init__(self, row_count: _Optional[int] = ..., success: bool = ...) -> None: ...
