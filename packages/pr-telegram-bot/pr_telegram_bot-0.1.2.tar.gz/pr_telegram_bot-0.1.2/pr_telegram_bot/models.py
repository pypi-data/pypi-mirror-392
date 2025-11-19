from typing import Any

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None  # Field(validation_alias=AliasChoices("id", "chat_id"))
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None
    state: str = "Start"  # Default state
    data: dict[str, Any] = {}
