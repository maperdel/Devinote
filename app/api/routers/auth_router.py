from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import AuthServiceDependency
from app.models.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, auth_service: AuthServiceDependency):
    return auth_service.register(payload.email, payload.full_name, payload.password)


@router.post("/login")
def login(email: str, password: str, auth_service: AuthServiceDependency):
    token = auth_service.login(email, password)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token")
def login(
    auth_service: AuthServiceDependency, form: OAuth2PasswordRequestForm = Depends()
):
    # Es la misma funcion de login, pero esta nos sirve para swagger
    # Recibimos un formulario como parametro, esto es para que el usuario se pueda loggear en swagger
    email = form.username
    password = form.password
    token = auth_service.login(email, password)
    return {"access_token": token, "token_type": "bearer"}
