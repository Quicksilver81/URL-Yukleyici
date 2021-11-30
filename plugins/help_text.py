import os
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types.bots_and_keyboards import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant

@Client.on_message(filters.command(["start"]))
async def start(bot, update):
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await bot.delete_messages(
                 chat_id=update.chat.id,
                 message_ids=update.message_id,
                 revoke=True
               )
               return
        except UserNotParticipant:
            await update.reply_text(
                text="**Botu sadece kanal aboneleri kullanabilir.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Kanala Katil", url=f"https://t.me/{update_channel}")]
                ])
            )
            return
        except Exception:
            await update.reply_text("Ters giden bir şey mi var. @mmagneto ile iletişime geçin")
            return
        await update.reply_text(
            text=Translation.START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=Translation.START_BUTTONS
           )
