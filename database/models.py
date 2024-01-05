from sqlalchemy import String
from sqlalchemy import Double
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
    #tags: Mapped[str] = mapped_column(String(1000), nullable=True)
    #recognizedText: Mapped[str] = mapped_column(String(1000), nullable=True)

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
    

class DementiaRating(Base):
    __tablename__ = "dementiaRating"

    id: Mapped[int] = mapped_column(primary_key=True)
    chatId: Mapped[str] = mapped_column(String(64))
    userId: Mapped[str] = mapped_column(String(64))
    rating: Mapped[str] = mapped_column(Double())

    def __repr__(self) -> str:
        return f"DRating(chatId={self.chatId!r}, userId={self.userId!r}, rating={self.rating!r})"