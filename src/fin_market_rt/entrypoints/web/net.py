import asyncio
import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fin_market_rt.settings import ACCESS_LOG_DEFAULT_FORMAT, Settings
from fin_market_rt.third_party.facet import ServiceMixin
from fin_market_rt.third_party.giveme import inject, register
from hypercorn.asyncio import serve
from hypercorn.config import Config
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import Message



def _api_error(status_code: int, code: str, message: str | None = None, data: Any | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": repr(message),
            "data": repr(data),
        },
    )


class QueryParamLoggerMiddleware(BaseHTTPMiddleware):
    async def set_body(self, request: Request, body: bytes) -> None:
        async def receive() -> Message:
            return {"type": "http.request", "body": body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # log the request
        logger.info("{} {}", request.method, request.url)

        if request.method == "GET":
            # GET requests don't have a body
            response = await call_next(request)
            return response

        # Log the request body
        # https://github.com/tiangolo/fastapi/issues/394#issuecomment-883524819
        await self.set_body(request, await request.body())
        body = await self.get_body(request)
        if body:
            try:
                # Decode to string and parse as JSON
                body_str = body.decode()
                body_json = json.loads(body_str)
                logger.info("Body: {}", body_json)
            except Exception:
                logger.exception("Exception while parsing body")
                logger.info("Raw Body: {}", body.decode("utf-8"))

        response = await call_next(request)
        return response


class NetHttpServer(ServiceMixin):
    def __init__(
        self,
        host: str | None = None,
        port: int = 80,
        *,
        enable_access_log: bool = False,
        access_log_format: str = ACCESS_LOG_DEFAULT_FORMAT,
        web_log_requests: bool = False,
    ):
        self.host = host
        self.port = port
        self.hypercorn_config = Config.from_mapping(
            bind=f"{host}:{port}",
            access_log_format=access_log_format,
            graceful_timeout=0,
        )
        if enable_access_log:
            self.hypercorn_config.accesslog = "-"
        self.app = FastAPI(
            redirect_slashes=False,
        )
        self.web_log_requests = web_log_requests

    async def start(self) -> None:
        self.app.add_exception_handler(Exception, self.error_handler)
        self.app.add_exception_handler(StarletteHTTPException, self.exception_handler)
        self.app.add_exception_handler(RequestValidationError, self.validation_handler)

        if self.web_log_requests:
            self.app.add_middleware(QueryParamLoggerMiddleware)

        self.add_task(
            serve(
                self.app,  # type: ignore
                self.hypercorn_config,
                shutdown_trigger=asyncio.Future,  # no signal handling
            ),
        )

    async def error_handler(self, request: Request, exc: Exception) -> JSONResponse:
        return _api_error(
            status_code=500,
            code="common.internal_server_error",
            message="Internal server error",
        )

    async def exception_handler(self, request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _api_error(
            status_code=exc.status_code,
            code="common.http_error",
            message=exc.detail,
        )

    async def validation_handler(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        return _api_error(
            status_code=422,
            code="common.validation_error",
            message=str(exc),
            data=exc.errors(),
        )


@register(name="net_http_server", singleton=True)
@inject
def net_http_server_factory(settings: Settings) -> NetHttpServer:
    return NetHttpServer(
        host=settings.project.web_host,
        port=settings.project.web_port,
        access_log_format=settings.project.web_access_log_format,
        web_log_requests=settings.project.web_log_requests,
        enable_access_log=settings.project.web_enable_access_log,
    )
