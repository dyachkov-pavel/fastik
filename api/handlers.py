import uuid
from logging import getLogger
from typing import Optional

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdatedUserResponse
from api.models import UpdateUserRequest
from api.models import UserCreate
from db.dals import UserDAL
from db.models import User
from db.session import get_db

user_router = APIRouter()
logger = getLogger()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    # do it with dependency?
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, db) -> Optional[uuid.UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = await user_dal.delete_user(user_id)
            return deleted_user_id


async def _update_user(body: dict, user_id, db) -> Optional[uuid.UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update_user(user_id, **body)
            return updated_user_id


async def _get_user_by_id(user_id, session) -> Optional[User]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        return HTTPException(
            status_code=404, detail=f"User with id {user_id} not found"
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
) -> UpdatedUserResponse:
    """Wont update if user is deactivated!!"""
    updated_fields = body.model_dump(exclude_none=True)

    if len(updated_fields) == 0:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter should be provided for update",
        )
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    updated_user_id = await _update_user(updated_fields, user_id, db)
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.get("/{user_id}")
async def get_user_by_id(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user
