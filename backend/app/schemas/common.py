from typing import ClassVar

from pydantic import BaseModel, model_validator


class UpdateModel(BaseModel):
    """Optional in a partial update is different from explicitly nullable."""
    non_nullable: ClassVar[set[str]] = set()

    @model_validator(mode="before")
    @classmethod
    def reject_null(cls, data):
        if isinstance(data, dict):
            for field in cls.non_nullable:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} 不能为 null")
        return data
