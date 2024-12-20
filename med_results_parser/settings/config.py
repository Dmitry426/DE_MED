__all__ = "settings"

from pathlib import Path

from pydantic.v1 import BaseSettings


class MedData:
    class Config:
        env_prefix = "MED_"

    file_name: str = "medicine.xlsx"


class YamlConfig(BaseSettings):
    class Config:
        env_prefix = "ENUM_"

    enam_path: str = None


class DatabaseSettings(BaseSettings):
    class Config:
        env_prefix = "PG_"

    """
    Configuration for the database connection, validated using Pydantic.
    """
    db_name: str = "db"
    db_user: str = "user"
    db_password: str = "pass"
    host: str = "localhost"
    port: int = 6432

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    db = DatabaseSettings()
    enum = YamlConfig()
    med_data = MedData()
    project_path = Path(__file__).resolve().parent.parent


settings = Settings()
