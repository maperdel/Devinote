from turtle import onclick

from app.core.db_error_handler import handle_db_errors
from app.core.exceptions import InvalidCredentialsError, NotFoundError
from app.core.unit_of_work import UnitOfWork
from app.models.shared import LabelShare, NoteShare, ShareRole
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.shared_repository import SharedRepository


class SharedService:
    def __init__(
        self,
        shared_repo: SharedRepository,
        note_repo: NoteRepository,
        label_repo: LabelRepository,
        unit_of_work: UnitOfWork,
    ):
        self.shared_repo = shared_repo
        self.note_repo = note_repo
        self.label_repo = label_repo
        self.unit_of_work = unit_of_work

    def share_note(
        self, owner_id: int, note_id: int, target_user_id: int, role: ShareRole
    ) -> NoteShare:
        note = self.note_repo.get(note_id)

        if not note:
            raise NotFoundError("Nota no encontrada")

        if note.owner_id != owner_id:
            raise InvalidCredentialsError("Usuario sin permisos para compartir nota")

        with handle_db_errors(self.unit_of_work):
            share = self.shared_repo.upsert_note_share(note_id, target_user_id, role)
            self.unit_of_work.commit()
            self.unit_of_work.refresh(share)
            return share

    def unshare_note(self, owner_id: int, note_id: int, target_user_id: int) -> None:
        note = self.note_repo.get(note_id)

        if not note:
            raise NotFoundError("Nota no encontrada")

        if note.owner_id != owner_id:
            raise InvalidCredentialsError("Usuario sin permisos para la nota")

        with handle_db_errors(self.unit_of_work):
            self.shared_repo.remove_note_share(note_id, target_user_id)
            self.unit_of_work.commit()

    def share_label(
        self, owner_id: int, label_id: int, target_user_id: int, role: ShareRole
    ) -> LabelShare:
        label = self.label_repo.get(label_id)
        if not label:
            raise NotFoundError("Etiqueta no encontrada")
        if label.owner_id != owner_id:
            raise InvalidCredentialsError(
                "El usuario no tiene permiso sobre la etiqueta"
            )
        with handle_db_errors(self.unit_of_work):
            share = self.shared_repo.upsert_label_share(label_id, target_user_id, role)
            self.unit_of_work.commit()
            self.unit_of_work.refresh(share)
            return share

    def unshare_label(self, owner_id: int, label_id: int, target_user_id: int) -> None:
        label = self.label_repo.get(label_id)
        if not label:
            raise NotFoundError("Etiqueta no encontrada")

        if label.owner_id != owner_id:
            raise InvalidCredentialsError(
                "El usuario no tiene permiso sobre la etiqueta"
            )

        with handle_db_errors(self.unit_of_work):
            self.shared_repo.remove_label_share(label_id, target_user_id)
            self.unit_of_work.commit()
