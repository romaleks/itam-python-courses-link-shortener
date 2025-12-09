from sqlalchemy import insert, select, desc

from infrastructure.db_connection import create_all_tables, connection
from persistent.link import Link, LinkUsage


class LinkRepository:
    def __init__(self) -> None:
        self._sessionmaker = connection()
        create_all_tables()

    async def create_link(self, short_link: str, real_link: str) -> None:
        stmp = insert(Link).values({"short_link": short_link, "real_link": real_link})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_link(self, short_link: str) -> Link | None:
        stmp = select(Link).where(Link.short_link == short_link).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]

    async def put_link_usage(self, link_id: str, ip_address: str | None, user_agent: str | None) -> None:
        stmp = insert(LinkUsage).values({"link_id":link_id, "ip_address": ip_address, "user_agent": user_agent})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()
    
    async def get_link_usage_statistics(self, link_id: str, offset: int, limit: int) -> list[LinkUsage] | None:
        stmp = select(LinkUsage).where(Link.id == link_id).order_by(desc(LinkUsage.created_at)).offset(offset).limit(limit)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)
        
        row = resp.fetchone()
        if row is None:
            return None

        return row[0]