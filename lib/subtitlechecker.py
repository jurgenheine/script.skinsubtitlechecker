# -*- coding: UTF-8 -*-

import Queue as queue
import threading
from providers.open_subtitles import OSDBServer
from providers.addic7ed import Adic7edServer
from providers.podnapisi import PNServer
from providers.addic7ed_tvshows import Adic7edServer_TVShows
import skinsubtitlekodi as kodi
from skinsubtitleresult import SubtitleResult
from lib.db_utils import DBConnection
from skinsubtitlesetting import Setting

class SubtitleChecker:
    def __init__(self):
        self._init_database()
        self._init_providers()
            
    def __enter__(self):
        return self

    def _init_database(self):
        self.db = DBConnection()
    
    def _init_providers(self):
        providers = []
        with Setting() as settings:
            if(bool(settings.get_setting("OSenabled"))):
                providers.append('opensubtitle')
            if(bool(settings.get_setting("A7enabled"))):
                providers.append('addic7ed')
                providers.append('addic7ed_tvshows')
            if(bool(settings.get_setting("PNenabled"))):
                providers.append('podnapisi')
        self.providers = providers

    def check_subtitle(self, item):
        # check cache first
        subtitle_present = self.search_cache(item)
        if subtitle_present == SubtitleResult.SEARCH:
            # only check if not found in cache, no subtitle is a result
            subtitle_present= self.search_providers(item)
                
            # store result to cache
            self.store_cache(item,subtitle_present)
        return subtitle_present

    def search_cache(self, item):
        kodi.log(__name__, 'start search local cache.')
        return self.db.get_cached_subtitle(item)

    def store_cache(self, item, subtitle_present):
        if subtitle_present != SubtitleResult.SEARCH and subtitle_present != SubtitleResult.HIDE:
            kodi.log(__name__, 'cache item')
            self.db.cache_subtitle(item, subtitle_present)

    def search_providers(self, item):
        result_queue = queue.Queue()
        thread_count = self.start_subtitle_providers(item, result_queue)
            
        return self.get_subtitle_result(thread_count, result_queue)

    def get_subtitle_result(self,thread_count, result_queue):
        subtitle_present = SubtitleResult.SEARCH
        # wait for the first subtitle found or if all checks are negative
        for x in range(0, thread_count):
            current_subtitle_present = result_queue.get()
            if current_subtitle_present != SubtitleResult.SEARCH and current_subtitle_present != SubtitleResult.HIDE:
                # result returned, set to subtitle present property, ignore error result
                subtitle_present = current_subtitle_present
            if subtitle_present == SubtitleResult.AVAILABLE:
                #subtitle found, other results can be ignored
                break
        return subtitle_present

    def start_subtitle_providers(self, item, result_queue):
        thread_count = 0 # number of threads started,needed to determine max queue results
            
        #start the threads
        for provider in self.providers:
            thread = threading.Thread(target=self.perform_search, args=(provider, item, result_queue))
            thread.daemon = True
            thread_count+=1
            thread.start()
        return thread_count

    def perform_search(self, name, item, result_queue):
        if name == 'opensubtitle':
            with OSDBServer()as osdbserver:
                kodi.log(__name__, 'start search Opensubtitle.')
                result_queue.put(osdbserver.searchsubtitles(item))
        elif name == 'addic7ed':
            with Adic7edServer()as adic7edserver:
                kodi.log(__name__, 'start search Addic7ed.')
                result_queue.put(adic7edserver.searchsubtitles(item))
        elif name == 'addic7ed_tvshows':
            if item['tvshow']:
                with Adic7edServer_TVShows()as adic7edserver_tvshows:
                    kodi.log(__name__, 'start search Addic7ed TV shows.')
                    result_queue.put(adic7edserver_tvshows.searchsubtitles(item))
            else:
                result_queue.put(SubtitleResult.NOT_AVAILABLE)
        elif name == 'podnapisi':
            with PNServer()as pnserver:
                kodi.log(__name__, 'start search Podnapisi.')
                result_queue.put(pnserver.searchsubtitles(item))

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up_database(exc_type, exc_value, traceback)
        
        # clean variables and delete pointers to variables
        self.provider = None
        del self.provider
        
    def clean_up_database(self, exc_type, exc_value, traceback):
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the db class, it is not used within with statement
            self.db.__exit__(exc_type, exc_value, traceback)
            self.db = None
            del self.db
        except:
            # database is not yet set
            pass



