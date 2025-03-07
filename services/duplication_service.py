from database.db import DbAccessor
from utils.dupdetector import DupDetector
from services.shared import MediaInfo
from utils.singleton import Singleton

class DuplicationService(metaclass=Singleton):
    def __init__(self):
        # chat_id -> msg_id -> media_info
        self.media_map = {}
        self.dd = DupDetector()
        self.db_accessor = DbAccessor()
    
    def detect_media_duplicates(self, media_info: MediaInfo):
        self.add_to_map(media_info)
        if media_info.is_photo():
            images = self.db_accessor.get_images_by_chat_id(media_info.chat_id)
            return self.dd.detect_image_duplicate(media_info.media_hash, images)

        if media_info.is_video():
            videos = self.db_accessor.get_videos_by_chat_id(media_info.chat_id)
            return self.dd.detect_video_duplicate(media_info.media_hash, videos)

    def add_to_map(self, media_info: MediaInfo):
        if not media_info.chat_id in self.media_map:
            self.media_map[media_info.chat_id] = {}
        self.media_map[media_info.chat_id][media_info.msg_id] = media_info

    def get_media(self, chat_id, msg_id):
        return self.media_map[chat_id][msg_id]
    
    def delete_media(self, media_info: MediaInfo):
        del self.media_map[media_info.chat_id][media_info.msg_id]


