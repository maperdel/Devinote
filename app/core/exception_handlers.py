from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    AlreadyExistsError,
    DatabaseOperationError,
    IntegrityErrorExc,
    NotFoundError,
    InvalidCredentialsError,
)

# Manejador de excepciones global para las rutas


def registrer_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AlreadyExistsError)
    def handle_already_exists(request: Request, exc: AlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(NotFoundError)
    def handle_not_found(request: Request, exc: AlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidCredentialsError)
    def handle_not_found(request: Request, exc: AlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)}
        )

    @app.exception_handler(IntegrityErrorExc)
    def handle_integrity_error(request: Request, exc: IntegrityErrorExc):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(DatabaseOperationError)
    def handle_database_error(request: Request, exc: DatabaseOperationError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
