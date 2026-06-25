from sqlmodel import SQLModel, Field


class Note(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str = ""
    color: str | None = None
    owner_id: int = Field(foreign_key="user.id", index=True)


class NoteCreate(SQLModel):
    title: str
    content: str = ""
    color: str | None = None
    label_ids: list[int] | None = None


class NoteUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    color: str | None = None
    label_ids: list[int] | None = None


class NoteRead(SQLModel):
    id: int
    title: str
    content: str
    color: str | None
    model_config = {"from_attributes": True}
