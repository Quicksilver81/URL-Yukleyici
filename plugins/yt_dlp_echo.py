import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import lk21, requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math
from PIL import Image

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

from pyrogram import Client, filters

from database import Database
from helper_funcs.display_progress import humanbytes
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from helper_funcs.help_uploadbot import DownLoadFile
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

db = Database(Config.DATABASE_URL, Config.SESSION_NAME)

@Client.on_message(filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "banned":
               await bot.delete_messages(
                 chat_id=update.chat.id,
                 message_ids=update.message_id,
                 revoke=True
               )
               return
        except UserNotParticipant:
            await update.reply_text(
                text="**Botu yalnızca kanal aboneleri kullanabilir.**",
                reply_markup=InlineKeyboardMarkup([
                    [ InlineKeyboardButton(text="Kanala Katıl", url=f"https://t.me/{update_channel}")]
              ])
            )
            return
        except Exception:
            await update.reply_text("Ters giden bir şey mi var. @thebans ile iletişime geçin")
            return
    if not await db.is_user_exist(update.chat.id):
        await db.add_user(update.chat.id)
    ban_status = await db.get_ban_status(update.chat.id)
    if ban_status['is_banned']:
      await update.reply_text(f"Sen yasaklısın dostum\n\nSebep: {ban_status['ban_reason']}")
      return
    await update.reply_chat_action("typing")
    send_message = await update.reply_text(text="İşleniyor...⏳", reply_to_message_id=update.message_id, quote=True)
    yt_dlp_username = None
    yt_dlp_password = None
    file_name = None
    url = update.text
    folder = f'./lk21/{update.from_user.id}/'
    bypass = ['zippyshare', 'hxfile', 'anonfiles', 'streamtape', 'antfiles']
    ext = tldextract.extract(url)
    if ext.domain in bypass:
        pablo = await update.reply_text('LK21 bağlantısı algılandı')
        time.sleep(2.5)
        if os.path.isdir(folder):
            await update.reply_text("Spam göndermeyin, önceki göreviniz bitene kadar bekleyin.")
            await pablo.delete()
            return
        os.makedirs(folder)
        await pablo.edit_text('İndiriliyor...')
        bypasser = lk21.Bypass()
        xurl = bypasser.bypass_url(url)
        if ' | ' in url:
            url_parts = url.split(' | ')
            url = url_parts[0]
            file_name = url_parts[1]
        else:
            if xurl.find('/'):
                urlname = xurl.rsplit('/', 1)[1]
            file_name = urllib.parse.unquote(urlname)
            if '+' in file_name:
                file_name = file_name.replace('+', ' ')
        dldir = f'{folder}{file_name}'
        r = requests.get(xurl, allow_redirects=True)
        open(dldir, 'wb').write(r.content)
        try:
            file = filetype.guess(dldir)
            xfiletype = file.mime
        except AttributeError:
            xfiletype = file_name
        if xfiletype in ['video/mp4', 'video/x-matroska', 'video/webm', 'audio/mpeg']:
            metadata = extractMetadata(createParser(dldir))
            if metadata is not None:
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
        await pablo.edit_text('Yükleniyor...')
        start_time = time.time()
        if xfiletype in ['video/mp4', 'video/x-matroska', 'video/webm']:
            video = await bot.send_video(
                chat_id=update.chat.id,
                video=dldir,
                caption=file_name,
                duration=duration,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    pablo,
                    start_time
                )
            )
            video_f = await video.forward(Config.LOG_CHANNEL)
            await video_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        elif xfiletype == 'audio/mpeg':
            audio = await bot.send_audio(
                chat_id=update.chat.id,
                audio=dldir,
                caption=file_name,
                duration=duration,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    pablo,
                    start_time
                )
            )
            audio_f = await audio.forward(Config.LOG_CHANNEL)
            await audio_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        else:
            doc = await bot.send_document(
                chat_id=update.chat.id,
                document=dldir,
                caption=file_name,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    pablo,
                    start_time
                )
            )
            doc_f = await doc.forward(Config.LOG_CHANNEL)
            await doc_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        await pablo.delete()
        shutil.rmtree(folder)
        return
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            yt_dlp_username = url_parts[2]
            yt_dlp_password = url_parts[3]
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if url is not None:
            url = url.strip()
        if file_name is not None:
            file_name = file_name.strip()
        # https://stackoverflow.com/a/761825/4723940
        if yt_dlp_username is not None:
            yt_dlp_username = yt_dlp_username.strip()
        if yt_dlp_password is not None:
            yt_dlp_password = yt_dlp_password.strip()
        logger.info(url)
        logger.info(file_name)
    else:
        for entity in update.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]
    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "--no-check-certificate",
            "-j",
            url,
            "--proxy", Config.HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "--no-check-certificate",
            "-j",
            url
        ]  
    if "moly.cloud" in url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://vidmoly.to/")
    if "closeload" in url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://closeload.com/")
    if "cdn.jwplayer.com" in url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://www.gain.tv/")
    if "mail.ru" in url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://my.mail.ru/")
    if Config.REFERER in url:
        command_to_exec.append("--referer")
        command_to_exec.append(f"https://{Config.REFERER_URL}/")
    if yt_dlp_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(yt_dlp_username)
    if yt_dlp_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(yt_dlp_password)
    logger.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    # logger.info(e_response)
    t_response = stdout.decode().strip()
    # logger.info(t_response)
    if e_response and "nonnumeric port" not in e_response:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = e_response.replace("please report this issue on https://github.com/yt-dlp/yt-dlp", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        await send_message.edit_text(
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            parse_mode="html",
            disable_web_page_preview=True
        )
        return False
    if t_response:
        await send_message.edit_text("Formatlar Ayıklanıyor...")
        # logger.info(t_response)
        x_reponse = t_response
        response_json = []
        if "\n" in x_reponse:
            for yu_r in x_reponse.split("\n"):
                response_json.append(json.loads(yu_r))
        else:
            response_json.append(json.loads(x_reponse))
        # response_json = json.loads(x_reponse)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        for current_r_json in response_json:

            duration = None
            if "duration" in current_r_json:
                duration = current_r_json["duration"]
            if "formats" in current_r_json:
                for formats in current_r_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    dipslay_str_uon = (
                        "🎬 "
                        + format_string
                        + " - "
                        + approx_file_size
                        + " "
                        + format_ext
                        + " "
                    )
                    cb_string_video = "{}|{}|{}".format("video", format_id, format_ext)
                    ikeyboard = []
                    if "instagram.com" in url:
                        if format_id == "source":
                            ikeyboard = [
                                InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8"),
                                )
                            ]
                    else:
                        if (
                            format_string is not None
                            and not "audio only" in format_string
                        ):
                            ikeyboard = [
                                InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8"),
                                )
                            ]
                        else:
                            # special weird case :\
                            ikeyboard = [
                                InlineKeyboardButton(
                                    "🎞️ SVideo [" + "] ( " + approx_file_size + " )",
                                    callback_data=(cb_string_video).encode("UTF-8"),
                                )
                            ]
                    inline_keyboard.append(ikeyboard)
                if duration is not None:
                    cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                    cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                    cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                    inline_keyboard.append(
                        [
                            InlineKeyboardButton(
                                "🎵 MP3 " + "(" + "64 kbps" + ")",
                                callback_data=cb_string_64.encode("UTF-8"),
                            ),
                            InlineKeyboardButton(
                                "🎵 MP3 " + "(" + "128 kbps" + ")",
                                callback_data=cb_string_128.encode("UTF-8"),
                            ),
                        ]
                    )
                    inline_keyboard.append(
                        [
                            InlineKeyboardButton(
                                "🎵 MP3 " + "(" + "320 kbps" + ")",
                                callback_data=cb_string.encode("UTF-8"),
                            )
                        ]
                    )
            else:
                format_id = current_r_json["format_id"]
                format_ext = current_r_json["ext"]
                cb_string_video = "{}|{}|{}".format("video", format_id, format_ext)
                inline_keyboard.append(
                    [
                        InlineKeyboardButton(
                            "🎞️ SVideo", callback_data=(cb_string_video).encode("UTF-8")
                        )
                    ]
                )
            break
        inline_keyboard.append([InlineKeyboardButton("✖️ Kapat",callback_data="close")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        # logger.info(reply_markup)
        thumbnail = Config.DEF_THUMB_NAIL_VID_S
        thumbnail_image = Config.DEF_THUMB_NAIL_VID_S
    
        if "thumbnail" in current_r_json:
            if current_r_json["thumbnail"] is not None:
                thumbnail = current_r_json["thumbnail"]
                thumbnail_image = current_r_json["thumbnail"]
        thumb_image_path = DownLoadFile(
            thumbnail_image,
            Config.DOWNLOAD_LOCATION + "/" +
            str(update.from_user.id) + ".webp",
            Config.CHUNK_SIZE,
            None,  # bot,
            Translation.DOWNLOAD_START,
            update.message_id,
            update.chat.id
        )
                
        if os.path.exists(thumb_image_path):
            im = Image.open(thumb_image_path).convert("RGB")
            im.save(thumb_image_path.replace(".webp", ".jpg"), "jpeg")
        else:
            thumb_image_path = None
            
        await send_message.edit_text(
            text=Translation.FORMAT_SELECTION.format(thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            parse_mode="html"
        )


@Client.on_message(filters.private & filters.command('lkdeldir'))
async def lkdeldir(bot, update):
    shutil.rmtree(f'./lk21/{update.from_user.id}')
    await update.reply_text(f'**{update.from_user.first_name}** lk21 dizini silindi')
