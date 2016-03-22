# -*- coding: UTF-8 -*-

import sys
from operator import itemgetter
from scrapers.open_subtitles import OSDBServer
from scrapers.addic7ed import Adic7edServer
from scrapers.podnapisi import PNServer
from lib import kodi
from lib.db_utils import DBConnection
from lib.setting import Setting
from lib.language import Language
from lib.videogui import VideoGui
from lib.videoitem import VideoItem

#import ptvsd
#ptvsd.enable_attach(secret='my_secret')
class SubtitleChecker:
    def __init__(self):
        kodi.log(__name__, "version %s started" % kodi.get_version(), kodi.LOGNOTICE)
        self._init_vars()
        self._parse_argv() 
            
    def __enter__(self):
        return self

    def _init_vars(self):
        self.settings = Setting()
        self.language = Language()
        self.videogui = VideoGui()
        self.videoitem = VideoItem()
        self.stop = False
        self.db = None
    
    @staticmethod
    def _get_params():
        kodi.log(__name__, "params: %s" % sys.argv[1])
        param = {}
        paramstring = sys.argv[1]
        if len(paramstring) >= 2:
            params = paramstring
            cleanedparams = params.replace('?', '')
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]

        return param

    def _parse_argv(self):
        self.params = self._get_params()
        kodi.log(__name__, "params: %s" % self.params)
        self.backend = self.params.get('backend', False)
        self.flush_cache = self.params.get('flushcache', False)
        self.present_text = self.params.get('availabereturnvalue', '')
        self.not_present_text = self.params.get('notavailablereturnvalue', '')
        self.search_text = self.params.get('searchreturnvalue', '')

    def execute(self):
        # don't run if already in back-end
        if self.flush_cache:
            self.execute_flush_cache()
            
        elif self.videogui.property_videolibrary_empty(skinsubtitlechecker.backend_running):
            self.prepare_run()
            
            if self.backend:
                kodi.log(__name__, 'Start running background.', kodi.LOGNOTICE)
                # run in back-end if parameter was set
                self.videogui.set_videolibrary_property("skinsubtitlechecker.backend_running","true")
                self.set_subtitle_properties(None)
                self.run_backend()
            else:
                kodi.log(__name__, 'Execute once.')
                self.videoitem.set_parameter_listitem(self.language.language_iso_639_2)
                self.check_subtitlte()
        else:
            kodi.log(__name__, 'Running in background detected, no action.')

    def execute_flush_cache(self):
        kodi.log(__name__, 'Flush cache.', kodi.LOGNOTICE)
        self.db = DBConnection()
        self.db.flush_cache()
    
    def prepare_run(self):
        self.db = DBConnection()
        self.scrapers = sorted([('opensubtitle', int(self.settings.get_setting("OSpriority")), bool(self.settings.get_setting("OSenabled"))),
                                ('addic7ed', int(self.settings.get_setting("A7priority")), bool(self.settings.get_setting("A7enabled"))),
                                ('podnapisi', int(self.settings.get_setting("PNpriority")), bool(self.settings.get_setting("PNenabled")))],
                               key=itemgetter(2))

    def run_backend(self):
        self.stop = False
        while not self.stop:
            if self.subtitlecheck_needed():
                self.check_subtitlte()
            kodi.sleep(200)
            self.check_stop_backend()
    
    def subtitlecheck_needed(self):
        if not self.videogui.is_scrolling() and (self.videogui.is_movie() or self.videogui.is_episode()):
            return self.videoitem.current_item_changed(self.language.language_iso_639_2)
         
        # clear subtitle check if not movie or episode or if scrolling
        self.set_subtitle_properties(None)
        return False

    def check_stop_backend(self):
        if not self.videogui.videolibray_is_visible():
            kodi.log(__name__, 'back-end stopped.', kodi.LOGNOTICE)
            self.videogui.clear_videolibrary_property("skinsubtitlechecker.backend_running")
            self.stop = True
        if kodi.abort_requested():
            self.stop = True
    
    def check_subtitlte(self):
        self.set_subtitle_properties(-1)
        # check cache first
        kodi.log(__name__, 'start search local cache.')
        subtitle_present = self.db.get_cached_subtitle(self.item)
        if subtitle_present == -1:
            # only check if not found in cache, no subtitle is a result
            for scraper in self.scrapers:
                if scraper[2]:
                    if scraper[0] == 'opensubtitle':
                        with OSDBServer()as osdbserver:
                            kodi.log(__name__, 'start search Opensubtitle.')
                            subtitle_present = osdbserver.searchsubtitles(self.videoitem.item)
                    elif scraper[0] == 'addic7ed':
                        with Adic7edServer()as adic7edserver:
                            kodi.log(__name__, 'start search Addic7ed.')
                            subtitle_present = adic7edserver.searchsubtitles(self.videoitem.item)
                    elif scraper[0] == 'podnapisi':
                        with PNServer()as pnserver:
                            kodi.log(__name__, 'start search Podnapisi.')
                            subtitle_present = pnserver.searchsubtitles(self.videoitem.item)
                
                if subtitle_present >= 0:
                    break
            # store result to cache
            if subtitle_present >= 0:
                kodi.log(__name__, 'cache item')
                self.db.cache_subtitle(self.item, subtitle_present)
            
        self.set_subtitle_properties(subtitle_present)

    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == -1:
            self.videogui.set_property('skinsubtitlechecker.available', self.search_text)
        elif subtitle_present == 1:
            kodi.log(__name__, 'subtitle found.')
            self.videogui.set_property('skinsubtitlechecker.available', self.present_text)
        elif subtitle_present == 0:
            kodi.log(__name__, 'no subtitle found')
            self.videogui.set_property('skinsubtitlechecker.available', self.not_present_text)
        else:
            kodi.log(__name__, 'no subtitle search for item')
            self.videogui.set_property('skinsubtitlechecker.available', '')
        self.set_language(subtitle_present)

    def set_language(self, subtitle_present):
        if(subtitle_present is not None):
            self.videogui.set_property('skinsubtitlechecker.language.full', self.language.language_full)
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_1', self.language.language_iso_639_1)
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2t', self.language.language_iso_639_2t)
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2b', self.language.language_iso_639_2b)
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2_kodi', self.language.language_iso_639_2)
        else:
            self.videogui.set_property('skinsubtitlechecker.language.full', "")
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_1', "")
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2t', "")
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2b', "")
            self.videogui.set_property('skinsubtitlechecker.language.iso_639_2_kodi', "")

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend = None
        self.params = None
        
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the db, it is not used within
            # with
            # statement
            self.db.__exit__(exc_type, exc_value, traceback)
            self.db = None
            del self.db
        except:
            # database is not yet set
            pass
        self.settings.__exit__(exc_type, exc_value, traceback)
        self.language.__exit__(exc_type, exc_value, traceback)
        self.videogui.__exit__(exc_type, exc_value, traceback)
        self.videoitem.__exit__(exc_type, exc_value, traceback)

        # clean variables
        self.flush_cache = None
        self.videoitem = None
        self.not_present_text = None
        self.present_text = None
        self.search_text = None
        self._stop = None
        self.settings = None
        self.language = None
        self.videogui = None

        #delete pointers to variables
        del self.flush_cache
        del self.videoitem
        del self.not_present_text
        del self.present_text
        del self.search_text
        del self._stop
        del self.settings
        del self.language
        del self.videogui

if __name__ == "__main__":
    with SubtitleChecker() as subtitlechecker:
        subtitlechecker.execute()

kodi.log(__name__, 'script finished.')
