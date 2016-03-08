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
        self.window = xbmcgui.Window(10025)  # MyVideoNav.xml (videolibrary)
        self.dialogwindow = xbmcgui.Window(12003)  # DialogVideoInfo.xml (movieinformation)
        self.preferredsub = ''
        self.item = None
        self.stop = False
        self.db = None
        self.last_cleanup_cache = time.time() - helpers.get_cache_not_found_timeout()
    
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
        self.unknown_text = self.params.get('searchreturnvalue', '')

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
                self.set_subtitle_properties(-1)
                self.run_backend()
            else:
                helpers.log(__name__, 'Execute once.')
                self.set_parameter_listitem()
                self.check_subtitlte()
        else:
            helpers.log(__name__, 'Running in background detected, no action.')

    def execute_flush_cache(self):
        helpers.log(__name__, 'Flush cache.', helpers.LOGNOTICE)
        self.set_db()
        self.db.flush_cache()
    
    def prepare_run(self):
        self.set_db()
        self.set_language()
        self.set_scrapers()
    
    def set_db(self):
        self.db = DBConnection()
        
    def set_language(self):
        lan = helpers.get_kodi_setting('locale.subtitlelanguage')
        if lan == "Portuguese (Brazil)":
            self.preferredsub = "pob"
        elif lan == "Greek":
            self.preferredsub = "ell"
        else:
            self.preferredsub = xbmc.convertLanguage(lan, xbmc.ISO_639_2)
        language_iso_639_1 = xbmc.convertLanguage(lan, xbmc.ISO_639_1)
        language_iso_639_2t = helpers.get_ISO_639_2_T(self.preferredsub)
        language_iso_639_2b = helpers.get_ISO_639_2_B(self.preferredsub)
        
        self.window.setProperty('skinsubtitlechecker.language.full', lan)
        self.dialogwindow.setProperty('skinsubtitlechecker.language.full', lan)
 
        self.window.setProperty('skinsubtitlechecker.language.iso_639_1', language_iso_639_1)
        self.dialogwindow.setProperty('skinsubtitlechecker.language.iso_639_1', language_iso_639_1)   
        
        self.window.setProperty('skinsubtitlechecker.language.iso_639_2t', language_iso_639_2t) 
        self.dialogwindow.setProperty('skinsubtitlechecker.language.iso_639_2t', language_iso_639_2t) 
        
        self.window.setProperty('skinsubtitlechecker.language.iso_639_2b', language_iso_639_2b)
        self.dialogwindow.setProperty('skinsubtitlechecker.language.iso_639_2b', language_iso_639_2b) 
           
        self.window.setProperty('skinsubtitlechecker.language.iso_639_2_kodi', self.preferredsub)
        self.dialogwindow.setProperty('skinsubtitlechecker.language.iso_639_2_kodi', self.preferredsub)   
        

    def set_scrapers(self):
        self.scrapers = sorted([('opensubtitle', int(helpers.get_setting("OSpriority")), bool(helpers.get_setting("OSenabled"))),
                                ('addic7ed', int(helpers.get_setting("A7priority")), bool(helpers.get_setting("A7enabled"))),
                                ('podnapisi', int(helpers.get_setting("PNpriority")), bool(helpers.get_setting("PNenabled")))],
                               key=itemgetter(2))

    def run_backend(self):
        self.stop = False
        while not self.stop:
            if self.check_current_item_subtitle():
                self.check_subtitlte()
            elif not self.cleanup_cache():
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
    
    def set_parameter_listitem(self):
        self.item = self.create_item(self.params.get('year', ''),
                                     self.params.get('season', ''),
                                     self.params.get('episode', ''),
                                     self.params.get('tvshow', ''),
                                     self.params.get('originaltitle', ''),
                                     self.params.get('title', ''),
                                     self.params.get('filename', ''))
    
    @staticmethod
    def check_item_not_empty(item):
        if(item['title'] == "" and
           item['tvshow'] == ""):
            # no item data for search
            return False
        elif(item['title'] != "" and
             item['tvshow'] == "" and
             item['year'] == ""):
            # title is known, but no tv-show title and no year, extra check to get year
            title, year = helpers.get_clean_movie_title(item['title'])
            if title == "" or year < 1900:
                # not tv-show and no title or no year, so probably not a movie
                return False
        
        elif(item['season'] != "" and
             item['episode'] == ""):
            # Browse Season, no search possible
            return False
            
#         if (xbmc.getCondVisibility("ListItem.IsFolder")):
#         Not checking for folder, not always an indication for not video
        return True
    
    def check_item_changed(self, item):
        if(self.item['year'] != item['year'] or
           self.item['season'] != item['season'] or
           self.item['episode'] != item['episode'] or
           self.item['tvshow'] != item['tvshow'] or
           self.item['title'] != item['title'] or
           self.item['filename'] != item['filename']):
            return True
        return False
    
    def check_current_item_subtitle(self):
        if not xbmc.getCondVisibility("Container.Scrolling"):
            item = self.get_current_listitem()
            if self.check_item_not_empty(item) and (not self.item or self.check_item_changed(item)):
                self.item = item
                return True
        return False

    def cleanup_cache(self):
        if self.last_cleanup_cache <= time.time() - helpers.get_cache_not_found_timeout():
            self.db.cleanup_cache()
            self.last_cleanup_cache = time.time()
            return True
        else:
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

        item['3let_language'].append(self.preferredsub)
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
        helpers.log(__name__, "data to search: year=%s; season=%s; episode=%s; tvshow=%s; title=%s; filename= %s" %
            (self.item['year'],
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
#                 helpers.log(__name__, 'subtitle present value:%s' %(subtitle_present))
                if subtitle_present == 1:
                    break
            # store result to cache
            if subtitle_present >= 0:
                helpers.log(__name__, 'cache item')
                self.db.cache_subtitle(self.item, subtitle_present)
            
        self.set_subtitle_properties(subtitle_present)

    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == -1:
            self.window.setProperty('skinsubtitlechecker.available', self.unknown_text)
            self.dialogwindow.setProperty('skinsubtitlechecker.available', self.unknown_text)
        elif subtitle_present == 1:
            helpers.log(__name__, 'subtitle found.')
            self.window.setProperty('skinsubtitlechecker.available', self.present_text)
            self.dialogwindow.setProperty('skinsubtitlechecker.available', self.present_text)
        else:
            helpers.log(__name__, 'no subtitle found')
            self.window.setProperty('skinsubtitlechecker.available', self.not_present_text)
            self.dialogwindow.setProperty('skinsubtitlechecker.available', self.not_present_text)
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.backend = None
        self.params = None
        # call explicit the exit function of the db, it is not used within with statement 
        # noinspection PyBroadException
        try:
            self.db.__exit__(exc_type, exc_value, traceback)
            self.db = None
        except:
            # database is not yet set
            pass
        self.dialogwindow = None
        self.flush_cache = None
        self.item = None
        self.not_present_text = None
        self.preferredsub = None
        self.present_text = None
        self.unknown_text = None
        self.window = None
        self._stop = None
        self.last_cleanup_cache = None

if __name__ == "__main__":
    with SubtitleChecker() as subtitlechecker:
        subtitlechecker.execute()

helpers.log(__name__, 'script finished.')
