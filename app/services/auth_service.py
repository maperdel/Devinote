from fastapi import HTTPException

from app.core.db_error_handler import handle_db_errors
from app.core.exceptions import InvalidCredentialsError, AlreadyExistsError
from app.core.security import create_access_token, hash_password, verify_password
from app.core.unit_of_work import UnitOfWork
from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repo: UserRepository, unit_of_work: UnitOfWork):
        self.repo = repo
        self.unit_of_work = unit_of_work

    def register(self, email: str, fullname: str, password: str) -> User:
        if self.repo.get_by_email(email):
            raise AlreadyExistsError(f"Email {email} ya registrado")
        user = User(
            email=email, full_name=fullname, hashed_password=hash_password(password)
        )
        with handle_db_errors(self.unit_of_work):
            user = self.repo.create(user)
            self.unit_of_work.commit()
            self.unit_of_work.refresh(user)
            return user

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(plain=password, hashed=user.hashed_password):
            raise InvalidCredentialsError("Credenciales no validas")
        token = create_access_token({"sub": str(user.id)})
        return token
