import xbmc
from lib import helpers
from lib.db_utils import DBConnection
from lib.setting import Setting

class Service:
    def __init__(self):
        helpers.log(__name__, "version %s started" % helpers.get_version(), helpers.LOGNOTICE)
        self.db = DBConnection()
        self.setting = Setting()
        self.wait_time = self.setting.get_cache_not_found_timeout()
    
    def __enter__(self):
        return self

    def run(self):
        helpers.log(__name__, 'Start running cache service.', helpers.LOGNOTICE)
        monitor = xbmc.Monitor()
        while not monitor.abortRequested():
            self.db.cleanup_cache()
            # Sleep/wait for abort for wait_time seconds
            if monitor.waitForAbort(self.wait_time):
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

helpers.log(__name__, 'cache service finished.')
