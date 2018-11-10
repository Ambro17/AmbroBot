from telegram.ext import CommandHandler

from commands.retro.retro import retro_add, show_retro_items, expire_retro

add_retro_item = CommandHandler('retro', retro_add, pass_args=True)
show_retro_details = CommandHandler('retroitems', show_retro_items)
expire_retro_command = CommandHandler('endretro', expire_retro)
