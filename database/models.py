from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    phash: Mapped[str] = mapped_column(String(64))
    msgId: Mapped[str] = mapped_column(String(64))
    authorId: Mapped[str] = mapped_column(String(64))
    chatId: Mapped[str] = mapped_column(String(64))

    def __repr__(self) -> str:
        return f"Image(phash={self.phash!r}, msgId={self.msgId!r}, authorId={self.authorId!r}, chatId={self.chatId!r})"

class Video(Base):
    __tablename__ = "video"

    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(String(64))
    msgId: Mapped[str] = mapped_column(String(64))
    authorId: Mapped[str] = mapped_column(String(64))
    chatId: Mapped[str] = mapped_column(String(64))

    def __repr__(self) -> str:
        return f"Video(hash={self.phash!r}, msgId={self.msgId!r}, authorId={self.authorId!r}, chatId={self.chatId!r})"