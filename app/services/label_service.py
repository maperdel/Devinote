from httpx import delete

from app.core.db_error_handler import handle_db_errors
from app.core.exceptions import (
    AlreadyExistsError,
    InvalidCredentialsError,
    NotFoundError,
)
from app.core.unit_of_work import UnitOfWork
from app.models.label import Label, LabelCreate
from app.repositories.label_repository import LabelRepository


class LabelService:
    def __init__(self, label_repo: LabelRepository, unit_of_work: UnitOfWork):
        self.label_repo = label_repo
        self.unit_of_work = unit_of_work

    def list(self, owner_id: int) -> list[Label]:
        return self.label_repo.list_by_user(owner_id)

    def create(self, owner_id: int, payload: LabelCreate) -> Label:
        if self.label_repo.get_by_name(owner_id, payload.name):
            raise AlreadyExistsError("La etiqueta ya existe")

        with handle_db_errors(self.unit_of_work):
            label = self.label_repo.create(owner_id, payload.name)
            self.unit_of_work.commit()
            self.unit_of_work.refresh(label)
            return label

    def delete(self, owner_id: int, label_id: int) -> None:
        label = self.label_repo.get(label_id)
        if not label:
            raise NotFoundError("Etiqueta no encontrada")
        if label.owner_id != owner_id:
            raise InvalidCredentialsError(
                "El usuario no tiene permiso de borrar la etiqueta"
            )
        with handle_db_errors(self.unit_of_work):
            self.label_repo.delete(label)
            self.unit_of_work.commit()
