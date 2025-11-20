from fastapi import APIRouter, Query, Response
from fastapi.templating import Jinja2Templates
import importlib.resources as pkg_resources
import os

from settings import LocalSettings

router = APIRouter(prefix="/frontend", tags=["frontend"])

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
if not os.path.exists(TEMPLATE_DIR):
    # Try to find templates inside the installed package (pipx/pip install)
    try:
        TEMPLATE_DIR = str(pkg_resources.files("lightrag_exploration") / "templates")
    except Exception:
        pass
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/chat")
async def serve_chat():
    return templates.TemplateResponse("chat.html", {"request": {}})

@router.get("/rag-chat")
async def serve_rag_chat():
    return templates.TemplateResponse("rag-chat.html", {"request": {}})

@router.get("/graph-viewer")
async def serve_graph_viewer():
    return templates.TemplateResponse("graph_viewer.html", {"request": {}})

@router.get("/graphml")
async def serve_graphml():
    try:
        with open(
            f"{LocalSettings().research_output_dir}/graph_chunk_entity_relation.graphml",
            "r",
            encoding="utf-8",
        ) as f:
            graphml_content = f.read()
        return Response(content=graphml_content, media_type="application/xml")
    except Exception as e:
        return Response(
            content=f"Error loading GraphML file: {e}",
            media_type="text/plain",
            status_code=500,
        )


@router.get("/redirect")
async def redirect_page(
    target: str = Query(..., description="Target URL to redirect to")
):
    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta http-equiv='refresh' content='0; url={target}' />
        <title>Redirecting...</title>
    </head>
    <body>
        <p>Redirecting to <a href='{target}'>{target}</a>...</p>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")