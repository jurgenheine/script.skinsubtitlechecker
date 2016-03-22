import xbmc
import xbmcaddon
from json import loads
from lib import kodi

class Setting:
    def __init__(self):
        pass
                    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass       

    def get_setting(self, name):
        return kodi.__addon__.getSetting(name)

    def get_cache_not_found_timeout(self):
        cachetimenotfound = self.get_setting("CacheTimeNotFound")
        if not cachetimenotfound:
            cachetimenotfound = "2"
        return 60 * 60 * float(cachetimenotfound)

    def get_cache_found_timeout(self):
        cachetimefound = self.get_setting("CacheTimeFound")
        if not cachetimefound:
            cachetimefound = "30"
        return 60 * 60 * 24 * float(cachetimefound)

    def get_script_path(self):
        return kodi.__cwd__

    def get_kodi_setting(self, name):
        """
        Uses XBMC/Kodi JSON-RPC API to retrieve subtitles location settings values.
        """
        command = '''{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "Settings.GetSettingValue",
    "params": {
        "setting": "%s"
    }
}'''
        result = kodi.execute_json_rpc(command % name)
        py = loads(result)
        if 'result' in py and 'value' in py['result']:
            return py['result']['value']
        else:
            raise ValueError

    