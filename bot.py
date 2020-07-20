from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from config import TG_Token
from detection import detect_face
import os
import json
import librosa
import soundfile as sf
import subprocess

# Хранить будем на диске
DATABASE_FILEPATH = './database.json'

users_data = {}
if os.path.exists(DATABASE_FILEPATH):
    with open(DATABASE_FILEPATH) as f:
        users_data = json.load(f)


def start(update, context):
    """Start command handler, create user in database"""
    user = update.message.from_user
    if user.id not in users_data.keys():
        users_data[user.id] = {'audio': [], 'photos': []}
    update.message.reply_text("I'm working, send me messages")


def take_photo(update, context):
    """Message handler for photos and detecting face"""
    photo = update.message.photo[-1].get_file()
    us_id = str(update.message.from_user.id)
    filepath = './photos/tmp' + str(us_id) + '.jpg'
    photo.download(filepath)
    if detect_face(filepath):
        count = len(users_data[us_id]['photos']) + 1
        saved_path = './photos/' + f'{us_id}_{count}' + '.jpg'
        os.rename(filepath, saved_path)
        users_data[us_id]['photos'].append(saved_path)
        save_base()
        update.message.reply_text(f'Face detected, photo saved as {us_id}_{count}.jpg')
    else:
        os.remove(filepath)
        update.message.reply_text("Photo hasn't got face. Discard")


def take_audio(update, context):
    """Message handler for voices"""
    sound = update.message.voice.get_file()
    us_id = str(update.message.from_user.id)
    count = len(users_data[us_id]['audio'])

    # Это часть кода которая должна конвертировать сообщения в wav с определенной частотой дискретизации
    # Однако у меня проблемы с либой для ogg, которую я физически не могу решить в данный момент
    """
    filepath = './voices/tmp' + str(us_id) + '.ogg'
    sound.download(filepath)
    saved_file = './voices/' + str(us_id) + f'audio_message_{count}.wav'
    data, samplerate = sf.read(filepath)
    sf.write(saved_file, data, 16000)
    """

    filepath = './voices/' + str(us_id) + f'audio_message_{count}.wav'
    sound.download(filepath)
    users_data[us_id]['audio'].append(filepath)
    save_base()
    update.message.reply_text(f'Voice message saved audio_message_{count}.wav')


def save_base():
    """ Dump database into json"""
    with open(DATABASE_FILEPATH, "w", encoding="utf-8") as file:
        json.dump(users_data, file)


updater = Updater(TG_Token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(filters=Filters.photo, callback=take_photo))
updater.dispatcher.add_handler(MessageHandler(filters=Filters.voice, callback=take_audio))

updater.start_polling()
updater.idle()
