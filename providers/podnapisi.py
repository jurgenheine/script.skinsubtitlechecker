# -*- coding: utf-8 -*- 
# Based on contents from https://github.com/amet/service.subtitles.podnapisi

from xml.dom import minidom
import urllib
import skinsubtitlekodi as kodi
from skinsubtitleresult import SubtitleResult
from skinsubtitlelanguage import LanguageHelper

class PNServer:
    
    def __init__( self, *args, **kwargs ):
        self.languagehelper = LanguageHelper()
        self.search_url = "http://www.podnapisi.net/ppodnapisi/search?tbsl=1&sK=%s&sJ=%s&sY=%s&sTS=%s&sTE=%s&sXML=1&lang=0"
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.search_url = None
        self.languagehelper = None
        del self.search_url
        del self.languagehelper
                
    def searchsubtitles( self, item):
        try:
            if len(item['tvshow']) > 1:
                title = item['tvshow']
            else:
                title = item['title']
            langs= []
            for lang in item['3let_language']:
                lan = self.languagehelper.get_podnapisi_code(lang)
                langs.append(lan) 
                
            if title:
                #todo fix language translation, get new list with correct translation
                url =  self.search_url % (title.replace(" ","+"),
                                       ','.join(langs),
                                       str(item['year']),
                                       str(item['season']), 
                                       str(item['episode'])
                                      )
                
                kodi.log( __name__ ,"Search URL - %s" % (url))
                
                subtitles = self.__fetch(url)
                
                if subtitles:
                    return SubtitleResult.AVAILABLE
            return SubtitleResult.NOT_AVAILABLE
        except:
            kodi.log(__name__, "failed to connect to Podnapisi service for subtitle search", kodi.LOGNOTICE)
            return SubtitleResult.NOT_AVAILABLE
  
    def __fetch(self,url):
        socket = urllib.urlopen( url )
        result = socket.read()
        socket.close()
        xmldoc = minidom.parseString(result)
        return xmldoc.getElementsByTagName("subtitle")   
    