from lib import kodi
from lib.db_utils import DBConnection
from lib.setting import Setting

class Service:
    def __init__(self):
        kodi.log(__name__, "version %s started" % kodi.get_version(), kodi.LOGNOTICE)
        self.db = DBConnection()
        self.setting = Setting()
        self.wait_time = self.setting.get_cache_not_found_timeout()
    
    def __enter__(self):
        return self

    def run(self):
        kodi.log(__name__, 'Start running cache service.', kodi.LOGNOTICE)
        monitor = xbmc.Monitor()
        while not kodi.abort_requested():
            self.db.cleanup_cache()
            # Sleep/wait for abort for wait_time seconds
            if kodi.wait_for_abort(self.wait_time):
                # Abort was requested while waiting. We should exit
                break

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.db.__exit__(exc_type, exc_value, traceback)
            self.db = None
            del self.db
        except:
            # database is not yet set
            pass
        self.setting.__exit__(exc_type, exc_value, traceback)
        self.setting=None
        self.wait_time = None
        del self.setting
        del self.wait_time 
  
if __name__ == "__main__":
    with Service() as service:
        service.run()

kodi.log(__name__, 'cache service finished.')
