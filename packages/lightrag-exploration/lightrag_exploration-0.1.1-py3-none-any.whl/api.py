from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import importlib.resources as pkg_resources
import os

from fastapi.middleware.cors import CORSMiddleware
import logging

# local imports
from routers import rag_router, frontend_router, text_router

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(TEMPLATE_DIR):
    # Try to find templates inside the installed package (pipx/pip install)
    try:
        TEMPLATE_DIR = str(pkg_resources.files("lightrag_exploration") / "templates")
    except Exception:
        pass
templates = Jinja2Templates(directory=TEMPLATE_DIR)

app = FastAPI(
    title="lightrag-exploration-api",
    version="0.0.1",
    description="General API for the lightrag exploration demo.",
    contact={
        "email": "contact@jamestwose.com",
    }
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(frontend_router.router)
app.include_router(text_router.router)
app.include_router(rag_router.router)

@app.get("/")
async def root():
    return templates.TemplateResponse("home.html", {"request": {}})