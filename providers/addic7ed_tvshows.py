# -*- coding: utf-8 -*-
# Based on contents from https://github.com/cflannagan/service.subtitles.addic7ed

import urllib
import urllib2
import re
import socket
import string
from BeautifulSoup import BeautifulSoup
from skinsubtitleresult import SubtitleResult
import skinsubtitlekodi as kodi

class Adic7edServer:
    def __init__(self, *args, **kwargs):
        self.host = "http://www.addic7ed.com"
        self.release_pattern = re.compile("Version (.+), ([0-9]+).([0-9])+ MBs")

        self.req_headers = {'User-Agent':
                            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13',
                            'Referer':
                            'http://www.addic7ed.com'}
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.host = None
        self.release_pattern = None
        self.req_headers = None
        del self.host
        del self.release_pattern
        del self.req_headers
    
    def get_url(self, url):
        request = urllib2.Request(url, headers=self.req_headers)
        opener = urllib2.build_opener()
        response = opener.open(request)
        
        contents = response.read()
        return contents

    # Sometimes search fail because Addic7ed uses URLs that does not match the TheTVDB format.
    # This will probably grow to be a hardcoded colleciton over time. 
    @staticmethod
    def addic7ize(title):
        addic7ize_dict = eval(open(kodi.get_script_path()+ '/resources' + '/addic7ed_dict.txt').read())
        return addic7ize_dict.get(title, title)
    
    def query_tv_show(self, name, season, episode, langs):
        name = self.addic7ize(name).lower().replace(" ", "_")
        searchurl = "%s/serie/%s/%s/%s/addic7ed" % (self.host, name, season, episode)
        return self.query(searchurl, langs)

    def query_film(self, name, year, langs):
        name = urllib.quote(name.replace(" ", "_"))
        searchurl = "%s/film/%s_(%s)-Download" % (self.host, name, str(year))
        return self.query(searchurl, langs)

    def query(self, searchurl, langs):
        
        kodi.log(__name__, "Search URL - %s" % searchurl,kodi.LOGINFO)
        socket.setdefaulttimeout(10)
        request = urllib2.Request(searchurl, headers=self.req_headers)
        request.add_header('Pragma', 'no-cache')
        page = urllib2.build_opener().open(request)
        content = page.read()
        content = content.replace("The safer, easier way", "The safer, easier way \" />")
        soup = BeautifulSoup(content)
        
        for langs_html in soup("td", {"class": "language"}):
        
            try:
                fulllanguage = str(langs_html).split('class="language">')[1].split('<a')[0].replace("\n", "")

                # noinspection PyBroadException
                try:
                    lang = self.get_language_info(fulllanguage)
                except:
                    lang = {'name': '', '2let': '', '3let': ''}
                
                statustd = langs_html.findNext("td")
                status = statustd.find("b").string.strip()
                
                if status == "Completed" and lang['3let'] != '' and (lang['3let'] in langs):
                    return SubtitleResult.AVAILABLE
            except Exception as ex:
                kodi.log(__name__, "ERROR IN BS: %s" % str(ex))
                pass
        
        return SubtitleResult.NOT_AVAILABLE
   
    def search_filename(self, filename, languages):
        title, year = kodi.get_clean_movie_title(filename)
        kodi.log(__name__, "clean title: \"%s\" (%s)" % (title, year))
        try:
            yearval = int(year)
        except ValueError:
            yearval = 0
        if title and yearval > 1900:
            return self.query_film(title, year, languages)
        else:
            match = re.search(r'\WS(?P<season>\d\d)E(?P<episode>\d\d)', title, flags=re.IGNORECASE)
            if match is not None:
                tvshow = string.strip(title[:match.start('season')-1])
                season = string.lstrip(match.group('season'), '0')
                episode = string.lstrip(match.group('episode'), '0')
                return self.query_tv_show(tvshow, season, episode, languages)
            else:
                return SubtitleResult.NOT_AVAILABLE
    
    def searchsubtitles(self, item):
        # noinspection PyBroadException
        try:
            if item['tvshow']:
                return self.query_tv_show(item['tvshow'],
                                          item['season'],
                                          item['episode'],
                                          item['3let_language'])
            elif item['title']:
                return self.query_film(item['title'], item['year'], item['3let_language'])
            else:
                return self.search_filename(item['filename'], item['3let_language'])
        except:
            kodi.log(__name__, "failed to connect to Addic7ed service for subtitle search", kodi.LOGNOTICE)
            return SubtitleResult.NOT_AVAILABLE
        
    @staticmethod
    def get_language_info(language):
        for lang in LANGUAGES:
            if lang[0] == language:
                return {'name': lang[0], '2let': lang[2], '3let': lang[3]}
  
LANGUAGES = (
  ("Albanian", "29", "sq", "alb", "0", 30201),
  ("Arabic", "12", "ar", "ara", "1", 30202),
  ("Belarusian", "0", "hy", "arm", "2", 30203),
  ("Bosnian", "10", "bs", "bos", "3", 30204),
  ("Bulgarian", "33", "bg", "bul", "4", 30205),
  ("Catalan", "53", "ca", "cat", "5", 30206),
  ("Chinese", "17", "zh", "chi", "6", 30207),
  ("Croatian", "38", "hr", "hrv", "7", 30208),
  ("Czech", "7", "cs", "cze", "8", 30209),
  ("Danish", "24", "da", "dan", "9", 30210),
  ("Dutch", "23", "nl", "dut", "10", 30211),
  ("English", "2", "en", "eng", "11", 30212),
  ("Estonian", "20", "et", "est", "12", 30213),
  ("Persian", "52", "fa", "per", "13", 30247),
  ("Finnish", "31", "fi", "fin", "14", 30214),
  ("French", "8", "fr", "fre", "15", 30215),
  ("German", "5", "de", "ger", "16", 30216),
  ("Greek", "16", "el", "ell", "17", 30217),
  ("Hebrew", "22", "he", "heb", "18", 30218),
  ("Hindi", "42", "hi", "hin", "19", 30219),
  ("Hungarian", "15", "hu", "hun", "20", 30220),
  ("Icelandic", "6", "is", "ice", "21", 30221),
  ("Indonesian", "0", "id", "ind", "22", 30222),
  ("Italian", "9", "it", "ita", "23", 30224),
  ("Japanese", "11", "ja", "jpn", "24", 30225),
  ("Korean", "4", "ko", "kor", "25", 30226),
  ("Latvian", "21", "lv", "lav", "26", 30227),
  ("Lithuanian", "0", "lt", "lit", "27", 30228),
  ("Macedonian", "35", "mk", "mac", "28", 30229),
  ("Malay", "0", "ms", "may", "29", 30248),
  ("Norwegian", "3", "no", "nor", "30", 30230),
  ("Polish", "26", "pl", "pol", "31", 30232),
  ("Portuguese", "32", "pt", "por", "32", 30233),
  ("PortugueseBrazil", "48", "pb", "pob", "33", 30234),
  ("Romanian", "13", "ro", "rum", "34", 30235),
  ("Russian", "27", "ru", "rus", "35", 30236),
  ("Serbian", "36", "sr", "scc", "36", 30237),
  ("Slovak", "37", "sk", "slo", "37", 30238),
  ("Slovenian", "1", "sl", "slv", "38", 30239),
  ("Spanish", "28", "es", "spa", "39", 30240),
  ("Swedish", "25", "sv", "swe", "40", 30242),
  ("Thai", "0", "th", "tha", "41", 30243),
  ("Turkish", "30", "tr", "tur", "42", 30244),
  ("Ukrainian", "46", "uk", "ukr", "43", 30245),
  ("Vietnamese", "51", "vi", "vie", "44", 30246),
  ("BosnianLatin", "10", "bs", "bos", "100", 30204),
  ("Farsi", "52", "fa", "per", "13", 30247),
  ("English (US)", "2", "en", "eng", "100", 30212),
  ("English (UK)", "2", "en", "eng", "100", 30212),
  ("Portuguese (Brazilian)", "48", "pt-br", "pob", "100", 30234),
  ("Portuguese (Brazil)", "48", "pb", "pob", "33", 30234),
  ("Portuguese-BR", "48", "pb", "pob", "33", 30234),
  ("Brazilian", "48", "pb", "pob", "33", 30234),
  ("Español (Latinoamérica)", "28", "es", "spa", "100", 30240),
  ("Español (España)", "28", "es", "spa", "100", 30240),
  ("Spanish (Latin America)", "28", "es", "spa", "100", 30240),
  ("Español", "28", "es", "spa", "100", 30240),
  ("SerbianLatin", "36", "sr", "scc", "100", 30237),
  ("Spanish (Spain)", "28", "es", "spa", "100", 30240),
  ("Chinese (Traditional)", "17", "zh", "chi", "100", 30207),
  ("Chinese (Simplified)", "17", "zh", "chi", "100", 30207))
