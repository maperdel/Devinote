from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth_router import router as router_auth
from app.api.routers.labels_router import router as router_labels
from app.api.routers.notes_router import router as router_notes
from app.api.routers.shares_router import router as router_shares
from app.core.config import settings
from app.core.db import init_db
from app.core.exception_handlers import registrer_exception_handlers

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

registrer_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_auth, prefix="/api/v1")
app.include_router(router_notes, prefix="/api/v1")
app.include_router(router_labels, prefix="/api/v1")
app.include_router(router_shares, prefix="/api/v1")
