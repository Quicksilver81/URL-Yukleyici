from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Translation(object):
    START_TEXT = """Merhaba {},
Ben bir URL Yükleyicisiyim!
Bu Botu kullanarak HTTP/HTTPS bağlantılarını yükleyebilirsiniz!"""
    FORMAT_SELECTION = "Formatı seçin <a href='{}'>dosya boyutu yaklaşık olabilir.</a>\n\nKapak fotoğrafı ayarlamak istiyorsanız, aşağıdaki düğmelerden herhangi birine dokunmadan önce veya hızlı bir şekilde fotoğraf gönderin.\n\nKapak fotoğrafını silmek için /delthumb kullanabilirsiniz."
    SET_CUSTOM_USERNAME_PASSWORD = """Video ismini değiştirmek istiyorsanız aşağıdaki formatı sağlayın:
URL | dosyaismi.mp4"""
    DOWNLOAD_START = "<b>Dosya Adı:</b> {}\n\nİndiriliyor.. 📥"
    UPLOAD_START = "Yükleniyor.."
    START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Destek', url='https://t.me/mmagneto'),
        InlineKeyboardButton('Kanal', url='https://t.me/anagrupp')
        ],[
        InlineKeyboardButton('Yardım Menüsü', callback_data='help')
        ]]
    )
    RCHD_TG_API_LIMIT = "{} saniye içinde İndirildi.\nAlgılanan Dosya Boyutu: {}\nÜzgünüm. Ancak, TELEGRAM API sınırlamaları nedeniyle 2GB'DEN büyük dosyaları yükleyemiyorum."
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "{} saniye içinde İndirildi.\n{} saniye içinde yüklendi.\n\n@mmagneto"
    SAVED_CUSTOM_THUMB_NAIL = "✔️ Video için kapak fotoğrafı kaydedildi. Bu görüntü video/dosya için kullanılacaktır."
    DEL_ETED_CUSTOM_THUMB_NAIL = "✔️ Kapak fotoğrafı başarıyla temizlendi."
    CUSTOM_CAPTION_UL_FILE = "{}"
    NO_VOID_FORMAT_FOUND = "HATA...\n<b>YouTubeDL</b>: {}"
    HELP_TEXT = """Nasıl kullanılırım? Aşağıdaki adımları izleyin!
    
1. URL gönderin.
2. Kapak fotoğrafı için fotoğraf gönderin. (İsteğe bağlı)
3. Buton seçin.
Bot cevap vermediyse @mmagneto ile iletişime geçin"""
    REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB = "Kapak fotoğrafı oluşturmak için bir fotoğrafa /genthumb komutunu yanıtlayın"
    ERR_ONLY_TWO_MEDIA_IN_ALBUM = """Albüm sadece iki fotoğraf içermelidir. Lütfen albümü yeniden gönderin ve tekrar deneyin veya bir albümde yalnızca iki adet fotoğraf gönderin."""
    CANCEL_STR = "İşlem İptal Edildi"
    SLOW_URL_DECED = "Dostum, çok yavaş bir URL gibi görünüyor."
