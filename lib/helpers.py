# -*- coding: utf-8 -*- 
import xbmc
import xbmcaddon
import unicodedata
from json import loads

__addon__ = xbmcaddon.Addon()
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING


def get_version():
    return __version__


def log(module, msg, level=xbmc.LOGDEBUG):
    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('%s [%s]: %s' % (__scriptname__, module, msg), level)
    except Exception as e:
        # noinspection PyBroadException
        try:
            xbmc.log('Logging Failure: %s' % e, level)
        except:
            pass  # just give up


def get_setting(name):
    return __addon__.getSetting(name)


def normalize_string(stri):
    return unicodedata.normalize(
         'NFKD', unicode(unicode(stri, 'utf-8'))
         ).encode('ascii', 'ignore')


def translate_path(path):
    return xbmc.translatePath(path).decode('utf-8')


def get_script_path():
    return __cwd__


def get_clean_movie_title(path, usefoldername=False):
    return xbmc.getCleanMovieTitle(path, usefoldername)


def get_kodi_setting(name):
    """
    Uses XBMC/Kodi JSON-RPC API to retrieve subtitles location settings values.
    """
    command = '''{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "Settings.GetSettingValue",
    "params": {
        "setting": "%s"
    }
}'''
    result = xbmc.executeJSONRPC(command % name)
    py = loads(result)
    if 'result' in py and 'value' in py['result']:
        return py['result']['value']
    else:
        raise ValueError


def get_ISO_639_2_B(iso_639_2_code):
        for x in LANGUAGES:
            if iso_639_2_code == x[2] or iso_639_2_code == x[3]:
                return x[2]


def get_ISO_639_2_T(iso_639_2_code):
        for x in LANGUAGES:
            if iso_639_2_code == x[2] or iso_639_2_code == x[3]:
                return x[3]


LANGUAGES = (

    # Full Language name[0]       ISO 639-1          ISO 639-2B             ISO 639-2T

    ("Albanian"                   , "sq",            "alb",                 "sqi"  ),
    ("Armenian"                   , "hy",            "arm",                 "hye"  ),
    ("Basque"                     , "eu",            "baq",                 "eus"  ),
    ("Burmese"                    , "my",            "bur",                 "mya"  ),
    ("Chinese"                    , "zh",            "chi",                 "zho"  ),
    ("Czech"                      , "cs",            "cze",                 "ces"  ),
    ("Dutch"                      , "nl",            "dut",                 "nld"  ),
    ("French"                     , "fr",            "fre",                 "fra"  ),
    ("Georgian"                   , "ka",            "geo",                 "kat"  ),
    ("German"                     , "de",            "ger",                 "deu"  ),
    ("Greek"                      , "el",            "gre",                 "ell"  ),
    ("Icelandic"                  , "is",            "ice",                 "isl"  ),
    ("Persian"                    , "fa",            "per",                 "fas"  ),
    ("Macedonian"                 , "mk",            "mac",                 "mkd"  ),
    ("Malay"                      , "ms",            "may",                 "msa"  ),
    ("Maori"                      , "mi",            "mao",                 "mri"  ),
    ("Romanian"                   , "ro",            "rum",                 "ron"  ),
    ("Slovak"                     , "sk",            "slo",                 "slk"  ),
    ("Tibetan"                    , "bo",            "tib",                 "bod"  ),
    ("Welsh"                      , "cy",            "wel",                 "cym"  ),
)