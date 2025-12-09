import re

from fastapi import Request

from repositories.link_repository import LinkRepository
from persistent.link import LinkUsage
from utils.utils_random import random_alfanum


class LinkService:
    def __init__(self) -> None:
        self._link_repository = LinkRepository()

    async def create_link(self, real_link: str) -> str:
        short_link = random_alfanum(5)

        await self._link_repository.create_link(short_link, real_link)

        return short_link

    async def get_real_link(self, short_link: str) -> str | None:
        link = await self._link_repository.get_link(short_link)
        if link is None:
            return None

        return str(link.real_link)
    
    async def put_link_usage(self, short_link: str, request: Request) -> None:
        link = await self._link_repository.get_link(short_link)

        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        
        await self._link_repository.put_link_usage(link_id=link.id, ip_address=ip_address, user_agent=user_agent)
    
    def check_link(self, link: str) -> bool:
        pattern = r'^(https?|ftp)://([^\s/$.?#]+\.)+[^\s/$.?#]+[^\s]*$'
        return bool(re.match(pattern, link))
    
    def convert_link(self, link:str) -> str:
        if 'https://' not in link:
            link = 'https://' + link
        return link
    
    async def get_link_statistics(self, short_link: str, page: int = 1, page_size: int = 10) -> list[LinkUsage]:
        offset = (page - 1) * page_size

        link = await self._link_repository.get_link(short_link)
        return await self._link_repository.get_link_usage_statistics(link_id=link.id, offset=offset, limit=page_size)