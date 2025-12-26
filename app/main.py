from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db, close_db
from app.config import get_settings
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title = settings.API_TITLE,
        version = settings.API_VERSION,
        description = settings.API_DESCRIPTION,
        lifespan = lifespan,
        docs_url = '/docs',
        redoc_url = '/redoc'
    )
    app.include_router(router)

    @app.get('/health')
    async def health_check():
        return {'status': 'healthy', 'version': settings.API_VERSION}

    @app.get('/')
    async def root():
        return {
            'message': 'aaa',
            'version': settings.API_VERSION,
            'docs': '/docs'
        }
    return app


app = create_app()