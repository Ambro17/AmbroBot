import logging
import os

import youtube_dl

from utils.decorators import handle_empty_arg, sending_audio_action
from utils.utils import send_message_to_admin

logger = logging.getLogger(__name__)


@sending_audio_action
@handle_empty_arg(required_params=('args',), error_message='Y la url del video? `/yt2mp3 <url>`', parse_mode='markdown')
def youtube_to_mp3(bot, update, args):
    video_url = args[0]

    try:
        def ext(f):
            return f'bestaudio[ext={f}]'

        def format_extensions(extens):
            return '/'.join(map(ext, extens))

        extensions = ('m4a', 'mp3', '3gp', 'aac', 'wav', 'flac')
        ydl_opts = {
            'format': format_extensions(extensions),
            'outtmpl': 'Audio_AmbroBot.%(ext)s',  # TODO: Maybe include title in filename so we can save more than one.
            'noprogress': True,
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
        logger.debug('Reading audio file from local storage')
        file, filename = get_audio_file(extensions)
        logger.debug(f'Filename: {filename}')
        if file:
            logger.info('Sending file to user')
            update.message.reply_document(document=file)
            file.close()
            logger.info('File sent successfully')

    except Exception:
        msg = 'Error uploading file to telegram servers'
        logger.exception(msg), send_message_to_admin(bot, msg)
        update.message.reply_text(text=msg)

    else:
        if filename:
            try:
                # Remove the file we just sent, as the name is hardcoded.
                logger.debug(f"Removing file '{filename}'")
                os.remove(filename)
                logger.debug('File removed')
            except FileNotFoundError:
                msg = f'Error removing audio file. File not found {filename}'
                logger.error(msg), send_message_to_admin(bot, msg)
            except Exception:
                msg = f"UnknownError removing audio file. '{filename}'"
                logger.error(msg), send_message_to_admin(bot, msg)


def get_audio_file(exts):
    possible_filenames = (f"Audio_AmbroBot.{ext}" for ext in exts)
    for filename in possible_filenames:
        try:
            return open(filename, 'rb'), filename
        except FileNotFoundError:
            continue

    return None, None
