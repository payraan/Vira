from __future__ import annotations

import uuid
from pydantic import BaseModel


class UserOut(BaseModel):
    id: uuid.UUID
    telegram_id: str

    model_config = {"from_attributes": True}
