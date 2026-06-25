from sqlmodel import Session, select, delete

from app.models.label import Label, NoteLabelLink
from app.models.shared import LabelShare


class LabelRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, owner_id: int) -> list[Label]:
        return self.db.exec(
            select(Label).where(Label.owner_id == owner_id).order_by(Label.name.asc())
        ).all()

    def get(self, label_id: int) -> Label | None:
        return self.db.get(Label, label_id)

    def get_by_name(self, owner_id: str, name: str) -> Label | None:
        return self.db.exec(
            select(Label).where(Label.name == name, Label.owner_id == owner_id)
        ).first()

    def create(self, owner_id: int, name: str) -> Label:
        label = Label(name=name, owner_id=owner_id)
        self.db.add(label)
        return label

    def delete(self, label: Label) -> None:
        self.db.exec(delete(NoteLabelLink).where(NoteLabelLink.label_id == label.id))
        self.db.exec(delete(LabelShare).where(LabelShare.label_id == label.id))

        self.db.delete(label)

    def list_ids_of_owner(self, owner_id: int, ids: list[int]) -> list[int]:
        return self.db.exec(
            select(Label.id).where(Label.owner_id == owner_id, Label.id.in_(set(ids)))
        ).all()

    def list_label_ids_for_note(self, note_id: int) -> list[int]:
        return self.db.exec(
            select(NoteLabelLink.label_id).where(NoteLabelLink.note_id == note_id)
        ).all()

    def list_note_ids_by_label_ids(self, label_ids: list[int]) -> list[int]:
        if not label_ids:
            return []
        return self.db.exec(
            select(NoteLabelLink.note_id).where(
                NoteLabelLink.label_id.in_(set(label_ids))
            )
        ).all()
