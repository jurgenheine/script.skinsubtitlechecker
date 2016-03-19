# -*- coding: UTF-8 -*-

import sys
import xbmc
import xbmcgui
import time
from operator import itemgetter
from scrapers.open_subtitles import OSDBServer
from scrapers.addic7ed import Adic7edServer
from scrapers.podnapisi import PNServer
from lib import helpers
from lib.db_utils import DBConnection
from lib.setting import Setting
from lib.language import Language
from lib.properties import Properties

#import ptvsd
#ptvsd.enable_attach(secret='my_secret')
class SubtitleChecker:
    def __init__(self):
        helpers.log(__name__, "version %s started" % helpers.get_version(), helpers.LOGNOTICE)
        self._init_vars()
        self._parse_argv() 
            
    def __enter__(self):
        return self

    def _init_vars(self):
        self.settings = Setting()
        self.language = Language()
        self.properties = Properties()
        self.item = None
        self.stop = False
        self.db = None
    
    @staticmethod
    def _get_params():
        helpers.log(__name__, "params: %s" % sys.argv[1])
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
        helpers.log(__name__, "params: %s" % self.params)
        self.backend = self.params.get('backend', False)
        self.flush_cache = self.params.get('flushcache', False)
        self.present_text = self.params.get('availabereturnvalue', '')
        self.not_present_text = self.params.get('notavailablereturnvalue', '')
        self.search_text = self.params.get('searchreturnvalue', '')

    def execute(self):
        # don't run if already in back-end
        if self.flush_cache:
            self.execute_flush_cache()
            
        elif xbmc.getCondVisibility('IsEmpty(Window(videolibrary).Property(skinsubtitlechecker.backend_running))'):
            self.prepare_run()
            
            if self.backend:
                helpers.log(__name__, 'Start running background.', helpers.LOGNOTICE)
                # run in back-end if parameter was set
                xbmc.executebuiltin("SetProperty(skinsubtitlechecker.backend_running,true,videolibrary)")
                self.set_subtitle_properties(None)
                self.run_backend()
            else:
                helpers.log(__name__, 'Execute once.')
                self.item = self.get_parameter_listitem()
                self.check_subtitlte()
        else:
            helpers.log(__name__, 'Running in background detected, no action.')

    def execute_flush_cache(self):
        helpers.log(__name__, 'Flush cache.', helpers.LOGNOTICE)
        self.set_db()
        self.db.flush_cache()
    
    def prepare_run(self):
        self.set_db()
        self.set_scrapers()
    
    def set_db(self):
        self.db = DBConnection()
        
    def set_scrapers(self):
        self.scrapers = sorted([('opensubtitle', int(self.settings.get_setting("OSpriority")), bool(self.settings.get_setting("OSenabled"))),
                                ('addic7ed', int(self.settings.get_setting("A7priority")), bool(self.settings.get_setting("A7enabled"))),
                                ('podnapisi', int(self.settings.get_setting("PNpriority")), bool(self.settings.get_setting("PNenabled")))],
                               key=itemgetter(2))

    def run_backend(self):
        self.stop = False
        while not self.stop:
            if self.check_current_item_subtitle():
                self.check_subtitlte()
            xbmc.sleep(200)
            self.check_stop_backend()

    def get_current_listitem(self):
        return self.create_item(xbmc.getInfoLabel("ListItem.Year"), 
                                xbmc.getInfoLabel("ListItem.Season"), 
                                xbmc.getInfoLabel("ListItem.Episode"), 
                                xbmc.getInfoLabel("ListItem.TVShowTitle"),
                                xbmc.getInfoLabel("ListItem.OriginalTitle"), 
                                xbmc.getInfoLabel("ListItem.Title"),
                                xbmc.getInfoLabel("ListItem.FileName"))
    
    def get_parameter_listitem(self):
        return self.create_item(self.params.get('year', ''),
                                     self.params.get('season', ''),
                                     self.params.get('episode', ''),
                                     self.params.get('tvshow', ''),
                                     self.params.get('originaltitle', ''),
                                     self.params.get('title', ''),
                                     self.params.get('filename', ''))
    
    @staticmethod
    def check_item_not_empty(item):
        if(item['title'] == "" and item['tvshow'] == ""):
            # no item data for search
            return False
        return True
    
    def check_item_changed(self, item):
        if(self.item['year'] != item['year'] or self.item['season'] != item['season'] or self.item['episode'] != item['episode'] or self.item['tvshow'] != item['tvshow'] or self.item['title'] != item['title'] or self.item['filename'] != item['filename']):
            return True
        return False
    
    def check_current_item_subtitle(self):
        if not xbmc.getCondVisibility("Container.Scrolling") and (xbmc.getCondVisibility("Container.Content(movies)") or xbmc.getCondVisibility("Container.Content(episodes)")):
            item = self.get_current_listitem()
            if self.check_item_not_empty(item) and (not self.item or self.check_item_changed(item)):
                self.item = item
                return True
        else: 
                # clear subtitle check
                self.set_subtitle_properties(None)
        return False

    def check_stop_backend(self):
        if not xbmc.getCondVisibility("Window.IsVisible(videolibrary)"):
            helpers.log(__name__, 'back-end stopped.', helpers.LOGNOTICE)
            xbmc.executebuiltin('ClearProperty(skinsubtitlechecker.backend_running,videolibrary)')
            self.stop = True
        if xbmc.abortRequested:
            self.stop = True
    
    def create_item(self, year, season, episode, tvshow, originaltitle, title, filename):
        item = {'year': helpers.normalize_string(year),  # Year
                'season': helpers.normalize_string(season),  # Season
                'episode': helpers.normalize_string(episode),  # Episode
                'tvshow': helpers.normalize_string(tvshow),
                'title': helpers.normalize_string(originaltitle),  # try to get original title
                'filename': helpers.normalize_string(filename),
                '3let_language': []}

        item['3let_language'].append(self.language.preferredsub)
#         log(__name__, "3let language: %s" % item['3let_language'])
        
        if item['title'] == "":
            item['title'] = helpers.normalize_string(title)      # no original title, get just Title
        
        if item['year'] == "":
            item['title'], year = helpers.get_clean_movie_title(item['title'])
            item['year'] = str(year)
                    
        if item['episode'].lower().find("s") > -1:  # Check if season is "Special"
            item['season'] = "0"
            item['episode'] = item['episode'][-1:]
        
        return item
    
    def check_subtitlte(self):
        self.set_subtitle_properties(-1)
        helpers.log(__name__, "data to search: year=%s; season=%s; episode=%s; tvshow=%s; title=%s; filename= %s" % (self.item['year'],
             self.item['season'],
             self.item['episode'],
             self.item['tvshow'],
             self.item['title'],
             self.item['filename']))
        # check cache first
        helpers.log(__name__, 'start search local cache.')
        subtitle_present = self.db.get_cached_subtitle(self.item)
        if subtitle_present == -1:
            # only check if not found in cache, no subtitle is a result
            for scraper in self.scrapers:
                if scraper[2]:
                    if scraper[0] == 'opensubtitle':
                        with OSDBServer()as osdbserver:
                            helpers.log(__name__, 'start search Opensubtitle.')
                            subtitle_present = osdbserver.searchsubtitles(self.item)
                    elif scraper[0] == 'addic7ed':
                        with Adic7edServer()as adic7edserver:
                            helpers.log(__name__, 'start search Addic7ed.')
                            subtitle_present = adic7edserver.searchsubtitles(self.item)
                    elif scraper[0] == 'podnapisi':
                        with PNServer()as pnserver:
                            helpers.log(__name__, 'start search Podnapisi.')
                            subtitle_present = pnserver.searchsubtitles(self.item)
#                 helpers.log(__name__, 'subtitle present value:%s'
#                 %(subtitle_present))
                if subtitle_present == 1:
                    break
            # store result to cache
            if subtitle_present >= 0:
                helpers.log(__name__, 'cache item')
                self.db.cache_subtitle(self.item, subtitle_present)
            
        self.set_subtitle_properties(subtitle_present)

    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == -1:
            self.language.set_language()
            self.properties.set_property('skinsubtitlechecker.available', self.search_text)
        elif subtitle_present == 1:
            helpers.log(__name__, 'subtitle found.')
            self.language.set_language()
            self.properties.set_property('skinsubtitlechecker.available', self.present_text)
        elif subtitle_present == 0:
            helpers.log(__name__, 'no subtitle found')
            self.language.set_language()
            self.properties.set_property('skinsubtitlechecker.available', self.not_present_text)
        else:
            helpers.log(__name__, 'no subtitle search for item')
            self.language.reset_language()
            self.properties.set_property('skinsubtitlechecker.available', '')

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend = None
        self.params = None
        
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the db, it is not used within with
            # statement
            self.db.__exit__(exc_type, exc_value, traceback)
            self.db = None
            del self.db
        except:
            # database is not yet set
            pass
        self.settings.__exit__(exc_type, exc_value, traceback)
        self.language.__exit__(exc_type, exc_value, traceback)
        self.properties.__exit__(exc_type, exc_value, traceback)

        # clean variables
        self.flush_cache = None
        self.item = None
        self.not_present_text = None
        self.present_text = None
        self.search_text = None
        self._stop = None
        self.settings = None
        self.language = None
        self.properties = None

        #delete pointers to variables
        del self.flush_cache
        del self.item
        del self.not_present_text
        del self.present_text
        del self.search_text
        del self._stop
        del self.settings
        del self.language
        del self.properties

if __name__ == "__main__":
    with SubtitleChecker() as subtitlechecker:
        subtitlechecker.execute()

helpers.log(__name__, 'script finished.')
