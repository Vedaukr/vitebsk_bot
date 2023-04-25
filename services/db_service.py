from database.db import db_accessor
from database.models import Image, Video
from utils.dupdetector import DupDetector
from services.shared import Singleton, MediaInfo

class DbService(metaclass=Singleton):
    def __init__(self):
        self.dd = DupDetector()

    def save_media_to_db(self, media_info: MediaInfo):
        if media_info.is_photo():
            img_phash = str(self.dd.get_phash(media_info.media_bytes))
            image = Image(
                phash=img_phash,
                msgId=media_info.msg_id,
                chatId=media_info.chat_id,
                authorId=media_info.author_id,
            )
            db_accessor.add_image(image)

        if media_info.is_video():
            vid_hash = str(self.dd.get_hash(media_info.media_bytes))
            video = Video(
                hash=vid_hash,
                msgId=media_info.msg_id,
                chatId=media_info.chat_id,
                authorId=media_info.author_id,
            )
            db_accessor.add_video(video)
    
    def get_images_count(self, chat_id):
        return len(list(db_accessor.get_images_by_chat_id(chat_id)))
