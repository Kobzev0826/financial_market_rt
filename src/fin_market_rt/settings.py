from enum import StrEnum

from pydantic import AnyUrl, Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from fin_market_rt.third_party.giveme import register
from yarl import URL

ACCESS_LOG_DEFAULT_FORMAT = '%(h)s %(l)s "%(r)s" %(s)s %(b)s "%(a)s"'

class LogLevel(StrEnum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"



class CoreSettings(BaseSettings):
    project_name: str = "Financial Market Realtime"
    service_name: str = "fin_market_rt"
    version: str = "unknown version"
    environment: str = "unknown"  # feature, pre-prod, prod
    app_env: str = "development"  # development, production
    namespace: str = "namespace"
    log_level: LogLevel = LogLevel.INFO

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProjectSettings(BaseSettings):
    # web
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    web_enable_access_log: bool = False
    web_access_log_format: str = ACCESS_LOG_DEFAULT_FORMAT
    web_log_requests: bool = False

    # mysql
    mysql_db_user: str  | None
    mysql_db_password: str | None
    mysql_db_host: str | None
    mysql_db_port: int | None
    mysql_db_name: str | None 
    mysql_db_url: str | None = None
    sql_db_pool_size: int = 5
    sql_db_pool_recycle: int = 300
    sql_db_query_timeout: float | None = None
    sql_db_healthcheck_timeout: float = 5
    sql_db_healthy_delay: float = 5 * 60
    sql_db_force_unverified_ssl: bool = False


    @property
    def sql_db_url_resolved(self) -> str:
        sql_db_url = self.mysql_db_url or f'mysql://{self.mysql_db_user}:{self.mysql_db_password}@{self.mysql_db_host}:{self.mysql_db_port}/{self.mysql_db_name}'
        url = str(URL(str(sql_db_url)).with_scheme("mysql+aiomysql"))
        return url


    model_config = SettingsConfigDict(
        env_prefix="FMRL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@register(name="settings", singleton=True)
class Settings(BaseModel):
    core: CoreSettings = Field(default_factory=CoreSettings)
    project: ProjectSettings = Field(default_factory=ProjectSettings)