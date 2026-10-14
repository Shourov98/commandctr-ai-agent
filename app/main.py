from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.config import get_settings
from app.request_logging import print_request_log, read_payload_for_log
from app.services.import_service import ImportService
from app.services.product_service import ProductService


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
    app.include_router(api_router, prefix="/api")
    app.include_router(api_router, prefix="/api/v1", include_in_schema=False)

    @app.middleware("http")
    async def request_logger_middleware(request, call_next):
        start = perf_counter()
        request_id = request.headers.get("x-request-id") or str(uuid4())
        payload = await read_payload_for_log(request)
        query = dict(request.query_params.multi_items())
        client = request.client.host if request.client else "unknown"
        try:
            response = await call_next(request)
        except Exception:
            print_request_log(
                service="Twinstr AI Agent",
                method=request.method,
                path=request.url.path,
                status_code="ERROR",
                duration_ms=(perf_counter() - start) * 1000,
                request_id=request_id,
                client=client,
                query=query,
                payload=payload,
            )
            raise
        response.headers["x-request-id"] = request_id
        print_request_log(
            service="Twinstr AI Agent",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=(perf_counter() - start) * 1000,
            request_id=request_id,
            client=client,
            query=query,
            payload=payload,
        )
        return response

    @app.on_event("startup")
    async def warm_service_caches() -> None:
        ProductService()
        ImportService()

    @app.on_event("shutdown")
    async def close_service_caches() -> None:
        ImportService.reset_shared_state()
        ProductService.reset_shared_state()
    return app


app = create_app()
