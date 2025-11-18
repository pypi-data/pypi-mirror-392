from pydantic import Field, NatsDsn, SecretStr, AnyUrl
from pydantic_settings import BaseSettings


class NatsConfig(BaseSettings):
    nats_url: NatsDsn

class SqsConfig(BaseSettings):
    sqs_endpoint: AnyUrl
    sqs_access_key: str
    sqs_secret_key: SecretStr
    sqs_region_name: str

    sqs_max_number_of_messages: int = Field(default=10)
    sqs_wait_time_seconds: int = Field(default=10)
    sqs_visibility_timeout: int = Field(default=30)


class ObjectStorageConfig(BaseSettings):
    object_storage_access_key: str
    object_storage_secret_key: SecretStr
    object_storage_region: str


class S3StorageConfig(BaseSettings):
    s3_access_key: str
    s3_secret_key: SecretStr
    s3_region: str
    s3_endpoint: str | None = None


class MlflowConfig(BaseSettings):
    mlflow_tracking_uri: AnyUrl
    mlflow_registry_uri: AnyUrl


class LokiLoggerConfig(BaseSettings):
    loki_push_endpoint: str
    loki_user: str
    loki_token: str


class SlackWebhook(BaseSettings):
    slack_webhook_url: str

class TeamsWebhook(BaseSettings):
    teams_webhook_url: str

class DiscordWebhook(BaseSettings):
    discord_webhook_url: str

