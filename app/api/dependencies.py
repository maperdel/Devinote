from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_token
from app.core.unit_of_work import UnitOfWork
from app.models.user import User
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.shared_repository import SharedRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.label_service import LabelService
from app.services.note_service import NoteService
from app.services.shared_service import SharedService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

DBSession = Annotated[Session, Depends(get_session)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DBSession
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise credentials_exc
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise credentials_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# Regresa los repositorios creados, para que no lo tenga que construir la capa de servicio
def get_user_repo(db: DBSession) -> UserRepository:
    return UserRepository(db)


def get_label_repo(db: DBSession) -> LabelRepository:
    return LabelRepository(db)


def get_note_repo(db: DBSession) -> NoteRepository:
    return NoteRepository(db)


def get_shared_repo(db: DBSession) -> SharedRepository:
    return SharedRepository(db)


def get_unit_of_work(db: DBSession) -> UnitOfWork:
    return UnitOfWork(db)


# Regresa una instancia del serviciod, que a la vez reciben los repositorios como argumento
# Esto es para que los ruteadores no tengan la responsabilidad de construirlo
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> AuthService:
    return AuthService(user_repo, unit_of_work)


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def get_label_service(
    label_repo: LabelRepository = Depends(get_label_repo),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> LabelService:
    return LabelService(label_repo, unit_of_work)


LabelServiceDependency = Annotated[LabelService, Depends(get_label_service)]


# Todos estos objetos que necesitan una sesion de bd reciben la misma
def get_note_service(
    note_repo: NoteRepository = Depends(get_note_repo),
    label_repo: LabelRepository = Depends(get_label_repo),
    shared_repo: SharedRepository = Depends(get_shared_repo),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> NoteService:
    return NoteService(note_repo, label_repo, shared_repo, unit_of_work)


NoteServiceDependency = Annotated[NoteService, Depends(get_note_service)]


def get_shared_service(
    note_repo: NoteRepository = Depends(get_note_repo),
    label_repo: LabelRepository = Depends(get_label_repo),
    shared_repo: SharedRepository = Depends(get_shared_repo),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> SharedService:
    return SharedService(shared_repo, note_repo, label_repo, unit_of_work)


SharedServiceDependency = Annotated[SharedService, Depends(get_shared_service)]
