def get_prompt(bot_request):
    return " ".join(str.lower(bot_request).split(" ")[1:])