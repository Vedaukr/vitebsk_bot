from database.db_config import engine
from database.db import DbAccessor
from PIL import Image

import io
import hashlib
import imagehash

class DupDetector:

    def __init__(self, threshold=10) -> None:
        self.threshold = threshold
        self.db_acc = DbAccessor(engine)

    def get_img_count(self, chat_id):
        return len(list(self.db_acc.get_images_by_chat_id(chat_id)))

    def detect_duplicate(self, img_info, tg_info, dup_number=3):
        phash = self.get_phash(img_info)
        images = self.db_acc.get_images_by_chat_id(tg_info["chatId"])
        sim_arr = []
        for img in images:
            if len(sim_arr) >= dup_number:
                break

            img_phash = imagehash.hex_to_hash(img.phash)
            dist = phash - img_phash
            
            if dist < self.threshold:
                sim_arr.append({
                    "dist": dist,
                    "msgId": img.msgId
                })
        return sim_arr
    
    def detect_video_duplicate(self, video, tg_info):
        hash = self.get_hash(video)
        videos = self.db_acc.get_videos_by_chat_id(tg_info["chatId"])
        for vid in videos:
            if vid.hash == hash:
                return {
                    "dist": 0,
                    "msgId": vid.msgId
                }
        return None
    
    def add_image(self, img_info, tg_info):
        phash = self.get_phash(img_info)
        self.db_acc.add_image(
            phash=str(phash),
            msgId=tg_info["msgId"],
            chatId=tg_info["chatId"],
            authorId=tg_info["authorId"],
        )
    
    def add_video(self, video, tg_info):
        hash = self.get_hash(video)
        self.db_acc.add_video(
            hash=hash,
            msgId=tg_info["msgId"],
            chatId=tg_info["chatId"],
            authorId=tg_info["authorId"],
        )
        
    def get_phash(self, img_info):
        image = Image.open(io.BytesIO(img_info["bytes"]))
        return imagehash.phash(image)
    
    def get_hash(self, video):
        return hashlib.sha512(video).hexdigest()