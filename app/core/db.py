import os
from typing import Iterator

from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# PAra Render
raw_url = os.environ["DATABASE_URL"]
url = raw_url

if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://") :]
elif url.startswith("postgresql://") and "+psycopg" not in url:
    url = "postgresql+psycopg://" + url[len("postgresql://") :]

# engine = create_engine(
#     settings.DATABASE_URL,
#     echo=True,
#     connect_args=(
#         {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
#     ),
# )

engine = create_engine(url, pool_pre_ping=True)


def init_db() -> None:
    if settings.ENVIRONMENT == "DEV":
        SQLModel.metadata.create_all(
            engine
        )  # Solo para desarrollo, creacion de bd y tablas


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
