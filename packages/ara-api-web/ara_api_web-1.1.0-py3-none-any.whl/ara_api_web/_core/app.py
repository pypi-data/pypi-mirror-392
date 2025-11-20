from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ara_api_web._core.routers import health
from ara_api_web._core.routers.api import msp, navigation, vision
from ara_api_web._utils.config import STATIC_DIR


def create_app() -> FastAPI:
    app = FastAPI(
        title="ARA API Web Interface",
        description="REST API wrapper for ARA drone control system",
        version="1.1.0",  # ! HARD VERSION
        docs_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=health.router)
    app.include_router(router=msp.router)
    app.include_router(router=navigation.router)
    app.include_router(router=vision.router)

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    return app
