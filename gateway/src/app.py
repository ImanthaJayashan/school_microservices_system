from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
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

SERVICE_RESOURCES: dict[str, str] = {
    "students": "students",
    "teachers": "teachers",
    "sports": "sports",
    "exams": "exams",
    "subjects": "subjects",
}


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
    </style>
</head>
<body>
    <main class="card">
        <section class="header">
            <h1>School API Gateway</h1>
            <p>Select a service to quickly open its Swagger docs or copy CRUD route templates through the gateway on port 8080.</p>
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
                Route format: /api/&lt;service&gt;/&lt;resource&gt; and /api/&lt;service&gt;/&lt;resource&gt;/&lt;id&gt;
            </p>
        </section>
    </main>

    <script>
        const serviceToResource = {SERVICE_RESOURCES};
        const serviceSelect = document.getElementById('serviceSelect');
        const docsUrl = document.getElementById('docsUrl');
        const crudBaseUrl = document.getElementById('crudBaseUrl');
        const crudByIdUrl = document.getElementById('crudByIdUrl');
        const openDocsBtn = document.getElementById('openDocsBtn');

        function updateView() {{
            const service = serviceSelect.value;
            const resource = serviceToResource[service];

            const docsPath = `/api/${{service}}/docs`;
            const crudBasePath = `/api/${{service}}/${{resource}}`;
            const crudByIdPath = `${{crudBasePath}}/1`;

            docsUrl.textContent = `${{window.location.origin}}${{docsPath}}`;
            crudBaseUrl.textContent = `${{window.location.origin}}${{crudBasePath}}`;
            crudByIdUrl.textContent = `${{window.location.origin}}${{crudByIdPath}}`;
            openDocsBtn.href = docsPath;
        }}

        serviceSelect.addEventListener('change', updateView);
        updateView();
    </script>
</body>
</html>
""".replace("{SERVICE_RESOURCES}", str(SERVICE_RESOURCES).replace("'", '"'))


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
