from fastapi import APIRouter, status

from app.api.dependencies import (
    CurrentUser,
    NoteServiceDependency,
    SharedServiceDependency,
)
from app.models.shared import ShareRequest
from app.services import label_service

router = APIRouter(prefix="/shares", tags=["Shares"])


@router.post("/notes/{note_id}", status_code=status.HTTP_201_CREATED)
def share_note(
    note_id: int,
    payload: ShareRequest,
    user: CurrentUser,
    share_service: SharedServiceDependency,
):
    share = share_service.share_note(
        user.id, note_id, payload.target_user_id, payload.role
    )
    return {
        "id": share.id,
        "note_id": note_id,
        "user_target_id": payload.target_user_id,
        "role": share.role,
    }


@router.delete("notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def unshare_note(
    note_id: int,
    target_user_id: int,
    user: CurrentUser,
    share_service: SharedServiceDependency,
):
    share_service.unshare_note(user.id, note_id, target_user_id)


@router.post("/labels/{label_id}", status_code=status.HTTP_201_CREATED)
def share_label(
    label_id: int,
    payload: ShareRequest,
    share_service: SharedServiceDependency,
    user: CurrentUser,
):
    share = share_service.share_label(
        user.id, label_id, payload.target_user_id, payload.role
    )
    return {
        "id": share.id,
        "note_id": label_id,
        "user_target_id": payload.target_user_id,
        "role": share.role,
    }


@router.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def unshare_label(
    label_id: int,
    target_user_id: int,
    user: CurrentUser,
    share_service: SharedServiceDependency,
):
    share_service.unshare_label(user.id, label_id, target_user_id)
