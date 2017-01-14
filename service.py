import skinsubtitlekodi as kodi
import sys
import threading
from lib.db_utils import DBConnection
from skinsubtitlesetting import Setting
from skinsubtitleresult import SubtitleResult
from lib.videogui import VideoGui
from lib.subtitlechecker import SubtitleChecker

class Service:
    def __init__(self):
        kodi.log(__name__, "version %s started" % kodi.get_version(), kodi.LOGNOTICE)
        self._init_vars()
    
    def __enter__(self):
        return self

    def _init_vars(self):
        self.gui = VideoGui()
        self.subtitlechecker = SubtitleChecker()
        self.setting = Setting()

    def run(self):
        self.start_cache_thread()
        #TODO: Enable when external providers are implemented
        #self.start_provider_thread()
        self.subtitle_search()

    def start_cache_thread(self):
        thread = threading.Thread(target=self.cache_thread)
        thread.daemon = True
        thread.start()

    def cache_thread(self):
        kodi.log(__name__, 'Start running cache service.', kodi.LOGNOTICE)
        monitor = xbmc.Monitor()
        with Setting() as setting:
            wait_time = setting.get_cache_not_found_timeout()
        while not kodi.abort_requested():
            with DBConnection() as db:
                db.cleanup_subtitle_cache()
            # Sleep/wait for abort for wait_time seconds
            if kodi.wait_for_abort(wait_time):
                # Abort was requested while waiting. We should exit
                break

    def start_provider_thread(self):
        thread = threading.Thread(target=self.provider_thread)
        thread.daemon = True
        thread.start()

    def provider_thread(self):
        kodi.log(__name__, 'Start running provider cache service.', kodi.LOGNOTICE)
        with Setting() as setting:        
            wait_time = setting.get_provider_search_interval()
        while not kodi.abort_requested():
            # check providers
            addons = kodi.get_addons()
            # update provider cache
            with DBConnection() as db:
                db.update_cached_providers(addons)
            # Sleep/wait for abort for wait_time seconds
            if kodi.wait_for_abort(self.wait_time):
                # Abort was requested while waiting. We should exit
                break

    def init_run_backend(self):
        kodi.log(__name__, 'Start running background.', kodi.LOGNOTICE)
        self.gui.set_running_backend()
        self.gui.show_subtitle(SubtitleResult.HIDE)

    def subtitle_search(self):
        self.init_run_backend()
        skin_poll_time = self.setting.get_polling_interval()
        notification_poll_time = self.setting.get_notification_delay()
        skinsupport = self.gui.get_skin_support()
        while not kodi.abort_requested():
            if self.gui.subtitlecheck_needed():
                self.check_subtitle()
                skinsupport = self.gui.get_skin_support()
            else:
                if(skinsupport):
                    kodi.sleep(skin_poll_time)
                else:
                    kodi.sleep(notification_poll_time)
        kodi.log(__name__, 'back-end stopped.', kodi.LOGNOTICE)
        self.gui.reset_running_backend()

    def check_subtitle(self):
        # set gui property to searching
        self.gui.show_subtitle(SubtitleResult.SEARCH)
        item = self.gui.get_video_item()
        subtitle_present = self.subtitlechecker.check_subtitle(item)
        # set data to gui properties
        self.gui.show_subtitle(subtitle_present)

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up_gui(exc_type, exc_value, traceback)        
        self.clean_up_subtitlechecker(exc_type, exc_value, traceback)
        self.clean_up_setting(exc_type, exc_value, traceback)
    
    def clean_up_setting(self, exc_type, exc_value, traceback):
        try:
            self.setting.__exit__(exc_type, exc_value, traceback)
            self.setting = None
            del self.setting
        except:
            # database is not yet set
            pass
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
    with Service() as service:
        service.run()

kodi.log(__name__, 'cache service finished.')
