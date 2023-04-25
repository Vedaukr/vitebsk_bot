from utils.singleton import Singleton
from google.cloud import vision
from google.cloud import translate_v2 as translate

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

class LabelingService(metaclass=Singleton):
    def __init__(self):
        pass

    def get_labels(self, image_bytes: bytearray, target_language: str="ru"):
        image = vision.Image(content=image_bytes)
        response = vision_client.label_detection(image=image)
        labels = list(map(lambda l: l.description, response.label_annotations))
        translated_labels = translate_client.translate(labels, target_language=target_language)
        return list(map(lambda l: l["translatedText"], translated_labels))

    def get_text(self, image_bytes: bytearray, target_languages=["ru", "en", "ua"]):
        image = vision.Image(content=image_bytes)
        image_context = {"language_hints": target_languages}
        response = vision_client.text_detection(image=image, image_context=image_context)
        return list(map(lambda l: l.description, response.text_annotations))