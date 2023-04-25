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
