from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, LabelServiceDependency
from app.models.label import LabelCreate, LabelRead

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("/", response_model=list[LabelRead])
def list_labels(user: CurrentUser, label_service: LabelServiceDependency):
    return label_service.list(user.id)


@router.post("/", response_model=LabelRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: LabelCreate, user: CurrentUser, label_service: LabelServiceDependency
):
    return label_service.create(user.id, payload)


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(label_id: int, user: CurrentUser, label_service: LabelServiceDependency):
    label_service.delete(user.id, label_id)
