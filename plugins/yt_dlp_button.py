import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import asyncio
import json
import math
import os
import shutil
import time
from datetime import datetime


# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram

from pyrogram.types import InputMediaPhoto
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots, get_thumbnail, get_duration, get_width_height


async def yt_dlp_call_back(bot, update):
    # LOGGER.info(update)
    cb_data = update.data

    tg_send_type, yt_dlp_format, yt_dlp_ext = cb_data.split("|")
    
    current_user_id = update.message.reply_to_message.from_user.id
    current_touched_user_id = update.from_user.id
    if current_user_id != current_touched_user_id:
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text="Hey seni tanımıyorum.",
            show_alert=True,
            cache_time=0,
        )
        return False, None

    thumb_image_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".jpg"
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except (FileNotFoundError) as e:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.message_id,
            revoke=True
        )
        return False
    #
    response_json = response_json[0]
    # TODO: temporary limitations
    # LOGGER.info(response_json)
    #
    yt_dlp_url = update.message.reply_to_message.text
    LOGGER.info(yt_dlp_url)
    #
    
    custom_file_name = str(response_json.get("title")) + \
        "_" + yt_dlp_format + "." + yt_dlp_ext
    LOGGER.info(custom_file_name)
    #
    await update.message.edit_caption(
        caption="İndiriliyor"
    )
    yt_dlp_username = None
    yt_dlp_password = None
    if "|" in yt_dlp_url:
        url_parts = yt_dlp_url.split("|")
        if len(url_parts) == 2:
            yt_dlp_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            yt_dlp_url = url_parts[0]
            custom_file_name = url_parts[1]
            yt_dlp_username = url_parts[2]
            yt_dlp_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    yt_dlp_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    yt_dlp_url = yt_dlp_url[o:o + l]
        if yt_dlp_url is not None:
            yt_dlp_url = yt_dlp_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        if yt_dlp_username is not None:
            yt_dlp_username = yt_dlp_username.strip()
        if yt_dlp_password is not None:
            yt_dlp_password = yt_dlp_password.strip()

    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                yt_dlp_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                yt_dlp_url = yt_dlp_url[o:o + l]
                
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]
          
    await bot.edit_message_text(
        text=Translation.DOWNLOAD_START.format(custom_file_name),
        chat_id=update.message.chat.id,
        parse_mode="html",
        message_id=update.message.message_id
    )
    
 
    tmp_directory_for_each_user = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(update.from_user.id)
    )
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user
    download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", yt_dlp_ext,
            "--audio-quality", yt_dlp_format,
            yt_dlp_url,
            "-o", download_directory
        ]
    else:
        for for_mat in response_json["formats"]:
            format_id = for_mat.get("format_id")
            if format_id == yt_dlp_format:
                acodec = for_mat.get("acodec")
                if acodec == "none":
                    yt_dlp_format += "+bestaudio"
                break

        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", yt_dlp_format,
            "--hls-prefer-ffmpeg", yt_dlp_url,
            "-o", download_directory
        ]
    #
    command_to_exec.append("--no-warnings")
    # command_to_exec.append("--quiet")
    command_to_exec.append("--restrict-filenames")
    #
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    if "hotstar" in yt_dlp_url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
    if "moly.cloud" in yt_dlp_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://vidmoly.to/")
    if "cdn.jwplayer.com" in yt_dlp_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://www.gain.tv/")
    if Config.REFERER in yt_dlp_url:
        command_to_exec.append("--referer")
        command_to_exec.append(f"https://{Config.REFERER_URL}/")
    if "closeload" in yt_dlp_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://closeload.com/")
    if yt_dlp_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(yt_dlp_username)
    if yt_dlp_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(yt_dlp_password)
    LOGGER.info(command_to_exec)
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    # LOGGER.info(e_response)
    # LOGGER.info(t_response)
    ad_string_to_replace = "please report this issue on https://github.com/yt-dlp/yt-dlp"
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await update.message.edit_caption(caption=error_message)
        return False, None
    if t_response:
        # LOGGER.info(t_response)
        os.remove(save_ytdl_json_path)
        end_one = datetime.now()
        time_taken_for_download = (end_one -start).seconds
        dir_contents = len(os.listdir(tmp_directory_for_each_user))
        # dir_contents.sort()
        await update.message.edit_caption(
            caption=f"{dir_contents} dosya bulundu."
        )
        user_id = update.from_user.id
        #
        file_size = Config.TG_MAX_FILE_SIZE + 1
        #
        LOGGER.info(tmp_directory_for_each_user)

        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                message_id=update.message.message_id
            )
        else:
            is_w_f = False
            images = await generate_screen_shots(
                download_directory,
                tmp_directory_for_each_user,
                is_w_f,
                Config.DEF_WATER_MARK_FILE,
                300,
                9
            )
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            # get the correct width, height, and duration for videos greater than 10MB
            width = 1280
            height = 720
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None:
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds

            if os.path.exists(thumb_image_path):
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if tg_send_type == "vm":
                    height = width
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                if tg_send_type == "file":
                    img.resize((320, height))
                else:
                    img.resize((90, height))
                img.save(thumb_image_path, "JPEG")  
                
            else:           
                 duration = get_duration(download_directory)
                 thumb_image_path = get_thumbnail(download_directory, tmp_directory_for_each_user, duration / 4)
            start_time = time.time()
            
            if tg_send_type == "audio":
                await update.message.reply_to_message.reply_chat_action("upload_audio")
                audio = await bot.send_audio(
                    chat_id=update.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
                audio_f = await audio.forward(Config.LOG_CHANNEL)
                await audio_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nKullanıcı ID: " + "<code>" + str(update.from_user.id) + "</code>" + "\nURL: " + yt_dlp_url)       
            elif tg_send_type == "file":
                await update.message.reply_to_message.reply_chat_action("upload_document")
                document = await bot.send_document(
                    chat_id=update.message.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    parse_mode="HTML",
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
                document_f = await document.forward(Config.LOG_CHANNEL)
                await document_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nKullanıcı ID: " + "<code>" + str(update.from_user.id) + "</code>" + "\nURL: " + yt_dlp_url)         
            elif tg_send_type == "vm":
                await update.message.reply_to_message.reply_chat_action("upload_video_note")
                video_note = await bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
                video_note_f = await video_note.forward(Config.LOG_CHANNEL)
                await video_note_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nKullanıcı ID: " + "<code>" + str(update.from_user.id) + "</code>" + "\nURL: " + yt_dlp_url)
            elif tg_send_type == "video":
                await update.message.reply_to_message.reply_chat_action("upload_video")
                video = await bot.send_video(
                    chat_id=update.message.chat.id,
                    video=download_directory,
                    caption=custom_file_name,
                    parse_mode="HTML",
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
                video_f = await video.forward(Config.LOG_CHANNEL)
                await video_f.reply_text("Ad: " + str(update.from_user.first_name) + "\nKullanıcı ID: " + "<code>" + str(update.from_user.id) + "</code>" + "\nURL: " + yt_dlp_url)
            else:
                LOGGER.info("Bu oldu mu? :\\")
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            #
            media_album_p = []
            if images is not None:
                i = 0
                caption = "© @torrentler"
                if is_w_f:
                    caption = "© @torrentler"
                for image in images:
                    if os.path.exists(str(image)):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode="html"
                                )
                            )
                        else:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await bot.send_media_group(
                chat_id=update.message.chat.id,
                disable_notification=True,
                reply_to_message_id=update.message.message_id,
                media=media_album_p
            )
            #
            try:
                shutil.rmtree(tmp_directory_for_each_user)   
            except:
                pass 
            try:
                os.remove(download_directory)
            except:
                pass
            try:
                os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                disable_web_page_preview=True
            )
