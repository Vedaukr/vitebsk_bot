from PIL import Image

import io
import hashlib
import imagehash

class DupDetector:

    def __init__(self, threshold=5) -> None:
        self.threshold = threshold

    def detect_image_duplicate(self, phash, images, dup_number=5):
        sim_arr = []
        for img in images:
            if len(sim_arr) >= dup_number:
                break

            img_phash = imagehash.hex_to_hash(img.phash)
            dist = imagehash.hex_to_hash(phash) - img_phash
            
            if dist < self.threshold:
                sim_arr.append({
                    "dist": dist,
                    "msgId": img.msgId
                })
        return sim_arr
    
    def detect_video_duplicate(self, hash, videos):
        for vid in videos:
            if vid.hash == hash:
                return [{
                    "dist": 0,
                    "msgId": vid.msgId
                }]
        return None
    
    def get_phash(self, image: bytearray):
        return str(imagehash.phash(Image.open(io.BytesIO(image))))
    
    def get_hash(self, video):
        return hashlib.sha512(video).hexdigest()