from utils.singleton import Singleton
from google.cloud import vision
from google.cloud import translate_v2 as translate

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

class LabelingService(metaclass=Singleton):
    def __init__(self):
        pass

    def get_labels(self, image_bytes: bytearray):
        image = vision.Image(content=image_bytes)
        response = vision_client.label_detection(image=image)
        return list(map(lambda l: l.description, response.label_annotations))

    def get_text(self, image_bytes: bytearray, target_languages=["ru", "en", "ua"]):
        image = vision.Image(content=image_bytes)
        image_context = {"language_hints": target_languages}
        response = vision_client.text_detection(image=image, image_context=image_context)
        return list(map(lambda l: l.description, response.text_annotations))
    
    def translate_text(self, text_list, target_language: str="ru"):
        translated_text = translate_client.translate(text_list, target_language=target_language)
        return list(map(lambda l: l["translatedText"], translated_text))