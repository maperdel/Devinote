from os import stat

from fastapi import APIRouter, Depends, status

from app.api.dependencies import CurrentUser, NoteServiceDependency
from app.models.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(user: CurrentUser, note_service: NoteServiceDependency):
    return note_service.list_visible(user.id)


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    user: CurrentUser,
    note_service: NoteServiceDependency,
):
    return note_service.create(user.id, payload)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    user: CurrentUser,
    note_service: NoteServiceDependency,
):
    return note_service.update(user.id, note_id, payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, note_service: NoteServiceDependency, user: CurrentUser):
    note_service.delete(user.id, note_id)
