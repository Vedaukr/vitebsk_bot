from bot.bot_instance.bot import bot_instance
from services.shazam_service import ShazamService, ShazamResult
import telebot, pydub, io
from bot.handlers.shared import download_file_from_telegram
from bot.handlers.shared import tg_exception_handler

AUDIO_MAX_LENGTH = 3*1000

shazam_service = ShazamService()

@bot_instance.message_handler(commands=['shazam_song'])
@tg_exception_handler
def handle_shazam(message: telebot.types.Message):
    file_id, file_name = handle_media_request(message)
    if file_id:
        audio_bytes = download_file_from_telegram(file_id)
        audio_extention = file_name.split('.')[-1]
        normalized_audio = normalize_audio(audio_bytes, audio_extention)
        track_info = shazam_service.recognize_song(normalized_audio)

        if track_info:
            bot_instance.reply_to(message, get_response_message(track_info))
        else:
            bot_instance.reply_to(message, "Nothing found")


def handle_media_request(message: telebot.types.Message) -> tuple[str, str]:
    if not message.reply_to_message:
        bot_instance.reply_to(message, "Use command as a reply to audio or video")
        return None, None
    
    if message.reply_to_message.audio:
        return message.reply_to_message.audio.file_id, message.reply_to_message.audio.file_name
    
    if message.reply_to_message.video:
        return message.reply_to_message.video.file_id, message.reply_to_message.video.file_name
    
    bot_instance.reply_to(message, "Nothing to recognize lol")
    return None, None

def normalize_audio(bytes: bytearray, extention: str) -> bytearray:
    input = io.BytesIO(bytes)
    audio = pydub.AudioSegment.from_file(input, format=extention)
    audio = audio[:AUDIO_MAX_LENGTH].set_channels(1)
    output = io.BytesIO()
    audio.export(output, format='s16le', bitrate='16k')
    return output.getvalue()

def get_response_message(info: ShazamResult) -> str:
    result = ""
    result += f"Found track info:\n{info.singer} - {info.title}\n"
    return result