from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserDAL:
    "Data Access Language for operating users info"

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_user(self, name: str, surname: str, email: str) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        print("DDDD", deleted_user_id_row)
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(
        # self, user_id: UUID, name: str, surname: str, email: str
        self,
        user_id: UUID,
        **kwargs
    ) -> Union[UUID, None]:
        """idk name/surname/email is optional or not?"""
        print("AAAAA", kwargs)
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(**kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]
