import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import Field
from pydantic import validator
from typing_extensions import Annotated
from typing_extensions import Union

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @validator("name", "surname")
    def validate_fio(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Field should contain only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Annotated[Optional[str], Field(default=None, min_length=1)] = None
    surname: Annotated[Optional[str], Field(default=None, min_length=1)] = None
    email: Optional[EmailStr] = None
