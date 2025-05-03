from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    secret_key: str
    algo: str
    access_token_expire_minutes: int


settings = Settings()
