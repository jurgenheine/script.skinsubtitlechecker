# -*- coding: UTF-8 -*-

import sys
import kodi
from subtitleresult import SubtitleResult
from lib.videogui import VideoGui
from lib.subtitlechecker import SubtitleChecker
from lib.db_utils import DBConnection

#import ptvsd
#ptvsd.enable_attach(secret='my_secret')
class Main:
    def __init__(self):
        kodi.log(__name__, "version %s started" % kodi.get_version(), kodi.LOGNOTICE)
        self._init_vars()
        self._parse_argv() 
            
    def __enter__(self):
        return self

    def _init_vars(self):
        self.gui = VideoGui()
        self.subtitlechecker = SubtitleChecker()
        self.stop = False
    
    @staticmethod
    def _get_params():
        param = {}
        if len(sys.argv) > 1:
            kodi.log(__name__, "params: %s" % sys.argv[1])
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
        self._set_action_from_params()
        self.gui.set_gui_params(self.params)

    def _set_action_from_params(self):
        if len(self.params) == 0:
            # if no parameters, then asume run from gui
            self.action = 'runfromgui'
        else:
            # if no action parameter, then asume run once
            self.action = self.params.get('action', 'runonce')
            if self.params.get('backend', False):
                # if backend set, then set action to backend
                self.action = "backend"

    def execute(self):
        if self.action == 'runfromgui':
            kodi.log(__name__, 'Running from GUI, no action.')
        elif self.action == 'flushcache':
            self.execute_flush_cache()
        elif self.gui.is_running_backend():
            # don't run if already in back-end
            kodi.log(__name__, 'Running in background detected, no action.')
        elif self.action == 'backend':
            # run in back-end if parameter was set
            self.run_backend()
        else:
            self.run_once()

    def execute_flush_cache(self):
        kodi.log(__name__, 'Flush cache.', kodi.LOGNOTICE)
        with DBConnection() as db:
            db.flush_cache()
    
    def run_backend(self):
        self.init_run_backend()
        while not self.stop:
            if self.gui.subtitlecheck_needed():
                self.check_subtitle()
            else:
                kodi.sleep(200)
            self.check_stop_backend()
    
    def init_run_backend(self):
        kodi.log(__name__, 'Start running background.', kodi.LOGNOTICE)
        self.gui.set_running_backend()
        self.gui.set_subtitle_properties(SubtitleResult.HIDE)
        self.stop = False

    def run_once(self):
        kodi.log(__name__, 'Execute once.')
        self.check_subtitle()

    def check_stop_backend(self):
        if not self.gui.videolibray_is_visible() or kodi.abort_requested():
            kodi.log(__name__, 'back-end stopped.', kodi.LOGNOTICE)
            self.gui.reset_running_backend()
            self.stop = True
    
    def check_subtitle(self):
        # set gui property to searching
        self.gui.set_subtitle_properties(SubtitleResult.SEARCH)
        subtitle_present = self.subtitlechecker.check_subtitle(self.gui.get_video_item())
        # set data to gui properties
        self.gui.set_subtitle_properties(subtitle_present)

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up_gui(exc_type, exc_value, traceback)        
        self.clean_up_subtitlechecker(exc_type, exc_value, traceback)
        # clean variables and delete pointers to variables
        self.stop = None
        del self.stop
        self.params =None
        del self.params
    
    def clean_up_gui(self, exc_type, exc_value, traceback):
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the gui class, it is not used
            # within with statement
            self.gui.__exit__(exc_type, exc_value, traceback)
            self.gui = None
            del self.gui
        except:
            # database is not yet set
            pass

    def clean_up_subtitlechecker(self, exc_type, exc_value, traceback):
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the videoitem class, it is not
            # used within with statement
            self.subtitlechecker.__exit__(exc_type, exc_value, traceback)
            self.subtitlechecker = None
            del self.subtitlechecker
        except:
            # database is not yet set
            pass    

if __name__ == "__main__":
    with Main() as subtitlechecker:
        subtitlechecker.execute()

kodi.log(__name__, 'script finished.')
