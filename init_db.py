from utils.dupdetector import DupDetector
import json, os

base_path = "D:\\Dev\\Tg\\dup_content"
dd = DupDetector()
with open(os.path.join(base_path, "result_VID.json"), "r", encoding="utf8") as file:
    json_data = json.loads(file.read())
    chat_id = json_data["id"]
    images = list(filter(lambda m: "photo" in m and "from_id" in m, json_data["messages"]))
    count = 0
    for img in images:
        count += 1
        print(f"Importing {count}/{len(images)} image:")

        tg_info = {
            "msgId": img["id"],
            "authorId": img["from_id"],
            "chatId": chat_id,
        }

        with open(os.path.join(base_path, img["photo"]), "rb") as img_bytes:
            img_info = {
                "ext": img["photo"].split('.')[-1],
                "bytes": img_bytes.read()
            }

            dd.add_image(img_info, tg_info)

    videos = list(filter(lambda m: "media_type" in m and "from_id" in m and m["media_type"] == "video_file", json_data["messages"]))
    count = 0
    for vid in videos:
        count += 1
        print(f"Importing {count}/{len(videos)} video:")

        tg_info = {
            "msgId": vid["id"],
            "authorId": vid["from_id"],
            "chatId": chat_id,
        }

        with open(os.path.join(base_path, vid["file"]), "rb") as vid_file:
            dd.add_video(vid_file.read(), tg_info)
