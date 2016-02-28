# -*- coding: UTF-8 -*-

import sys
import xbmc
import xbmcgui
from operator import itemgetter
from scrapers.open_subtitles import OSDBServer
from scrapers.addic7ed import Adic7edServer
from scrapers.podnapisi import PNServer
from lib.helpers import log, normalize_string, get_setting, get_kodi_setting, get_version
from lib.helpers import get_clean_movie_title, get_ISO_639_2_T, LOGNOTICE
from lib.db_utils import DBConnection
# Script constants


class SubtitleChecker:
    def __init__(self):
        log(__name__, "version %s started" % get_version(), LOGNOTICE)
        self._init_vars()
        self._parse_argv()
            
    def __enter__(self):
        return self

    def _init_vars(self):
        # win_id = xbmcgui.getCurrentWindowId()
        # log(__name__,'window ID: ' + str(win_id))
        self.window = xbmcgui.Window(10025)  # MyVideoNav.xml (videolibrary)
        self.dialogwindow = xbmcgui.Window(12003)  # DialogVideoInfo.xml (movieinformation)
        self.preferredsub = ''
        self.item = None
        self.stop = False
        self.db = None
    
    @staticmethod
    def _get_params():
        log(__name__, "params: %s" % sys.argv[1])
        param = {}
        paramstring = sys.argv[1]
        if len(paramstring) >= 2:
            params = paramstring
            cleanedparams = params.replace('?', '')
            # if params[len(params) - 1] == '/':
            #     params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]

        return param

    def _parse_argv(self):
        self.params = self._get_params()
        log(__name__, "params: %s" % self.params)
        self.backend = self.params.get('backend', False)
        self.flush_cache = self.params.get('flushcache', False)
        self.present_text = self.params.get('availabereturnvalue', '')
        self.not_present_text = self.params.get('notavailablereturnvalue', '')
        self.unknown_text = self.params.get('searchreturnvalue', '')

    def execute(self):
        # don't run if already in back-end
        if self.flush_cache:
            self.execute_flush_cache()
            
        elif xbmc.getCondVisibility('IsEmpty(Window(videolibrary).Property(skinsubtitlechecker_backend_running))'):
            self.prepare_run()
            
            if self.backend:
                log(__name__, 'Start running background.', LOGNOTICE)
                # run in back-end if parameter was set
                xbmc.executebuiltin("SetProperty(skinsubtitlechecker_backend_running,true,videolibrary)")
                self.set_subtitle_properties(-1)
                self.run_backend()
            else:
                log(__name__, 'Execute once.')
                self.set_parameter_listitem()
                self.check_subtitlte()
        else:
            log(__name__, 'Running in background detected, no action.')

    def execute_flush_cache(self):
        log(__name__, 'Flush cache.', LOGNOTICE)
        self.set_db()
        self.db.flush_cache()
    
    def prepare_run(self):
        self.set_db()
        self.set_language()
        self.set_scrapers()
    
    def set_db(self):
        self.db = DBConnection()
        
    def set_language(self):
        lan = get_kodi_setting('locale.subtitlelanguage')
        if lan == "Portuguese (Brazil)":
            self.preferredsub = "pob"
        elif lan == "Greek":
            self.preferredsub = "ell"
        else:
            self.preferredsub = xbmc.convertLanguage(lan, xbmc.ISO_639_2)
        
        skinlanguage = get_ISO_639_2_T(self.preferredsub)
        self.window.setProperty('SubTitleAvailableLanguage', skinlanguage)
        self.dialogwindow.setProperty('SubTitleAvailableLanguage', skinlanguage)    

    def set_scrapers(self):
        self.scrapers = sorted([('opensubtitle', int(get_setting("OSpriority")), bool(get_setting("OSenabled"))),
                                ('addic7ed', int(get_setting("A7priority")), bool(get_setting("A7enabled"))),
                                ('podnapisi', int(get_setting("PNpriority")), bool(get_setting("PNenabled")))],
                               key=itemgetter(2))

    def run_backend(self):
        self.stop = False
        while not self._stop:
            if not xbmc.getCondVisibility("Container.Scrolling"):
                item = self.get_current_listitem()
                if self.check_item_not_empty(item) and (not self.item or self.check_item_changed(item)):
                    self.item = item
                    self.check_subtitlte()
                else:
                    xbmc.sleep(200)
#                     log(__name__,'No change detected in current ListItem.')
            else:
                xbmc.sleep(200)
#                 log(__name__,'ListItem is folder or Container is scrolling, no action.')
            
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
            title, year = get_clean_movie_title(item['title'])
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
    
    def check_stop_backend(self):
        if not xbmc.getCondVisibility("Window.IsVisible(videolibrary)"):
            log(__name__, 'back-end stopped.', LOGNOTICE)
            xbmc.executebuiltin('ClearProperty(skinsubtitlechecker_backend_running,videolibrary)')
            self.stop = True
        if xbmc.abortRequested:
            self.stop = True
    
    def create_item(self, year, season, episode, tvshow, originaltitle, title, filename):
        item = {'year': normalize_string(year),  # Year
                'season': normalize_string(season),  # Season
                'episode': normalize_string(episode),  # Episode
                'tvshow': normalize_string(tvshow),
                'title': normalize_string(originaltitle),  # try to get original title
                'filename': normalize_string(filename),
                '3let_language': []}

        item['3let_language'].append(self.preferredsub)
#         log(__name__, "3let language: %s" % item['3let_language'])
        
        if item['title'] == "":
            item['title'] = normalize_string(title)      # no original title, get just Title
        
        if item['year'] == "":
            item['title'], year = get_clean_movie_title(item['title'])
            item['year'] = str(year)
                    
        if item['episode'].lower().find("s") > -1:  # Check if season is "Special"
            item['season'] = "0"
            item['episode'] = item['episode'][-1:]
        
        return item
    
    def check_subtitlte(self):
        self.set_subtitle_properties(-1)
        log(__name__, "data to search: year=%s; season=%s; episode=%s; tvshow=%s; title=%s; filename= %s" %
            (self.item['year'],
             self.item['season'],
             self.item['episode'],
             self.item['tvshow'],
             self.item['title'],
             self.item['filename']))
        # check cache first
        log(__name__, 'start search local cache.')
        subtitle_present = self.db.get_cached_subtitle(self.item)
        if subtitle_present == -1:
            # only check if not found in cache, no subtitle is a result
            for scraper in self.scrapers:
                if scraper[2]:
                    if scraper[0] == 'opensubtitle':
                        with OSDBServer()as osdbserver:
                            log(__name__, 'start search Opensubtitle.')
                            subtitle_present = osdbserver.searchsubtitles(self.item)
                    elif scraper[0] == 'addic7ed':
                        with Adic7edServer()as adic7edserver:
                            log(__name__, 'start search Addic7ed.')
                            subtitle_present = adic7edserver.searchsubtitles(self.item)
                    elif scraper[0] == 'podnapisi':
                        with PNServer()as pnserver:
                            log(__name__, 'start search Podnapisi.')
                            subtitle_present = pnserver.searchsubtitles(self.item)
#                 log(__name__, 'subtitle present value:%s' %(subtitle_present))
                if subtitle_present == 1:
                    break
            # store result to cache
            if subtitle_present >= 0:
                log(__name__, 'cache item')
                self.db.cache_subtitle(self.item, subtitle_present)
            
        self.set_subtitle_properties(subtitle_present)

    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == -1:
            self.window.setProperty('SubTitleAvailable', self.unknown_text)
            self.dialogwindow.setProperty('SubTitleAvailable', self.unknown_text)
        elif subtitle_present == 1:
            log(__name__, 'subtitle found.')
            self.window.setProperty('SubTitleAvailable', self.present_text)
            self.dialogwindow.setProperty('SubTitleAvailable', self.present_text)
        else:
            log(__name__, 'no subtitle found')
            self.window.setProperty('SubTitleAvailable', self.not_present_text)
            self.dialogwindow.setProperty('SubTitleAvailable', self.not_present_text)
    
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

if __name__ == "__main__":
    with SubtitleChecker() as subtitlechecker:
        subtitlechecker.execute()

log(__name__, 'script finished.')
