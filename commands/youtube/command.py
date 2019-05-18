import logging
import os

import youtube_dl
from telegram import ChatAction
from telegram.error import NetworkError
from telegram.ext import CommandHandler

from updater import elbot
from utils.decorators import handle_empty_arg, send_recording_action
from utils.utils import send_message_to_admin

logger = logging.getLogger(__name__)

FILENAME = 'Audio_Cuervot'
VLC_LINK = 'https://play.google.com/store/apps/details?id=org.videolan.vlc'


@send_recording_action
@handle_empty_arg(required_params=('args',), error_message='Y la url del video? `/yttomp3 <url>`',
                  parse_mode='markdown')
@elbot.route(command='yttomp3', pass_args=True)
def youtube_to_mp3(bot, update, args):
    video_url = args[0]

    def ext(f):
        return f'bestaudio[ext={f}]'

    def format_extensions(extens):
        return '/'.join(map(ext, extens))

    try:
        extensions = ('mp3', '3gp', 'aac', 'wav', 'flac', 'm4a')
        ydl_opts = {
            'format': format_extensions(extensions),
            'outtmpl': f'{FILENAME}.%(ext)s',
        }
        logger.info(f'Starting download of {video_url}..')
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        logger.info(f'Video downloaded.')

    except Exception:
        logger.error('Audio not downloaded.', exc_info=True)
        update.message.reply_text(f'No audio found for {video_url}')
        return

    # Download was successful, now we must open the audio file
    try:
        logger.info('Reading audio file from local storage')
        file, filename = get_audio_file(extensions)
        update.message.reply_text(f'✅ Archivo descargado. Enviando...')
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)
        logger.info(f'Filename: {filename}')
        if file:
            logger.info('Sending file to user')
            update.message.reply_document(document=file)
            update.message.reply_text(f'💬 Tip: Podés usar [VLC]({VLC_LINK}) para reproducir el audio 🎶',
                                      parse_mode='markdown', disable_web_page_preview=True)
            file.close()
            logger.info('File sent successfully')
    except NetworkError:
        logger.error('A network error occurred.', exc_info=True)
        update.message.reply_text(text='🚀 Hay problemas de conexión en estos momentos. Intentá mas tarde..')
        send_message_to_admin(bot, f'Error mandando {video_url}, {filename}')

    except Exception:
        msg = 'Error uploading file to telegram servers'
        logger.exception(msg), send_message_to_admin(bot, msg)
        update.message.reply_text(text=msg)

    else:
        if filename:
            try:
                # Remove the file we just sent, as the name is hardcoded.
                logger.info(f"Removing file '{filename}'")
                os.remove(filename)
                logger.info('File removed')
            except FileNotFoundError:
                msg = f'Error removing audio file. File not found {filename}'
                logger.error(msg), send_message_to_admin(bot, msg)
            except Exception:
                msg = f"UnknownError removing audio file. '{filename}'"
                logger.error(msg), send_message_to_admin(bot, msg)


def get_audio_file(exts):
    """Youtube-dl does not return file data on success, so we must guess the file extension"""
    possible_filenames = (f"{FILENAME}.{ext}" for ext in exts)
    for filename in possible_filenames:
        try:
            return open(filename, 'rb'), filename
        except FileNotFoundError:
            continue

    return None, None
