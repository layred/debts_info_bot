import logging
import os
from base64 import b64decode
from io import BytesIO
from pathlib import Path, PosixPath
from typing import Union

import telebot
from apps.bot.models import TelegramUser
from apps.bot.utils import constants, markups, tools, txts  # noqa
from django.conf import settings
from telebot.apihelper import ApiTelegramException as TelegramException
from telebot.types import (CallbackQuery, InlineKeyboardMarkup, Message,
                           ReplyKeyboardMarkup)

logger = telebot.logger
fh = logging.FileHandler(os.path.join(settings.BASE_DIR, 'logs/bot_log.log'))
logger.addHandler(fh)


class BaseBot(telebot.TeleBot):

    def __init__(self, token, *args, **kwargs):
        self.DEBUG = settings.DEBUG
        self.BASE_DIR = Path(__file__).resolve().parent
        self.TEMPORARY_DIR = os.path.join(self.BASE_DIR, 'temporary_files')
        self.ADMIN_USER_ID = constants.ADMIN_USER_ID
        self.markups = markups.Markups()
        self.logger = logger
        super().__init__(token=token, parse_mode='html', threaded=False, *args, **kwargs)

    def send_admin_message(self, message_text: str) -> Message:
        return self.send(self.ADMIN_USER_ID, message_text)

    def download_file(self, message: Message, file_id: str = None) -> Path:
        if file_id is None:
            file_id = message.document.file_id
            file_name = message.document.file_name
        else:
            file_name = 'photo'
        downloaded_file = super().download_file(self.get_file(file_id).file_path)
        src = os.path.join(self.TEMPORARY_DIR, f'{message.from_user.id}_{file_name}')
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        return Path(src)

    def log_error(self, error: Exception, exc_info: bool = True):
        if hasattr(self, 'pill2kill'):
            self.stop_loading()
        if hasattr(self, 'loading_message') and self.loading_message is not None:
            self.delete(self.loading_message.chat.id, self.loading_message.id)
            self.loading_message = None
        self.logger.error(error, exc_info=exc_info)

    def send(self, chat_id: int, text: str,
             markup: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup] = None) -> Message:
        return super().send_message(chat_id, text, parse_mode='html', reply_markup=markup, disable_web_page_preview=True)

    def send_photo(self, chat_id: int, photo: Union[Path, str],
                   caption: str, markup: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup] = None) -> Message:
        if type(photo) is PosixPath or (type(photo) is str and photo.startswith('/')):
            return super().send_photo(chat_id, photo if type(photo) is str else open(photo, 'rb+'), caption=caption, parse_mode='html', reply_markup=markup)
        else:
            return super().send_photo(chat_id, BytesIO(b64decode(photo.encode('ascii'))), caption=caption, parse_mode='html', reply_markup=markup)

    def send_document(self, chat_id: int, path: Union[Path, PosixPath, str],
                      markup: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup] = None,
                      caption: str = None, file_name: str = None) -> Message:
        if type(path) is PosixPath or (type(path) is str and path.startswith('/')):
            return super().send_document(chat_id, open(path, 'rb'), reply_markup=markup, caption=caption, parse_mode='html', visible_file_name=file_name)
        else:
            return super().send_document(chat_id, BytesIO(b64decode(path.encode('ascii'))), reply_markup=markup, caption=caption, parse_mode='html', visible_file_name=file_name)

    def delete(self, chat_id: int, message_id: int) -> bool:
        try:
            return super().delete_message(chat_id, message_id)
        except TelegramException:
            pass

    def answer_call(self, call: CallbackQuery, *args, **kwargs):
        super().answer_callback_query(call.id, *args, **kwargs)

    def edit(self, message: Message, text: str, markup: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup] = None,
             position: int = 0, message_id: int = None):
        if message_id is not None:
            change_id = message_id
        else:
            change_id = message.id + position
        try:
            return super().edit_message_text(text, message.chat.id, change_id, parse_mode='html', reply_markup=markup, disable_web_page_preview=True)
        except TelegramException:
            pass

    def _delete_file(self, path: Union[Path, list, tuple]) -> None:
        if type(path) is list or type(path) is tuple:
            for file in path:
                os.remove(file)
        os.remove(path)


class Bot(BaseBot):

    def __init__(self, *kwargs) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        # self.set_my_commands(
        #     commands=[]
        # )
        super().__init__(token=self.token, *kwargs)

    def get_user(self, user_id: int) -> TelegramUser:
        """
            Возвращает объект пользователя телеграмма

            :return TelegramUser:
        """
        return TelegramUser.objects.get(user_id=user_id)

    def is_new_user(self, message: Message) -> bool:
        """
            Проверяет есть ли такой пользователь в базе данныъ

            :return bool:
        """
        return not TelegramUser.objects.filter(user_id=message.from_user.id).exists()

    def kick_user(self, user_id: int):
        """
            Если пользователь блокирует бота то ставит unactive в True
        """
        if isinstance(user_id, str) and user_id.is_digit():
            user_id = int(user_id)
        if TelegramUser.objects.filter(user_id=user_id).exists():
            user = TelegramUser.objects.get(user_id=user_id)
            user.unactive = True
            user.save()

    def register_new_user(self, message: Message) -> None:
        """
            Обрабатываем отправленный пользователем контает и создаем объект пользователя в базе данных
        """
        if not TelegramUser.objects.filter(user_id=message.contact.user_id).exists():
            TelegramUser.objects.create(user_id=message.contact.user_id, username=message.from_user.username, phone_number=message.contact.phone_number)
        self.send(message.chat.id, 'Теперь вы зарегистрированны в Джанго телеграмм боте!', self.markups._remove())

    def send_register_message(self, message: Message) -> Message:
        """
            Отправляет сообщение с клавиатурой для отправки контакта пользователем
        """
        return self.send(message.chat.id, '<b>Для регистрации в боте необходимо отправить контакт, если вы согласны, то нажмите на кнопку ниже⤵️</b>', self.markups.register())

    def send_welcome_message(self, message: Message) -> Message:
        """
            Отправляет привественное сообщение
        """
        return self.send(message.chat.id, txts.welcome_text, self.markups._remove())

    def toFixed(self, numObj, digits=2):
        obj_str = f'{numObj:.{digits}f}'
        if len(str(round(numObj))) == 8:
            return obj_str[1:2] + ' ' + obj_str[2:5] + ' ' + obj_str[5:]
        if len(str(round(numObj))) == 7:
            return obj_str[:1] + ' ' + obj_str[1:4] + ' ' + obj_str[4:]
        elif len(str(round(numObj))) == 6:
            return obj_str[:3] + ' ' + obj_str[3:]
        elif len(str(round(numObj))) == 5:
            return obj_str[:2] + ' ' + obj_str[2:]
        elif len(str(round(numObj))) == 4:
            return obj_str[:1] + ' ' + obj_str[1:]
        else:
            return obj_str

    def send_debt_notification(self, user: TelegramUser) -> Message:
        """
            Сообщение об задолжностях
        """
        chat_id = user.user_id
        message_text = '<b>Задолжности %s</b>\n\n' % user.username

        for i, creditor in enumerate(user.creditor_set.all()):
            message_text += '<i>%i. %s</i>\n' % (i+1, creditor.name)
            for credit in creditor.credit_set.all():
                percents = float(credit.get_percents())
                if percents == 0.00:
                    message_text += f'   <code>{credit.comment}</code> {self.toFixed(credit.amount)} ₽\n'
                else:
                    message_text += f'   <code>{credit.comment}:</code> <i>{self.toFixed(credit.amount)}+{self.toFixed(float(credit.get_percents()))}</i> = <b>{self.toFixed(float(credit.total_amount))}</b> ₽\n'
            message_text += '   <i>Всего: %s ₽</i>\n\n' % self.toFixed(float(creditor.total_debt()))

        message_text += '<i>Общая задолжность </i> <b>%s ₽</b>\n\n' % self.toFixed(user.get_total_credits())

        return self.send(chat_id, message_text)
