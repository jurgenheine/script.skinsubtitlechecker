# -*- coding: utf-8 -*- 
# Based on contents from https://github.com/amet/service.subtitles.opensubtitles

import xmlrpclib
import skinsubtitlekodi as kodi
from skinsubtitlesetting import Setting
from skinsubtitleresult import SubtitleResult

__scriptname__ = "XBMC Subtitles"

class OSDBServer:

    def __init__( self, *args, **kwargs ):
        self.base_url = u"http://api.opensubtitles.org/xml-rpc"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.base_url = None
        del self.base_url
        
    def searchsubtitles( self, item):
        try:
            server = xmlrpclib.Server( self.base_url, verbose=0 )
            setting =Setting()
            login = server.LogIn(setting.get_setting( "OSuser" ), setting.get_setting( "OSpass" ), "en", "%s_v%s" %(__scriptname__.replace(" ","_"),kodi.get_version()))
            osdb_token  = login[ "token" ]
            
            if ( osdb_token ) :
                searchlist  = []
        
                if len(item['tvshow']) > 0:
                    OS_search_string = ("%s S%.2dE%.2d" % (item['tvshow'],
                                                        int(item['season']),
                                                        int(item['episode']),)
                                                      ).replace(" ","+")      
                else:
                    OS_search_string = item['title'].replace(" ","+")
                
                kodi.log( __name__ , "Search String [ %s ]" % (OS_search_string,))
        
                searchlist = [{'sublanguageid':",".join(item['3let_language']),
                               'query'        :OS_search_string
                              }]
        
                search = server.SearchSubtitles( osdb_token, searchlist )
                server.__close()
                if search["data"]:
                    return SubtitleResult.AVAILABLE
            return SubtitleResult.NOT_AVAILABLE
        except Exception as e:
            kodi.log(__name__, "failed to connect to Opensubtitles service for subtitle search", kodi.LOGNOTICE)
            kodi.log(__name__, "Opensubtitles error:" + str(e))
            return SubtitleResult.NOT_AVAILABLE