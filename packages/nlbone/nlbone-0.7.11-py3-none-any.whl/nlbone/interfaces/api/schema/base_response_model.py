from pydantic import BaseModel, ConfigDict, model_serializer

from nlbone.core.domain.base import BaseId

EXCLUDE_NONE = "exclude_none"


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            BaseId: lambda v: str(v.value),
        },
    )

    @model_serializer(mode="wrap")
    def _auto_hide_none_fields(self, handler):
        data = handler(self)

        hide_candidates = {
            name for name, f in self.model_fields.items() if (f.json_schema_extra or {}).get(EXCLUDE_NONE) is True
        }

        for key in list(data.keys()):
            if key in hide_candidates and data[key] is None:
                data.pop(key)

        return data
