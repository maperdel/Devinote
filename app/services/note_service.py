from app.core import unit_of_work
from app.core import db_error_handler
from app.core.db_error_handler import handle_db_errors
from app.core.exceptions import InvalidCredentialsError, NotFoundError
from app.core.unit_of_work import UnitOfWork
from app.models.note import Note, NoteCreate, NoteUpdate
from app.models.shared import ShareRole
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.shared_repository import SharedRepository


class NoteService:
    def __init__(
        self,
        note_repo: NoteRepository,
        label_repo: LabelRepository,
        shared_repo: SharedRepository,
        unit_of_work: UnitOfWork,
    ):
        self.note_repo = note_repo
        self.label_repo = label_repo
        self.shared_repo = shared_repo
        self.unit_of_work = unit_of_work

    # PERMISOS
    def user_can_read(self, user_id: int, note: Note) -> bool:
        # ¿El usuario es dueño de la nota?
        if note.owner_id == user_id:
            return True

        # ¿A este usuario se le compartio la nota?
        if self.shared_repo.has_note_share(note_id=note.id, user_id=user_id):
            return True

        # Obtenemos las etiquetas de la nota y vemos si el usuario tiene permisos sobre las etiquetas
        label_ids = self.label_repo.list_label_ids_for_note(note_id=note.id)
        return self.shared_repo.has_any_label_share(
            label_ids=label_ids, user_id=user_id
        )

    def user_can_edit(self, user_id: int, note: Note) -> bool:
        if note.owner_id == user_id:
            return True
        if self.shared_repo.has_note_share(
            note_id=note.id, user_id=user_id, role=ShareRole.EDIT
        ):
            return True
        # Obtenemos las etiquetas de la nota y vemos si el usuario tiene permisos sobre las etiquetas
        label_ids = self.label_repo.list_label_ids_for_note(note_id=note.id)
        return self.shared_repo.has_any_label_share(
            label_ids=label_ids, user_id=user_id, role=ShareRole.EDIT
        )

    def list_visible(self, user_id: int) -> list[Note]:
        # Notas propias
        owned = self.note_repo.list_owned(owner_id=user_id)
        # Notas compartidas
        direct_ids = self.shared_repo.list_notes_shared(user_id=user_id)
        shared_label_ids = self.shared_repo.list_labels_shared(user_id=user_id)
        ids_by_label = self.label_repo.list_note_ids_by_label_ids(shared_label_ids)
        # Convertirmos las 2 listas en un set para eliminar duplicados
        total_ids = list(set(direct_ids + ids_by_label))
        shared = self.note_repo.list_by_ids(total_ids)

        # Convierto la lista de owned en diccionario
        combined_notes = {note.id: note for note in owned}

        # Agrega los id's que no esten repetidos de shared en combined_notes
        for note in shared:
            combined_notes.setdefault(note.id, note)

        # Se ordenan las notas del diccionario en forma descendente, pero solo se regresan los valores del dict en una lista
        return sorted(combined_notes.values(), key=lambda note: note.id, reverse=True)

    def create(self, owner_id: int, note_data: NoteCreate) -> Note:
        with handle_db_errors(self.unit_of_work):
            note = self.note_repo.create(
                Note(
                    owner_id=owner_id,
                    title=note_data.title,
                    content=note_data.content,
                    color=note_data.color,
                )
            )
            self.unit_of_work.flush()
            if note_data.label_ids:
                self._set_labels(owner_id, note.id, note_data.label_ids)
            self.unit_of_work.commit()
            self.unit_of_work.refresh(note)
            return note

    def _set_labels(self, owner_id: int, note_id: int, label_ids: list[int]) -> None:
        valid_label_ids = self.label_repo.list_ids_of_owner(owner_id, label_ids)
        self.note_repo.replace_labels(note_id, valid_label_ids)

    def update(self, user_id: int, note_id: int, note_data: NoteUpdate) -> Note:
        note = self.note_repo.get(note_id)
        if not note:
            raise NotFoundError("La nota no fue encontrada")
        if not self.user_can_edit(user_id, note):
            raise InvalidCredentialsError("Usuario no autorizado para editar nota")
        # Obtenemos la lista de ids asignados a esta nota
        label_ids = note_data.label_ids.copy() if note_data.label_ids else None

        # Copiamos los valores de un objeto a otro
        for key, value in note_data.__dict__.items():
            if hasattr(note, key) and value is not None:
                setattr(note, key, value)

        with handle_db_errors(self.unit_of_work):
            self.note_repo.update(note)
            self.unit_of_work.commit()
            if label_ids is not None:
                if note.owner_id != user_id:
                    raise InvalidCredentialsError(
                        "Usuario no autorizado para modificar etiquetas"
                    )
                self._set_labels(user_id, note_id, label_ids)
                self.unit_of_work.commit()
            self.unit_of_work.refresh(note)
            return note

    def delete(self, user_id: int, note_id: int) -> None:
        note = self.note_repo.get(note_id)
        if not note:
            raise NotFoundError("Nota no encontrada")
        if note.owner_id != user_id:
            raise InvalidCredentialsError(
                "El usuario no tiene permisos para borrar la nota"
            )

        with handle_db_errors(self.unit_of_work):
            self.note_repo.delete(note)
            self.unit_of_work.commit()
