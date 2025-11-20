from google.protobuf import timestamp_pb2 as _timestamp_pb2
from public import options_pb2 as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONNECTOR_TYPE_UNSPECIFIED: _ClassVar[ConnectorType]
    REDSHIFT: _ClassVar[ConnectorType]
    SNOWFLAKE: _ClassVar[ConnectorType]
    BIGQUERY: _ClassVar[ConnectorType]
    AZURE_SYNAPSE: _ClassVar[ConnectorType]
    AURORA: _ClassVar[ConnectorType]
    TABLEAU: _ClassVar[ConnectorType]
    DATABRICKS: _ClassVar[ConnectorType]
    SUPABASE: _ClassVar[ConnectorType]
    POSTGRES: _ClassVar[ConnectorType]
    MOTHERDUCK: _ClassVar[ConnectorType]
    CLICKHOUSE: _ClassVar[ConnectorType]
    MYSQL: _ClassVar[ConnectorType]
    ATHENA: _ClassVar[ConnectorType]
    GOOGLE_DRIVE: _ClassVar[ConnectorType]
    POWERBI: _ClassVar[ConnectorType]
    SQL_SERVER: _ClassVar[ConnectorType]

class ListingStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LISTING_STATUS_UNSPECIFIED: _ClassVar[ListingStatus]
    LISTING_STATUS_PENDING: _ClassVar[ListingStatus]
    LISTING_STATUS_IN_PROGRESS: _ClassVar[ListingStatus]
    LISTING_STATUS_COMPLETED: _ClassVar[ListingStatus]
    LISTING_STATUS_SYNCHRONIZED: _ClassVar[ListingStatus]
    LISTING_STATUS_FAILED: _ClassVar[ListingStatus]

class SyncStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SYNC_STATUS_UNSPECIFIED: _ClassVar[SyncStatus]
    SYNC_PENDING: _ClassVar[SyncStatus]
    SYNC_IN_PROGRESS: _ClassVar[SyncStatus]
    SYNC_COMPLETED: _ClassVar[SyncStatus]
    SYNC_FAILED: _ClassVar[SyncStatus]
CONNECTOR_TYPE_UNSPECIFIED: ConnectorType
REDSHIFT: ConnectorType
SNOWFLAKE: ConnectorType
BIGQUERY: ConnectorType
AZURE_SYNAPSE: ConnectorType
AURORA: ConnectorType
TABLEAU: ConnectorType
DATABRICKS: ConnectorType
SUPABASE: ConnectorType
POSTGRES: ConnectorType
MOTHERDUCK: ConnectorType
CLICKHOUSE: ConnectorType
MYSQL: ConnectorType
ATHENA: ConnectorType
GOOGLE_DRIVE: ConnectorType
POWERBI: ConnectorType
SQL_SERVER: ConnectorType
LISTING_STATUS_UNSPECIFIED: ListingStatus
LISTING_STATUS_PENDING: ListingStatus
LISTING_STATUS_IN_PROGRESS: ListingStatus
LISTING_STATUS_COMPLETED: ListingStatus
LISTING_STATUS_SYNCHRONIZED: ListingStatus
LISTING_STATUS_FAILED: ListingStatus
SYNC_STATUS_UNSPECIFIED: SyncStatus
SYNC_PENDING: SyncStatus
SYNC_IN_PROGRESS: SyncStatus
SYNC_COMPLETED: SyncStatus
SYNC_FAILED: SyncStatus

class ConnectorConfig(_message.Message):
    __slots__ = ("connector_type", "name", "redshift", "snowflake", "bigquery", "azure_synapse", "tableau", "aurora", "databricks", "motherduck", "clickhouse", "mysql", "athena", "google_drive", "powerbi", "postgres", "supabase", "sql_server")
    CONNECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REDSHIFT_FIELD_NUMBER: _ClassVar[int]
    SNOWFLAKE_FIELD_NUMBER: _ClassVar[int]
    BIGQUERY_FIELD_NUMBER: _ClassVar[int]
    AZURE_SYNAPSE_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_FIELD_NUMBER: _ClassVar[int]
    AURORA_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_FIELD_NUMBER: _ClassVar[int]
    MOTHERDUCK_FIELD_NUMBER: _ClassVar[int]
    CLICKHOUSE_FIELD_NUMBER: _ClassVar[int]
    MYSQL_FIELD_NUMBER: _ClassVar[int]
    ATHENA_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_FIELD_NUMBER: _ClassVar[int]
    POWERBI_FIELD_NUMBER: _ClassVar[int]
    POSTGRES_FIELD_NUMBER: _ClassVar[int]
    SUPABASE_FIELD_NUMBER: _ClassVar[int]
    SQL_SERVER_FIELD_NUMBER: _ClassVar[int]
    connector_type: ConnectorType
    name: str
    redshift: RedshiftMetadata
    snowflake: SnowflakeMetadata
    bigquery: BigQueryMetadata
    azure_synapse: AzureSynapseMetadata
    tableau: TableauMetadata
    aurora: AuroraMetadata
    databricks: DatabricksMetadata
    motherduck: MotherduckMetadata
    clickhouse: ClickHouseMetadata
    mysql: MYSQLMetadata
    athena: AthenaMetadata
    google_drive: GoogleDriveMetadata
    powerbi: PowerBIMetadata
    postgres: PostgresMetadata
    supabase: SupabaseMetadata
    sql_server: SQLServerMetadata
    def __init__(self, connector_type: _Optional[_Union[ConnectorType, str]] = ..., name: _Optional[str] = ..., redshift: _Optional[_Union[RedshiftMetadata, _Mapping]] = ..., snowflake: _Optional[_Union[SnowflakeMetadata, _Mapping]] = ..., bigquery: _Optional[_Union[BigQueryMetadata, _Mapping]] = ..., azure_synapse: _Optional[_Union[AzureSynapseMetadata, _Mapping]] = ..., tableau: _Optional[_Union[TableauMetadata, _Mapping]] = ..., aurora: _Optional[_Union[AuroraMetadata, _Mapping]] = ..., databricks: _Optional[_Union[DatabricksMetadata, _Mapping]] = ..., motherduck: _Optional[_Union[MotherduckMetadata, _Mapping]] = ..., clickhouse: _Optional[_Union[ClickHouseMetadata, _Mapping]] = ..., mysql: _Optional[_Union[MYSQLMetadata, _Mapping]] = ..., athena: _Optional[_Union[AthenaMetadata, _Mapping]] = ..., google_drive: _Optional[_Union[GoogleDriveMetadata, _Mapping]] = ..., powerbi: _Optional[_Union[PowerBIMetadata, _Mapping]] = ..., postgres: _Optional[_Union[PostgresMetadata, _Mapping]] = ..., supabase: _Optional[_Union[SupabaseMetadata, _Mapping]] = ..., sql_server: _Optional[_Union[SQLServerMetadata, _Mapping]] = ...) -> None: ...

class RedshiftMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schemas", "dialect", "ssl_mode")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    DIALECT_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schemas: _containers.RepeatedScalarFieldContainer[str]
    dialect: str
    ssl_mode: bool
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schemas: _Optional[_Iterable[str]] = ..., dialect: _Optional[str] = ..., ssl_mode: bool = ...) -> None: ...

class PostgresMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schemas", "dialect", "ssl_mode")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    DIALECT_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schemas: _containers.RepeatedScalarFieldContainer[str]
    dialect: str
    ssl_mode: bool
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schemas: _Optional[_Iterable[str]] = ..., dialect: _Optional[str] = ..., ssl_mode: bool = ...) -> None: ...

class SupabaseMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schemas", "dialect", "ssl_mode")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    DIALECT_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schemas: _containers.RepeatedScalarFieldContainer[str]
    dialect: str
    ssl_mode: bool
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schemas: _Optional[_Iterable[str]] = ..., dialect: _Optional[str] = ..., ssl_mode: bool = ...) -> None: ...

class SnowflakeMetadata(_message.Message):
    __slots__ = ("username", "password", "private_key", "private_key_passphrase", "role", "schema", "locator", "database", "warehouse")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_PASSPHRASE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    LOCATOR_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    private_key: str
    private_key_passphrase: str
    role: str
    schema: str
    locator: str
    database: str
    warehouse: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ..., private_key: _Optional[str] = ..., private_key_passphrase: _Optional[str] = ..., role: _Optional[str] = ..., schema: _Optional[str] = ..., locator: _Optional[str] = ..., database: _Optional[str] = ..., warehouse: _Optional[str] = ...) -> None: ...

class BigQueryMetadata(_message.Message):
    __slots__ = ("project_id", "dataset_id", "service_account_key", "region_qualifier")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_KEY_FIELD_NUMBER: _ClassVar[int]
    REGION_QUALIFIER_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    dataset_id: str
    service_account_key: str
    region_qualifier: str
    def __init__(self, project_id: _Optional[str] = ..., dataset_id: _Optional[str] = ..., service_account_key: _Optional[str] = ..., region_qualifier: _Optional[str] = ...) -> None: ...

class AzureSynapseMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schema", "auth_type")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    AUTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schema: str
    auth_type: str
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schema: _Optional[str] = ..., auth_type: _Optional[str] = ...) -> None: ...

class AuroraMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schema", "dialect", "ssl_mode", "aurora_auth")
    class AuroraAuth(_message.Message):
        __slots__ = ("iam_auth", "cluster_id", "region")
        IAM_AUTH_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        REGION_FIELD_NUMBER: _ClassVar[int]
        iam_auth: bool
        cluster_id: str
        region: str
        def __init__(self, iam_auth: bool = ..., cluster_id: _Optional[str] = ..., region: _Optional[str] = ...) -> None: ...
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DIALECT_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    AURORA_AUTH_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schema: str
    dialect: str
    ssl_mode: bool
    aurora_auth: AuroraMetadata.AuroraAuth
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schema: _Optional[str] = ..., dialect: _Optional[str] = ..., ssl_mode: bool = ..., aurora_auth: _Optional[_Union[AuroraMetadata.AuroraAuth, _Mapping]] = ...) -> None: ...

class MYSQLMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schema", "ssl_mode")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schema: str
    ssl_mode: bool
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schema: _Optional[str] = ..., ssl_mode: bool = ...) -> None: ...

class SQLServerMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "schema", "ssl_mode")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SSL_MODE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    schema: str
    ssl_mode: bool
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., schema: _Optional[str] = ..., ssl_mode: bool = ...) -> None: ...

class TableauMetadata(_message.Message):
    __slots__ = ("server_url", "site_name", "pat_name", "pat_secret")
    SERVER_URL_FIELD_NUMBER: _ClassVar[int]
    SITE_NAME_FIELD_NUMBER: _ClassVar[int]
    PAT_NAME_FIELD_NUMBER: _ClassVar[int]
    PAT_SECRET_FIELD_NUMBER: _ClassVar[int]
    server_url: str
    site_name: str
    pat_name: str
    pat_secret: str
    def __init__(self, server_url: _Optional[str] = ..., site_name: _Optional[str] = ..., pat_name: _Optional[str] = ..., pat_secret: _Optional[str] = ...) -> None: ...

class PowerBIMetadata(_message.Message):
    __slots__ = ("tenant_id", "client_id", "client_secret")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    client_id: str
    client_secret: str
    def __init__(self, tenant_id: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ...) -> None: ...

class DatabricksMetadata(_message.Message):
    __slots__ = ("host", "http_path", "port", "databricks_auth", "catalog", "schema")
    class DatabricksAuth(_message.Message):
        __slots__ = ("pat", "client_credentials")
        class PersonalAccessToken(_message.Message):
            __slots__ = ("token",)
            TOKEN_FIELD_NUMBER: _ClassVar[int]
            token: str
            def __init__(self, token: _Optional[str] = ...) -> None: ...
        class ClientCredentials(_message.Message):
            __slots__ = ("client_id", "client_secret")
            CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
            CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
            client_id: str
            client_secret: str
            def __init__(self, client_id: _Optional[str] = ..., client_secret: _Optional[str] = ...) -> None: ...
        PAT_FIELD_NUMBER: _ClassVar[int]
        CLIENT_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
        pat: DatabricksMetadata.DatabricksAuth.PersonalAccessToken
        client_credentials: DatabricksMetadata.DatabricksAuth.ClientCredentials
        def __init__(self, pat: _Optional[_Union[DatabricksMetadata.DatabricksAuth.PersonalAccessToken, _Mapping]] = ..., client_credentials: _Optional[_Union[DatabricksMetadata.DatabricksAuth.ClientCredentials, _Mapping]] = ...) -> None: ...
    HOST_FIELD_NUMBER: _ClassVar[int]
    HTTP_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_AUTH_FIELD_NUMBER: _ClassVar[int]
    CATALOG_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    host: str
    http_path: str
    port: int
    databricks_auth: DatabricksMetadata.DatabricksAuth
    catalog: str
    schema: str
    def __init__(self, host: _Optional[str] = ..., http_path: _Optional[str] = ..., port: _Optional[int] = ..., databricks_auth: _Optional[_Union[DatabricksMetadata.DatabricksAuth, _Mapping]] = ..., catalog: _Optional[str] = ..., schema: _Optional[str] = ...) -> None: ...

class MotherduckMetadata(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class ClickHouseMetadata(_message.Message):
    __slots__ = ("host", "port", "user", "password", "database", "use_ssl", "protocol")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    USE_SSL_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    user: str
    password: str
    database: str
    use_ssl: bool
    protocol: str
    def __init__(self, host: _Optional[str] = ..., port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., database: _Optional[str] = ..., use_ssl: bool = ..., protocol: _Optional[str] = ...) -> None: ...

class AthenaMetadata(_message.Message):
    __slots__ = ("region", "database", "workgroup", "s3_output_location", "athena_auth")
    class AthenaAuth(_message.Message):
        __slots__ = ("access_key", "iam_role")
        class AccessKeyCredentials(_message.Message):
            __slots__ = ("access_key_id", "secret_access_key")
            ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
            SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
            access_key_id: str
            secret_access_key: str
            def __init__(self, access_key_id: _Optional[str] = ..., secret_access_key: _Optional[str] = ...) -> None: ...
        class IAMRoleCredentials(_message.Message):
            __slots__ = ("role_arn", "session_name")
            ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
            SESSION_NAME_FIELD_NUMBER: _ClassVar[int]
            role_arn: str
            session_name: str
            def __init__(self, role_arn: _Optional[str] = ..., session_name: _Optional[str] = ...) -> None: ...
        ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
        IAM_ROLE_FIELD_NUMBER: _ClassVar[int]
        access_key: AthenaMetadata.AthenaAuth.AccessKeyCredentials
        iam_role: AthenaMetadata.AthenaAuth.IAMRoleCredentials
        def __init__(self, access_key: _Optional[_Union[AthenaMetadata.AthenaAuth.AccessKeyCredentials, _Mapping]] = ..., iam_role: _Optional[_Union[AthenaMetadata.AthenaAuth.IAMRoleCredentials, _Mapping]] = ...) -> None: ...
    REGION_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    WORKGROUP_FIELD_NUMBER: _ClassVar[int]
    S3_OUTPUT_LOCATION_FIELD_NUMBER: _ClassVar[int]
    ATHENA_AUTH_FIELD_NUMBER: _ClassVar[int]
    region: str
    database: str
    workgroup: str
    s3_output_location: str
    athena_auth: AthenaMetadata.AthenaAuth
    def __init__(self, region: _Optional[str] = ..., database: _Optional[str] = ..., workgroup: _Optional[str] = ..., s3_output_location: _Optional[str] = ..., athena_auth: _Optional[_Union[AthenaMetadata.AthenaAuth, _Mapping]] = ...) -> None: ...

class GoogleDriveMetadata(_message.Message):
    __slots__ = ("access_token", "refresh_token", "member_id")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    member_id: str
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., member_id: _Optional[str] = ...) -> None: ...

class Connector(_message.Message):
    __slots__ = ("id", "name", "connector_type", "member_id", "created_at", "last_synced", "redshift_metadata", "snowflake_metadata", "bigquery_metadata", "azure_synapse_metadata", "tableau_metadata", "aurora_metadata", "databricks_metadata", "motherduck_metadata", "clickhouse_metadata", "mysql_metadata", "athena_metadata", "google_drive_metadata", "powerbi_metadata", "postgres_metadata", "supabase_metadata", "sql_server_metadata", "is_example")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_SYNCED_FIELD_NUMBER: _ClassVar[int]
    REDSHIFT_METADATA_FIELD_NUMBER: _ClassVar[int]
    SNOWFLAKE_METADATA_FIELD_NUMBER: _ClassVar[int]
    BIGQUERY_METADATA_FIELD_NUMBER: _ClassVar[int]
    AZURE_SYNAPSE_METADATA_FIELD_NUMBER: _ClassVar[int]
    TABLEAU_METADATA_FIELD_NUMBER: _ClassVar[int]
    AURORA_METADATA_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_METADATA_FIELD_NUMBER: _ClassVar[int]
    MOTHERDUCK_METADATA_FIELD_NUMBER: _ClassVar[int]
    CLICKHOUSE_METADATA_FIELD_NUMBER: _ClassVar[int]
    MYSQL_METADATA_FIELD_NUMBER: _ClassVar[int]
    ATHENA_METADATA_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_DRIVE_METADATA_FIELD_NUMBER: _ClassVar[int]
    POWERBI_METADATA_FIELD_NUMBER: _ClassVar[int]
    POSTGRES_METADATA_FIELD_NUMBER: _ClassVar[int]
    SUPABASE_METADATA_FIELD_NUMBER: _ClassVar[int]
    SQL_SERVER_METADATA_FIELD_NUMBER: _ClassVar[int]
    IS_EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    connector_type: ConnectorType
    member_id: str
    created_at: _timestamp_pb2.Timestamp
    last_synced: _timestamp_pb2.Timestamp
    redshift_metadata: RedshiftMetadata
    snowflake_metadata: SnowflakeMetadata
    bigquery_metadata: BigQueryMetadata
    azure_synapse_metadata: AzureSynapseMetadata
    tableau_metadata: TableauMetadata
    aurora_metadata: AuroraMetadata
    databricks_metadata: DatabricksMetadata
    motherduck_metadata: MotherduckMetadata
    clickhouse_metadata: ClickHouseMetadata
    mysql_metadata: MYSQLMetadata
    athena_metadata: AthenaMetadata
    google_drive_metadata: GoogleDriveMetadata
    powerbi_metadata: PowerBIMetadata
    postgres_metadata: PostgresMetadata
    supabase_metadata: SupabaseMetadata
    sql_server_metadata: SQLServerMetadata
    is_example: bool
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., connector_type: _Optional[_Union[ConnectorType, str]] = ..., member_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_synced: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., redshift_metadata: _Optional[_Union[RedshiftMetadata, _Mapping]] = ..., snowflake_metadata: _Optional[_Union[SnowflakeMetadata, _Mapping]] = ..., bigquery_metadata: _Optional[_Union[BigQueryMetadata, _Mapping]] = ..., azure_synapse_metadata: _Optional[_Union[AzureSynapseMetadata, _Mapping]] = ..., tableau_metadata: _Optional[_Union[TableauMetadata, _Mapping]] = ..., aurora_metadata: _Optional[_Union[AuroraMetadata, _Mapping]] = ..., databricks_metadata: _Optional[_Union[DatabricksMetadata, _Mapping]] = ..., motherduck_metadata: _Optional[_Union[MotherduckMetadata, _Mapping]] = ..., clickhouse_metadata: _Optional[_Union[ClickHouseMetadata, _Mapping]] = ..., mysql_metadata: _Optional[_Union[MYSQLMetadata, _Mapping]] = ..., athena_metadata: _Optional[_Union[AthenaMetadata, _Mapping]] = ..., google_drive_metadata: _Optional[_Union[GoogleDriveMetadata, _Mapping]] = ..., powerbi_metadata: _Optional[_Union[PowerBIMetadata, _Mapping]] = ..., postgres_metadata: _Optional[_Union[PostgresMetadata, _Mapping]] = ..., supabase_metadata: _Optional[_Union[SupabaseMetadata, _Mapping]] = ..., sql_server_metadata: _Optional[_Union[SQLServerMetadata, _Mapping]] = ..., is_example: bool = ...) -> None: ...

class CreateConnectorRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: ConnectorConfig
    def __init__(self, config: _Optional[_Union[ConnectorConfig, _Mapping]] = ...) -> None: ...

class CreateConnectorResponse(_message.Message):
    __slots__ = ("connector_id", "name", "connector_type")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    name: str
    connector_type: ConnectorType
    def __init__(self, connector_id: _Optional[int] = ..., name: _Optional[str] = ..., connector_type: _Optional[_Union[ConnectorType, str]] = ...) -> None: ...

class UpdateConnectorRequest(_message.Message):
    __slots__ = ("connector_id", "config")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    config: ConnectorConfig
    def __init__(self, connector_id: _Optional[int] = ..., config: _Optional[_Union[ConnectorConfig, _Mapping]] = ...) -> None: ...

class UpdateConnectorResponse(_message.Message):
    __slots__ = ("connector",)
    CONNECTOR_FIELD_NUMBER: _ClassVar[int]
    connector: Connector
    def __init__(self, connector: _Optional[_Union[Connector, _Mapping]] = ...) -> None: ...

class GetConnectorRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetConnectorResponse(_message.Message):
    __slots__ = ("connector",)
    CONNECTOR_FIELD_NUMBER: _ClassVar[int]
    connector: Connector
    def __init__(self, connector: _Optional[_Union[Connector, _Mapping]] = ...) -> None: ...

class GetConnectorsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetConnectorsResponse(_message.Message):
    __slots__ = ("connectors",)
    CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    connectors: _containers.RepeatedCompositeFieldContainer[Connector]
    def __init__(self, connectors: _Optional[_Iterable[_Union[Connector, _Mapping]]] = ...) -> None: ...

class DeleteConnectorRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class DeleteConnectorResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class TestConnectorRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: ConnectorConfig
    def __init__(self, config: _Optional[_Union[ConnectorConfig, _Mapping]] = ...) -> None: ...

class TestConnectorResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class DuplicateConnectorRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class DuplicateConnectorResponse(_message.Message):
    __slots__ = ("connector",)
    CONNECTOR_FIELD_NUMBER: _ClassVar[int]
    connector: Connector
    def __init__(self, connector: _Optional[_Union[Connector, _Mapping]] = ...) -> None: ...

class QueryResult(_message.Message):
    __slots__ = ("arrow_data", "total_rows")
    ARROW_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    arrow_data: bytes
    total_rows: int
    def __init__(self, arrow_data: _Optional[bytes] = ..., total_rows: _Optional[int] = ...) -> None: ...

class PrimaryKeyMetadata(_message.Message):
    __slots__ = ("columns", "descriptions")
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedScalarFieldContainer[str]
    descriptions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, columns: _Optional[_Iterable[str]] = ..., descriptions: _Optional[_Iterable[str]] = ...) -> None: ...

class ConnectorTable(_message.Message):
    __slots__ = ("table_database", "table_schema", "table_name", "preview", "listing_status", "listing_error", "primary_keys")
    TABLE_DATABASE_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    LISTING_STATUS_FIELD_NUMBER: _ClassVar[int]
    LISTING_ERROR_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_KEYS_FIELD_NUMBER: _ClassVar[int]
    table_database: str
    table_schema: str
    table_name: str
    preview: QueryResult
    listing_status: ListingStatus
    listing_error: str
    primary_keys: _containers.RepeatedCompositeFieldContainer[PrimaryKeyMetadata]
    def __init__(self, table_database: _Optional[str] = ..., table_schema: _Optional[str] = ..., table_name: _Optional[str] = ..., preview: _Optional[_Union[QueryResult, _Mapping]] = ..., listing_status: _Optional[_Union[ListingStatus, str]] = ..., listing_error: _Optional[str] = ..., primary_keys: _Optional[_Iterable[_Union[PrimaryKeyMetadata, _Mapping]]] = ...) -> None: ...

class ListConnectorTablesStreamRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class ListingProgressUpdate(_message.Message):
    __slots__ = ("status", "progress_percent", "current_table", "total_tables", "processed_tables", "error", "listing_result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TABLE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TABLES_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_TABLES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    LISTING_RESULT_FIELD_NUMBER: _ClassVar[int]
    status: ListingStatus
    progress_percent: float
    current_table: str
    total_tables: int
    processed_tables: int
    error: str
    listing_result: ListConnectorTablesResponse
    def __init__(self, status: _Optional[_Union[ListingStatus, str]] = ..., progress_percent: _Optional[float] = ..., current_table: _Optional[str] = ..., total_tables: _Optional[int] = ..., processed_tables: _Optional[int] = ..., error: _Optional[str] = ..., listing_result: _Optional[_Union[ListConnectorTablesResponse, _Mapping]] = ...) -> None: ...

class ListConnectorTablesResponse(_message.Message):
    __slots__ = ("connector_name", "connector_type", "table")
    CONNECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    connector_name: str
    connector_type: ConnectorType
    table: ConnectorTable
    def __init__(self, connector_name: _Optional[str] = ..., connector_type: _Optional[_Union[ConnectorType, str]] = ..., table: _Optional[_Union[ConnectorTable, _Mapping]] = ...) -> None: ...

class SyncTableRequest(_message.Message):
    __slots__ = ("connector_id", "table_database", "table_schema", "table_name", "preview")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_DATABASE_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    table_database: str
    table_schema: str
    table_name: str
    preview: QueryResult
    def __init__(self, connector_id: _Optional[int] = ..., table_database: _Optional[str] = ..., table_schema: _Optional[str] = ..., table_name: _Optional[str] = ..., preview: _Optional[_Union[QueryResult, _Mapping]] = ...) -> None: ...

class SyncConnectorTablesStreamRequest(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[SyncTableRequest]
    def __init__(self, tables: _Optional[_Iterable[_Union[SyncTableRequest, _Mapping]]] = ...) -> None: ...

class SyncProgressUpdate(_message.Message):
    __slots__ = ("status", "progress_percent", "total_tables", "processed_tables", "table_statuses", "error")
    class TableStatusesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SyncTableStatus
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SyncTableStatus, _Mapping]] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TABLES_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_TABLES_FIELD_NUMBER: _ClassVar[int]
    TABLE_STATUSES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    status: SyncStatus
    progress_percent: float
    total_tables: int
    processed_tables: int
    table_statuses: _containers.MessageMap[str, SyncTableStatus]
    error: str
    def __init__(self, status: _Optional[_Union[SyncStatus, str]] = ..., progress_percent: _Optional[float] = ..., total_tables: _Optional[int] = ..., processed_tables: _Optional[int] = ..., table_statuses: _Optional[_Mapping[str, SyncTableStatus]] = ..., error: _Optional[str] = ...) -> None: ...

class SyncTableStatus(_message.Message):
    __slots__ = ("status", "error")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    status: SyncStatus
    error: str
    def __init__(self, status: _Optional[_Union[SyncStatus, str]] = ..., error: _Optional[str] = ...) -> None: ...

class RetryTableRequest(_message.Message):
    __slots__ = ("connector_id", "table_database", "table_schema", "table_name")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_DATABASE_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    table_database: str
    table_schema: str
    table_name: str
    def __init__(self, connector_id: _Optional[int] = ..., table_database: _Optional[str] = ..., table_schema: _Optional[str] = ..., table_name: _Optional[str] = ...) -> None: ...

class RetryConnectorTablesStreamRequest(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[RetryTableRequest]
    def __init__(self, tables: _Optional[_Iterable[_Union[RetryTableRequest, _Mapping]]] = ...) -> None: ...

class GetTablePreviewRequest(_message.Message):
    __slots__ = ("connector_id", "table_database", "table_schema", "table_name", "limit")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_DATABASE_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    table_database: str
    table_schema: str
    table_name: str
    limit: int
    def __init__(self, connector_id: _Optional[int] = ..., table_database: _Optional[str] = ..., table_schema: _Optional[str] = ..., table_name: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class GetTablePreviewResponse(_message.Message):
    __slots__ = ("arrow_data", "success", "error_message")
    ARROW_DATA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    arrow_data: bytes
    success: bool
    error_message: str
    def __init__(self, arrow_data: _Optional[bytes] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class UnsyncTableRequest(_message.Message):
    __slots__ = ("connector_id", "table_database", "table_schema", "table_name")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_DATABASE_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    table_database: str
    table_schema: str
    table_name: str
    def __init__(self, connector_id: _Optional[int] = ..., table_database: _Optional[str] = ..., table_schema: _Optional[str] = ..., table_name: _Optional[str] = ...) -> None: ...

class UnsyncConnectorTablesRequest(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[UnsyncTableRequest]
    def __init__(self, tables: _Optional[_Iterable[_Union[UnsyncTableRequest, _Mapping]]] = ...) -> None: ...

class UnsyncConnectorTablesResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetSyncedTablesRequest(_message.Message):
    __slots__ = ("connector_id",)
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    def __init__(self, connector_id: _Optional[int] = ...) -> None: ...

class GetSyncedTablesResponse(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[ConnectorTable]
    def __init__(self, tables: _Optional[_Iterable[_Union[ConnectorTable, _Mapping]]] = ...) -> None: ...

class ExecuteQueryRequest(_message.Message):
    __slots__ = ("connector_id", "query", "limit")
    CONNECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    connector_id: int
    query: str
    limit: int
    def __init__(self, connector_id: _Optional[int] = ..., query: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class ExecuteQueryResponse(_message.Message):
    __slots__ = ("arrow_data", "success", "error_message")
    ARROW_DATA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    arrow_data: bytes
    success: bool
    error_message: str
    def __init__(self, arrow_data: _Optional[bytes] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...
