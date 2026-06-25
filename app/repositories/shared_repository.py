from sqlmodel import Session, select

from app.models.shared import LabelShare, NoteShare, ShareRole


class SharedRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_note_share(
        self, note_id: int, user_id: int, role: ShareRole
    ) -> NoteShare:
        share = self.db.exec(
            select(NoteShare).where(
                NoteShare.user_id == user_id, NoteShare.note_id == note_id
            )
        ).first()
        if share:
            share.role = role
        else:
            share = NoteShare(note_id=note_id, user_id=user_id, role=role)

        self.db.add(share)
        return share

    def remove_note_share(self, note_id: int, user_id: int) -> None:
        share = self.db.exec(
            select(NoteShare).where(
                NoteShare.user_id == user_id, NoteShare.note_id == note_id
            )
        ).first()
        if share:
            self.db.delete(share)

    def upsert_label_share(
        self, label_id: int, user_id: int, role: ShareRole
    ) -> LabelShare:
        share = self.db.exec(
            select(LabelShare).where(
                LabelShare.label_id == label_id, LabelShare.user_id == user_id
            )
        ).first()
        if share:
            share.role = role
        else:
            share = LabelShare(label_id=label_id, user_id=user_id, role=role)
        self.db.add(share)
        return share

    def remove_label_share(self, label_id: int, user_id: int) -> None:
        share = self.db.exec(
            select(LabelShare).where(
                LabelShare.label_id == label_id, LabelShare.user_id == user_id
            )
        ).first()
        if share:
            self.db.delete(share)

    def has_note_share(
        self, note_id: int, user_id: int, role: ShareRole | None = None
    ) -> bool:
        query = select(NoteShare).where(
            NoteShare.note_id == note_id, NoteShare.user_id == user_id
        )
        if role is not None:
            query = query.where(NoteShare.role == role)
        return self.db.exec(query).first() is not None

    def has_any_label_share(
        self, label_ids: list[int], user_id: int, role: ShareRole | None = None
    ) -> bool:

        if not label_ids:
            return False
        query = select(LabelShare).where(
            LabelShare.user_id == user_id, LabelShare.label_id.in_(label_ids)
        )
        if role is not None:
            query = query.where(LabelShare.role == role)

        return self.db.exec(query).first() is not None

    def list_notes_shared(self, user_id: int) -> list[int]:
        query = select(NoteShare.note_id).where(NoteShare.user_id == user_id)
        return self.db.exec(query).all()

    def list_labels_shared(self, user_id: int) -> list[int]:
        query = select(LabelShare.label_id).where(LabelShare.user_id == user_id)
        return self.db.exec(query).all()
