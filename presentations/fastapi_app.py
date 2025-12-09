import time
from typing import Callable, Awaitable

from fastapi import FastAPI, HTTPException, Response, Request, status
from pydantic import BaseModel
from loguru import logger

from services.link_service import LinkService


def create_app() -> FastAPI:
    app = FastAPI()
    short_link_service = LinkService()

    class PutLink(BaseModel):
        link: str

    def _service_link_to_real(short_link: str) -> str:
        return f"http://localhost:8000/{short_link}"

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        t0 = time.time()
        
        response = await call_next(request)

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["X-Latency"] = str(elapsed_ms)
        logger.debug("{} {} done in {}ms", request.method, request.url, elapsed_ms)
        
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> Response:
        logger.error(
            "Unhandled exception: {} {} - {}: {}",
            request.method,
            request.url,
            type(exc).__name__,
            str(exc),
            exc_info=True
        )
        
        logger.debug("Request details: method={}, url={}, headers={}, client={}",
                    request.method, request.url, dict(request.headers), request.client)
        
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Internal server error"
        )

    @app.post("/link")
    async def create_link(put_link_request: PutLink) -> PutLink:
        right_link = short_link_service.convert_link(put_link_request.link)

        is_valid_link = short_link_service.check_link(right_link)
        if not is_valid_link:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Link is not valid")

        short_link = await short_link_service.create_link(right_link)
        return PutLink(link=_service_link_to_real(short_link))

    @app.get("/{link}")
    async def get_link(link: str, request: Request) -> Response:
        real_link = await short_link_service.get_real_link(link, request)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")
        
        await short_link_service.put_link_usage(link, request)

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    @app.get("/{short_link}/statistics")
    async def get_link_statistics(short_link: str, page: int = 1, page_size: int = 10,) -> Response:
        real_link = await short_link_service.get_real_link(short_link)
        if real_link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short link not found:("
            )
    
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page must be greater than 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page size must be between 1 and 100"
            )
        
        statistics = await short_link_service.get_link_statistics(short_link, page, page_size)
        
        return statistics

    return app