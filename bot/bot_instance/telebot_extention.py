import types
from typing import Iterable, List, Optional, Union
import telebot

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

class TelebotExt(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def edit_message_text(
            self, 
            text: str, 
            chat_id: Optional[Union[int, str]]=None, 
            message_id: Optional[int]=None, 
            inline_message_id: Optional[str]=None, 
            parse_mode: Optional[str]=None,
            entities: Optional[List[telebot.types.MessageEntity]]=None,
            disable_web_page_preview: Optional[bool]=None,
            reply_markup: Optional[telebot.types.InlineKeyboardMarkup]=None) -> Union[telebot.types.Message, bool]:
        
        all_parts = list(self._split_txt(text=text))

        for index, item in enumerate(all_parts):
            if index == 0:
                res = super().edit_message_text(text=item, 
                    chat_id=chat_id, 
                    message_id=message_id, 
                    inline_message_id=inline_message_id, 
                    parse_mode=parse_mode,
                    entities=entities,
                    disable_web_page_preview=disable_web_page_preview,
                    reply_markup=reply_markup)
            else:
                res = super().reply_to(text=item, 
                                       message=res, 
                                       disable_web_page_preview=disable_web_page_preview,
                                       parse_mode=parse_mode)
        
        return res
   
    def send_message(
            self, chat_id: Union[int, str], text: str, 
            parse_mode: Optional[str]=None, 
            entities: Optional[List[telebot.types.MessageEntity]]=None,
            disable_web_page_preview: Optional[bool]=None, 
            disable_notification: Optional[bool]=None, 
            protect_content: Optional[bool]=None,
            reply_to_message_id: Optional[int]=None, 
            allow_sending_without_reply: Optional[bool]=None,
            reply_markup: Optional[telebot.types.InlineKeyboardMarkup]=None,
            timeout: Optional[int]=None,
            message_thread_id: Optional[int]=None) -> telebot.types.Message:
        
        for txt_part in self._split_txt(text=text):
            res = super().send_message(text=txt_part, 
                chat_id=chat_id, 
                parse_mode=parse_mode,
                entities=entities,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification, 
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id, 
                allow_sending_without_reply=allow_sending_without_reply,
                reply_markup=reply_markup,
                timeout=timeout,
                message_thread_id=message_thread_id)
        
        return res
    
    def reply_to(self, message: telebot.types.Message, text: str, **kwargs) -> telebot.types.Message:
        for txt_part in self._split_txt(text=text):
            res = super().reply_to(message=message, text=txt_part, **kwargs)
        return res
    
    @staticmethod
    def _split_txt(text: str) -> Iterable[str]:
        if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
            return [text]
        try:
            return TelebotExt._split_nicely(text)
        except Exception as e:
            return TelebotExt._split_naively(text)
    
    @staticmethod
    def _split_naively(text: str) -> Iterable[str]:
        for i in range(0, len(text), TELEGRAM_MAX_MESSAGE_LENGTH):
            yield text[i:i + TELEGRAM_MAX_MESSAGE_LENGTH] 
    
    @staticmethod
    def _split_nicely(text: str) -> Iterable[str]:
        def split_and_leave_separator(sep: str, string: str):
            if sep == '':
                return list(string)
            
            return [f"{chunk}{sep}" for chunk in string.split(sep)]
            
        char_split_order = ('\n', ' ', '')
        str_chunks = split_and_leave_separator(char_split_order[0], text)
        big_chunks_map = {} # index to chunk map

        for sep in char_split_order[1:]:
            big_chunks_map = {
                index: split_and_leave_separator(sep, chunk) 
                for index, chunk in enumerate(str_chunks) 
                if len(chunk) > TELEGRAM_MAX_MESSAGE_LENGTH
            }
            if not big_chunks_map:
                break
            
            new_str_chunks = []
            for index, chunk in enumerate(str_chunks):
                if index in big_chunks_map:
                    new_str_chunks.extend(big_chunks_map[index])
                else:
                    new_str_chunks.append(chunk)
            str_chunks = new_str_chunks

        # Merge chunks
        res_chunks = []
        prev_accum_str = ""
        accum_str = ""

        for chunk in str_chunks:
            accum_str += chunk
            if len(accum_str) > TELEGRAM_MAX_MESSAGE_LENGTH:
                res_chunks.append(prev_accum_str)
                prev_accum_str = accum_str = chunk
                continue
            prev_accum_str = accum_str
        
        res_chunks.append(accum_str)
        return res_chunks

        