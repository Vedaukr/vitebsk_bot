from bot.bot_instance.bot import bot_instance
from services.db_service import DbService
from bot.handlers.shared import tg_exception_handler
import telebot

from utils.md_utils import escape_markdown

db_service = DbService()

@bot_instance.message_handler(commands=['ping'])
@tg_exception_handler
def handle_ping(message: telebot.types.Message):
    bot_instance.reply_to(message, "Alive")

@bot_instance.message_handler(commands=['get_img_count'])
@tg_exception_handler
def handle_image_count(message: telebot.types.Message):
    bot_instance.reply_to(message, db_service.get_images_count(str(message.chat.id)))

@bot_instance.message_handler(commands=['test_exception_handling'])
@tg_exception_handler
def handle_image_count(message: telebot.types.Message):
    raise Exception("Exception")

TEST_MSG = """To split a string by line breaks in Python, you can use the `splitlines()` method. This method splits the string at line breaks and returns a list of lines. Here’s an example:\n\n```python\ntext = \"\"\"This is line one\nThis is line two\nThis is line three\"\"\"\n\n# Split the text by line breaks\nlines = text.splitlines()\n\n# Printing the result\nfor i, line in enumerate(lines):\n    print(f"Line {i+1}: {line}")\n```\n\nAdditionally, if you need to consider different types of newline characters (`\\n`, `\\r\\n`, or `\\r`), `splitlines()` handles those automatically.\n\nIf you prefer using `split(\'\\n\')` or need to handle a specific newline character manually, you can do so as well:\n\n```python\ntext = "This is line one\\nThis is line two\\nThis is line three"\n\n# Split the text by \'\\n\'\nlines = text.split(\'\\n\')\n\n# Printing the result\nfor i, line in enumerate(lines):\n    print(f"Line {i+1}: {line}")\n```\n\nBoth methods will give you similar results for typical cases where lines are separated by standard newline characters. The first method is more versatile as it automatically adapts to different types of newlines."""

@bot_instance.message_handler(commands=['test'])
@tg_exception_handler
def handle_image_count(message: telebot.types.Message):
    test_msg = "0"*5000
    test_msg  = f"{test_msg} \n*TEST MARKDOWN*"
    test = bot_instance.send_message(message.chat.id, "wo md")
    test = bot_instance.send_message(message.chat.id, TEST_MSG)
    test = bot_instance.send_message(message.chat.id, "with md")
    test = bot_instance.send_message(message.chat.id, escape_markdown(TEST_MSG), parse_mode="MarkdownV2")
    #bot_instance.edit_message_text(test_msg, chat_id=message.chat.id, message_id=test.message_id, parse_mode="MarkdownV2")

