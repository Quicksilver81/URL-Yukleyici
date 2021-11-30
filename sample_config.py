import os

class Config(object):

    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    
    # The Telegram API things
    # Get these values from my.telegram.org
    APP_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "")
    
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    
    # Update channel for Force Subscribe
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "")
    
    # Log Channel ID
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
   
    # Telegram maximum file upload size
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 2097152000

    # chunk size that should be used with requests
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    
    # default thumbnail to be used in the videos
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "")
    
    # proxy for accessing youtube-dl in GeoRestricted Areas
    # Get your own proxy from https://github.com/rg3/youtube-dl/issues/1091#issuecomment-230163061
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
    
    # maximum message length in Telegram
    MAX_MESSAGE_LENGTH = 4096
    
    # set timeout for subprocess
    PROCESS_MAX_TIMEOUT = 3600
    
    # watermark file
    DEF_WATER_MARK_FILE = ""
    
    # your telegram id
    OWNER_ID = int(os.environ.get("OWNER_ID", ""))
    
    # database session name, example: urluploader
    SESSION_NAME = os.environ.get("SESSION_NAME", "")
    
    # database uri (mongodb)
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    
    # Website referer
    REFERER = os.environ.get("REFERER", "")
    REFERER_URL = os.environ.get("REFERER_URL", "")
