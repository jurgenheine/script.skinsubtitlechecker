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