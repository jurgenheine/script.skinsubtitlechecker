import xbmc
import xbmcaddon
from json import loads

class Setting:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.cwd = xbmc.translatePath(self.addon.getAddonInfo('path')).decode("utf-8")
                    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.addon = None
        self.cwd =None
        del self.addon
        del self.cwd

    def get_setting(self, name):
        return self.addon.getSetting(name)

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
        return self.cwd

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
        result = xbmc.executeJSONRPC(command % name)
        py = loads(result)
        if 'result' in py and 'value' in py['result']:
            return py['result']['value']
        else:
            raise ValueError

    