from database.db_config import engine
from database.models import Image, Video
from sqlalchemy import select
from sqlalchemy.orm import Session

class DbAccessor:

    def __init__(self, engine) -> None:
        self.engine = engine

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
    
db_accessor = DbAccessor(engine)
