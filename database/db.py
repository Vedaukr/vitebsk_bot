from database.models import Image, Video
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

    def get_images_by_chat_id(self, chatId):
        session = Session(self.engine)
        stmt = select(Image).where(Image.chatId.in_([chatId]))
        return session.scalars(stmt)
    

    def get_videos_by_chat_id(self, chatId):
        session = Session(self.engine)
        stmt = select(Video).where(Video.chatId.in_([chatId]))
        return session.scalars(stmt)
    
