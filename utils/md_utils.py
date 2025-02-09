import re

# Stolen from https://github.com/python-telegram-bot/python-telegram-bot/blob/1fdaaac8094c9d76c34c8c8e8c9add16080e75e7/telegram/utils/helpers.py#L149-L174
def escape_markdown(text: str, entity_type: str = None) -> str:
    if entity_type in ['pre', 'code']:
        escape_chars = r'\\_[]()~>#+-=|{}.!'
    elif entity_type == 'text_link':
        escape_chars = r'\)'
    else:
        escape_chars = r'\\_*[]()~`>#+-=|{}.!'

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def get_md_link(link_text: str, link_url: str) -> str:
    return f"[{escape_markdown(link_text)}]({escape_markdown(link_url)})"