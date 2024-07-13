from enum import StrEnum

from pydantic import AnyUrl, Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from fin_market_rt.third_party.giveme import register

ACCESS_LOG_DEFAULT_FORMAT = '%(h)s %(l)s "%(r)s" %(s)s %(b)s "%(a)s"'

class LogLevel(StrEnum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"



class CoreSettings(BaseSettings):
    project_name: str = "Scope Manager"
    service_name: str = "scope_manager"
    version: str = "unknown version"
    environment: str = "unknown"  # feature, pre-prod, prod
    app_env: str = "development"  # development, production, like RAILS_ENV or NODE_ENV
    namespace: str = "namespace"
    log_level: LogLevel = LogLevel.INFO

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProjectSettings(BaseSettings):
    # rabbit listener
    rabbit_status_updater_queue_name: str = "tasks.status"
    rabbit_add_task_queue_name: str = "tasks.preprocessed"
    rabbit_silence_timeout: float | None = 60.0
    expire_tasks_routine_interval: float = 60.0

    # web
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    web_enable_access_log: bool = False
    web_access_log_format: str = ACCESS_LOG_DEFAULT_FORMAT
    web_log_requests: bool = False

    # mysql
    mysql_da_db_user: str  | None
    mysql_da_db_password: str | None
    mysql_da_db_host: str | None
    mysql_da_db_port: int | None
    mysql_da_db_name: str | None
    ql_db_url: AnyUrl | None = "mysql://{{ mysql_da_db_user }}:{{ mysql_da_db_password }}@{{ mysql_da_db_host }}:{{ mysql_da_db_port }}/{{ mysql_da_db_name }}"
    sql_db_pool_size: int = 5
    sql_db_pool_recycle: int = 300
    sql_db_query_timeout: float | None = None
    sql_db_healthcheck_timeout: float = 5
    sql_db_healthy_delay: float = 5 * 60
    sql_db_force_unverified_ssl: bool = False

    model_config = SettingsConfigDict(
        env_prefix="SM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@register(name="settings", singleton=True)
class Settings(BaseModel):
    core: CoreSettings = Field(default_factory=CoreSettings)
    project: ProjectSettings = Field(default_factory=ProjectSettings)