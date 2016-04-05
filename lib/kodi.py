# -*- coding: utf-8 -*- 
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import unicodedata

__addon__ = xbmcaddon.Addon()
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__monitor__ = xbmc.Monitor()

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING
ISO_639_1 =xbmc.ISO_639_1
ISO_639_2 =xbmc.ISO_639_2
ENGLISH_NAME =xbmc.ENGLISH_NAME


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


def convert_language(language, format):
    return xbmc.convertLanguage(language,format)


def get_clean_movie_title(path, usefoldername=False):
    return xbmc.getCleanMovieTitle(path, usefoldername)


def get_condition_visibility(value):
    return xbmc.getCondVisibility(value)


def get_window(id):
    return xbmcgui.Window(id)


def get_info_label(name):
    return xbmc.getInfoLabel(name)


def abort_requested():
    return  __monitor__.abortRequested()


def sleep( time):
    xbmc.sleep(time)


def wait_for_abort(time):
    return __monitor__.waitForAbort(time)


def file_exists(path):
    return xbmcvfs.exists(path)


def mkdirs(path):
    try:
        xbmcvfs.mkdirs(path)
    except:
        os.mkdir(path)


def dirname(path):
    return os.path.dirname(path)


def execute_json_rpc(jsonrpccommand):
    return xbmc.executeJSONRPC(jsonrpccommand)