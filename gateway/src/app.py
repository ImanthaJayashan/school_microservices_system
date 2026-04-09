from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
import httpx
import json


app = FastAPI(
    title="School API Gateway",
    version="1.0.0",
    description="Single-entry API gateway for school microservices",
    docs_url=None,
    redoc_url=None,
)


SERVICE_BASE_URLS: dict[str, str] = {
    "students": "http://127.0.0.1:8001",
    "teachers": "http://127.0.0.1:8002",
    "sports": "http://127.0.0.1:8003",
    "exams": "http://127.0.0.1:8004",
    "subjects": "http://127.0.0.1:8005",
}

SERVICE_RESOURCES: dict[str, str] = {
    "students": "students",
    "teachers": "teachers",
    "sports": "sports",
    "exams": "exams",
    "subjects": "subjects",
}

SERVICE_ALIASES: dict[str, str] = {
    "student": "students",
    "teacher": "teachers",
    "sport": "sports",
    "exam": "exams",
    "subject": "subjects",
}


def _normalize_service_name(service_name: str) -> str:
    return SERVICE_ALIASES.get(service_name, service_name)


def _resolve_target_path(service_name: str, path: str) -> str:
    resource = SERVICE_RESOURCES[service_name]
    clean_path = path.lstrip("/")

    # Do not rewrite service metadata/documentation paths.
    if clean_path in {"openapi.json", "docs", "redoc"}:
        return clean_path

    if clean_path == "":
        return resource
    if clean_path == resource or clean_path.startswith(f"{resource}/"):
        return clean_path
    return f"{resource}/{clean_path}"


def _swagger_html(openapi_url: str, title: str, selected_service: str | None = None) -> HTMLResponse:
    response = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
            "filter": True,
            "persistAuthorization": True,
        },
    )

    service_links = "".join(
        (
            f'<a class="quick-link {'active' if selected_service == service else ''}" '
            f'href="/api/{service}/docs">{service.capitalize()}</a>'
        )
        for service in SERVICE_BASE_URLS
    )

    helper_bar = f"""
    <div class="quick-nav">
        <a class="quick-link" href="/">Gateway Home</a>
        <a class="quick-link {'active' if selected_service is None else ''}" href="/docs">Gateway Docs</a>
        {service_links}
    </div>
    <style>
        .quick-nav {{
            position: sticky;
            top: 0;
            z-index: 1000;
            padding: 10px 16px;
            background: #0f2a2f;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            border-bottom: 1px solid #1f4750;
        }}

        .quick-link {{
            text-decoration: none;
            color: #e8f6f8;
            background: #1c5661;
            border: 1px solid #2a6c78;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 0.9rem;
            line-height: 1;
        }}

        .quick-link:hover {{
            background: #28727f;
        }}

        .quick-link.active {{
            background: #0e8f83;
            border-color: #12a395;
            font-weight: 600;
        }}

        .swagger-ui .topbar {{
            display: none;
        }}
    </style>
    """

    html = response.body.decode("utf-8").replace("<body>", f"<body>{helper_bar}")
    return HTMLResponse(content=html, status_code=response.status_code)


@app.get("/docs", include_in_schema=False)
def gateway_docs() -> HTMLResponse:
    return _swagger_html(
        openapi_url="/openapi.json",
        title="School API Gateway Docs",
        selected_service=None,
    )


@app.get("/", response_class=HTMLResponse)
def root() -> str:
        options = "\n".join(
                f'<option value="{name}">{name.capitalize()}</option>'
                for name in SERVICE_BASE_URLS
        )

        return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>School API Gateway</title>
    <style>
        :root {{
            --bg: #f3f7f8;
            --panel: #ffffff;
            --text: #0f2a2f;
            --muted: #4a676d;
            --accent: #0e8f83;
            --accent-dark: #0a6e64;
            --border: #d7e4e7;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at 10% 10%, #d8f0ee 0%, transparent 28%),
                radial-gradient(circle at 90% 20%, #dceef8 0%, transparent 26%),
                var(--bg);
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }}

        .card {{
            width: min(840px, 100%);
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 16px 40px rgba(15, 42, 47, 0.08);
            overflow: hidden;
        }}

        .header {{
            padding: 24px;
            border-bottom: 1px solid var(--border);
        }}

        .header h1 {{
            margin: 0 0 6px;
            font-size: clamp(1.4rem, 2.3vw, 2rem);
        }}

        .header p {{
            margin: 0;
            color: var(--muted);
            line-height: 1.5;
        }}

        .content {{
            padding: 24px;
            display: grid;
            gap: 16px;
        }}

        label {{
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
        }}

        select {{
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid var(--border);
            font-size: 1rem;
            color: var(--text);
            background: #fff;
        }}

        .urls {{
            background: #f8fbfc;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            display: grid;
            gap: 8px;
        }}

        .urls span {{
            font-size: 0.9rem;
            color: var(--muted);
        }}

        .urls code {{
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.95rem;
            color: var(--text);
            display: block;
            word-break: break-word;
        }}

        .actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .btn {{
            appearance: none;
            border: none;
            background: var(--accent);
            color: #fff;
            padding: 11px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: transform 120ms ease, background 120ms ease;
        }}

        .btn:hover {{
            background: var(--accent-dark);
            transform: translateY(-1px);
        }}

        .btn.secondary {{
            background: #2f4e57;
        }}

        .btn.secondary:hover {{
            background: #223a41;
        }}

        .note {{
            color: var(--muted);
            font-size: 0.93rem;
            line-height: 1.45;
        }}

        .data-panel {{
            border: 1px solid var(--border);
            border-radius: 12px;
            background: #f8fbfc;
            padding: 14px;
            display: grid;
            gap: 10px;
        }}

        .data-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .status {{
            font-size: 0.9rem;
            color: var(--muted);
            margin: 0;
        }}

        pre {{
            margin: 0;
            max-height: 280px;
            overflow: auto;
            background: #0f2a2f;
            color: #e7f8fb;
            border-radius: 10px;
            padding: 12px;
            font-size: 0.84rem;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <main class="card">
        <section class="header">
            <h1>School API Gateway</h1>
              <p>Select a service to quickly open its Swagger docs or copy CRUD route templates through the gateway on port 8000.</p>
        </section>

        <section class="content">
            <div>
                <label for="serviceSelect">Service</label>
                <select id="serviceSelect">{options}</select>
            </div>

            <div class="urls">
                <span>Docs URL</span>
                <code id="docsUrl"></code>
                <span>CRUD Base URL</span>
                <code id="crudBaseUrl"></code>
                <span>CRUD by ID URL</span>
                <code id="crudByIdUrl"></code>
            </div>

            <div class="actions">
                <a class="btn" id="openDocsBtn" href="#" target="_blank" rel="noopener">Open Service Docs</a>
                <a class="btn secondary" href="/docs" target="_blank" rel="noopener">Open Gateway Docs</a>
            </div>

            <p class="note">
                Route format: /api/&lt;service&gt; and /api/&lt;service&gt;/&lt;id&gt; (legacy /api/&lt;service&gt;/&lt;resource&gt; still works)
            </p>

            <section class="data-panel">
                <div class="data-head">
                    <strong>Live Data (GET List)</strong>
                    <button class="btn" id="fetchBtn" type="button">Fetch Data</button>
                </div>
                <p class="status" id="fetchStatus">Select a service and click Fetch Data.</p>
                <pre id="dataPreview">[]</pre>
            </section>
        </section>
    </main>

    <script>
        const serviceToResource = {SERVICE_RESOURCES};
        const serviceSelect = document.getElementById('serviceSelect');
        const docsUrl = document.getElementById('docsUrl');
        const crudBaseUrl = document.getElementById('crudBaseUrl');
        const crudByIdUrl = document.getElementById('crudByIdUrl');
        const openDocsBtn = document.getElementById('openDocsBtn');
        const fetchBtn = document.getElementById('fetchBtn');
        const fetchStatus = document.getElementById('fetchStatus');
        const dataPreview = document.getElementById('dataPreview');

        async function fetchServiceData() {{
            const service = serviceSelect.value;
            const endpoint = `/api/${{service}}`;

            fetchBtn.disabled = true;
            fetchStatus.textContent = `Loading data from ${{endpoint}} ...`;

            try {{
                const response = await fetch(endpoint, {{
                    method: 'GET',
                    headers: {{ 'Accept': 'application/json' }}
                }});

                const payload = await response.json();

                if (!response.ok) {{
                    fetchStatus.textContent = `Failed (${{response.status}}) from ${{endpoint}}`;
                    dataPreview.textContent = JSON.stringify(payload, null, 2);
                    return;
                }}

                const count = Array.isArray(payload) ? payload.length : 1;
                fetchStatus.textContent = `Loaded ${{count}} record(s) from ${{endpoint}}`;
                dataPreview.textContent = JSON.stringify(payload, null, 2);
            }} catch (error) {{
                fetchStatus.textContent = `Request error: ${{error.message}}`;
                dataPreview.textContent = '[]';
            }} finally {{
                fetchBtn.disabled = false;
            }}
        }}

        function updateView() {{
            const service = serviceSelect.value;

            const docsPath = `/api/${{service}}/docs`;
            const crudBasePath = `/api/${{service}}`;
            const crudByIdPath = `${{crudBasePath}}/1`;

            docsUrl.textContent = `${{window.location.origin}}${{docsPath}}`;
            crudBaseUrl.textContent = `${{window.location.origin}}${{crudBasePath}}`;
            crudByIdUrl.textContent = `${{window.location.origin}}${{crudByIdPath}}`;
            openDocsBtn.href = docsPath;
            fetchStatus.textContent = 'Select a service and click Fetch Data.';
            dataPreview.textContent = '[]';
        }}

        serviceSelect.addEventListener('change', updateView);
        fetchBtn.addEventListener('click', fetchServiceData);
        updateView();
    </script>
</body>
</html>
""".replace("{SERVICE_RESOURCES}", str(SERVICE_RESOURCES).replace("'", '"'))


@app.get("/services")
def list_services() -> dict[str, str]:
    return SERVICE_BASE_URLS


@app.get("/api/{service_name}/docs", include_in_schema=False)
def service_docs(service_name: str) -> HTMLResponse:
    service_name = _normalize_service_name(service_name)
    if service_name not in SERVICE_BASE_URLS:
        raise HTTPException(status_code=404, detail="Unknown service")

    return _swagger_html(
        openapi_url=f"/api/{service_name}/openapi.json",
        title=f"{service_name.capitalize()} Service Docs via Gateway",
        selected_service=service_name,
    )


@app.get("/api/{service_name}/openapi.json", include_in_schema=False)
async def service_openapi(service_name: str, request: Request) -> Response:
    service_name = _normalize_service_name(service_name)
    base_url = SERVICE_BASE_URLS.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail="Unknown service")

    target_url = f"{base_url}/openapi.json"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            upstream_response = await client.get(target_url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{service_name} service is unavailable. Ensure it is running on {base_url}.",
        ) from exc

    response_headers = {}
    upstream_content_type = upstream_response.headers.get("content-type")
    if upstream_content_type:
        response_headers["content-type"] = upstream_content_type

    if upstream_response.status_code != 200:
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=response_headers,
        )

    # Ensure Swagger "Try it out" uses gateway-prefixed routes.
    try:
        openapi_doc = upstream_response.json()
    except ValueError:
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=response_headers,
        )

    openapi_doc["servers"] = [{"url": f"/api/{service_name}"}]

    return Response(
        content=json.dumps(openapi_doc),
        status_code=200,
        headers=response_headers,
    )


@app.api_route(
    "/api/{service_name}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy_root(service_name: str, request: Request) -> Response:
    return await proxy(service_name=service_name, path="", request=request)


@app.api_route(
    "/api/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy(service_name: str, path: str, request: Request) -> Response:
    service_name = _normalize_service_name(service_name)
    base_url = SERVICE_BASE_URLS.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail="Unknown service")

    target_path = _resolve_target_path(service_name, path)
    target_url = f"{base_url}/{target_path}"

    body = await request.body()
    
    # Prepare headers, excluding host to avoid conflicts
    headers = {}
    for header_name, header_value in request.headers.items():
        # Skip hop-by-hop headers
        if header_name.lower() not in ["host", "connection", "transfer-encoding", "content-length"]:
            headers[header_name] = header_value
    
    # Ensure content-type is present for POST/PUT/PATCH
    if request.method in ["POST", "PUT", "PATCH"] and "content-type" not in headers:
        headers["content-type"] = "application/json"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Build request kwargs
            request_kwargs = {
                "method": request.method,
                "url": target_url,
                "headers": headers,
            }
            
            # Only add params and content if they exist
            if request.query_params:
                request_kwargs["params"] = request.query_params
            if body:
                request_kwargs["content"] = body
            
            upstream_response = await client.request(**request_kwargs)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{service_name} service is unavailable. Ensure it is running on {base_url}.",
        ) from exc

    response_headers = {}
    upstream_content_type = upstream_response.headers.get("content-type")
    if upstream_content_type:
        response_headers["content-type"] = upstream_content_type

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )