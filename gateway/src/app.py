from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.openapi.docs import get_swagger_ui_html
import httpx


app = FastAPI(
    title="School API Gateway",
    version="1.0.0",
    description="Single-entry API gateway for school microservices",
)


SERVICE_BASE_URLS: dict[str, str] = {
    "students": "http://127.0.0.1:8001",
    "teachers": "http://127.0.0.1:8002",
    "sports": "http://127.0.0.1:8003",
    "exams": "http://127.0.0.1:8004",
    "subjects": "http://127.0.0.1:8005",
}


@app.get("/")
def root() -> dict[str, object]:
    return {
        "message": "School API Gateway is running",
        "usage": "Use /api/{service-name}/{service-path}",
        "services": list(SERVICE_BASE_URLS.keys()),
    }


@app.get("/services")
def list_services() -> dict[str, str]:
    return SERVICE_BASE_URLS


@app.get("/api/{service_name}/docs")
def service_docs(service_name: str) -> Response:
    if service_name not in SERVICE_BASE_URLS:
        raise HTTPException(status_code=404, detail="Unknown service")

    return get_swagger_ui_html(
        openapi_url=f"/api/{service_name}/openapi.json",
        title=f"{service_name.capitalize()} Service Docs via Gateway",
    )


@app.api_route(
    "/api/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy(service_name: str, path: str, request: Request) -> Response:
    base_url = SERVICE_BASE_URLS.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail="Unknown service")

    target_url = f"{base_url}/{path}"

    body = await request.body()
    content_type = request.headers.get("content-type")
    headers: dict[str, str] = {}
    if content_type:
        headers["content-type"] = content_type

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=body,
            headers=headers,
        )

    response_headers = {}
    upstream_content_type = upstream_response.headers.get("content-type")
    if upstream_content_type:
        response_headers["content-type"] = upstream_content_type

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )
