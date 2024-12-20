from enum import Enum
from typing import Union

from pydantic import BaseModel, Field, field_validator

from med_results_parser import PROJROOT
from med_results_parser.core.yaml_handler import YamlFileHandler
from med_results_parser.settings.config import settings

yml_loader = YamlFileHandler()


class ValueEnum(str, Enum):
    @staticmethod
    def to_numeric(value: str, enum_mapping):
        if value in enum_mapping["negative"]:
            return 0
        elif value in enum_mapping["positive"]:
            return 1
        return value


class AnalysisModel(BaseModel):
    patient_code: int = Field(alias="Код пациента")
    analysis: str = Field(alias="Анализ")
    value: Union[int, str] = Field(alias="Значение")

    @field_validator("value", mode="after")
    def validate_value(cls, v):
        if settings.enum.enam_path:
            enum_mapping = yml_loader.read(settings.enum.enam_path)
        else:
            enum_mapping = yml_loader.read(PROJROOT / "enum_values.yaml")
        return ValueEnum.to_numeric(v, enum_mapping)
