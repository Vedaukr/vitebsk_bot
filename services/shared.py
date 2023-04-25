from dataclasses import dataclass

@dataclass
class MediaInfo:
    msg_id: int
    author_id: str
    chat_id: int
    media_type: str
    media_bytes: bytearray
    tags: str = ""
    recognised_text: str = ""

    def is_video(self):
        return self.media_type == "video"

    def is_photo(self):
        return self.media_type == "photo"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]