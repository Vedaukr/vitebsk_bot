from typing import Iterable
from database.models import Image, Video, DementiaRating
from sqlalchemy import select
from sqlalchemy.orm import Session
from utils.singleton import Singleton
from sqlalchemy import create_engine
from settings import SQLALCHEMY_DATABASE_URI

class DbAccessor(metaclass=Singleton):

    def __init__(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

    def add_image(self, image):
        with Session(self.engine) as session:
            session.add(image)
            session.commit()

    def add_video(self, video):
        with Session(self.engine) as session:
            session.add(video)
            session.commit()

    def update_drating(self, chatId, userId, rating):
        with Session(self.engine) as session:
            stmt = select(DementiaRating).where(DementiaRating.chatId.in_([chatId])).where(DementiaRating.userId.in_([userId]))
            res = list(session.scalars(stmt))
            if not res:
                drating = DementiaRating(chatId=chatId, userId=userId, rating=rating)
                session.add(drating)
            else:
                res[0].rating += rating
            stmt = select(DementiaRating)
            res = list(session.scalars(stmt))
            session.commit()
            
    def get_images_by_chat_id(self, chatId) -> Iterable[Image]:
        with Session(self.engine) as session:
            stmt = select(Image).where(Image.chatId.in_([chatId])).execution_options(stream_results=True)
            for image in session.scalars(stmt).yield_per(100):
                yield image

    def get_videos_by_chat_id(self, chatId):
        with Session(self.engine) as session:
            stmt = select(Video).where(Video.chatId.in_([chatId]))
            return list(session.scalars(stmt))
    
    def get_drating_by_chat_id(self, chatId):
        with Session(self.engine) as session:
            stmt = select(DementiaRating).where(DementiaRating.chatId.in_([chatId]))
            return list(session.scalars(stmt))
