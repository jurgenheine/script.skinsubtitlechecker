# -*- coding: utf-8 -*-
import os
import time
import urllib2
import re
import xbmcvfs
import htmlentitydefs
from skinsubtitleresult import SubtitleResult
import skinsubtitlekodi as kodi
from skinsubtitlelanguage import LanguageHelper

BASE_URL = 'http://www.addic7ed.com'
USER_AGENT = "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"


class Adic7edServer_TVShows():

    def __init__(self):
        self.languagehelper = LanguageHelper()

    def __enter__(self):
        return self

    def __get_tvshow_id(self, title, year=None):
        match_title = title.lower()
        
        html = self.__get_cached_url(BASE_URL)
        regex = re.compile('option\s+value="(\d+)"\s*>(.*?)</option')
        site_matches = []
        for item in regex.finditer(html):
            tvshow_id, site_title = item.groups()

            # strip year off title and assign it to year if it exists
            r = re.search('(\s*\((\d{4})\))$', site_title)
            if r:
                site_title = site_title.replace(r.group(1), '')
                site_year = r.group(2)
            else:
                site_year = None

            # print 'show: |%s|%s|%s|' % (tvshow_id, site_title, site_year)
            if match_title == site_title.lower():
                if year is None or year == site_year:
                    return tvshow_id

                site_matches.append((tvshow_id, site_title, site_year))

        if not site_matches:
            return None
        elif len(site_matches) == 1:
            return site_matches[0][0]
        else:
            # there were multiple title matches and year was passed but no
            # exact year matches found
            for match in site_matches:
                # return the match that has no year specified
                if match[2] is None:
                    return match[0]

    def __get_subtitles(self, tvshow_id, searchseason, searchepisode, langs):
        url = BASE_URL + '/ajax_loadShow.php?show=%s&season=%s&langs=&hd=%s&hi=%s' % (tvshow_id, searchseason, 0, 0)
        html = self.__get_cached_url(url)
 
        regex = re.compile('<td>(\d+)</td><td>(\d+)</td><td>.*?</td><td>(.*?)</td><td.*?>(.*?)</td>.*?<td.*?>(.+?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?><a\s+href="(.*?)">.+?</td>',
                           re.DOTALL)
        for match in regex.finditer(html):
            season, episode, srt_lang, version, completed, hi, corrected, hd, srt_url = match.groups()
            try:
                lang = self.languagehelper.get_ISO_639_2(srt_lang)
            except:
                lang =  ''
            if completed.lower() == 'completed' and lang != '' and (lang in langs) and episode == searchepisode and season == searchseason:
                return SubtitleResult.AVAILABLE
        return SubtitleResult.NOT_AVAILABLE

    def __get_cached_url(self, url):
        kodi.log(__name__, 'Fetching Cached URL: %s' % url, kodi.LOGDEBUG)
        req = urllib2.Request(url)

        host = BASE_URL.replace('http://', '')
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Host', host)
        req.add_header('Referer', BASE_URL)
        try:
            response = urllib2.urlopen(req, timeout=10)
            html = response.read()
            html = self.__cleanse_title(html)
        except Exception as e:
            kodi.log(__name__, 'Failed to connect to URL %s: (%s)' % (url, e), kodi.LOGDEBUG)
            return ''

        return html

    def __cleanse_title(self, text):
        def fixup(m):
            text = m.group(0)
            if not text.endswith(';'): text += ';'
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                
                except KeyError:
                    pass

            # replace nbsp with a space
            text = text.replace(u'\xa0', u' ')
            return text
    
        if isinstance(text, str):
            try: text = text.decode('utf-8')
            except:
                try: text = text.decode('utf-8', 'ignore')
                except: pass
    
        return re.sub("&(\w+;|#x?\d+;?)", fixup, text.strip())

    def searchsubtitles(self, item):
        # noinspection PyBroadException
        try:
            if item['tvshow']:
                tvshow_id = self.__get_tvshow_id(item['tvshow'])
                return self.__get_subtitles(tvshow_id, item['season'], item['episode'], item['3let_language'])
            else:
                return SubtitleResult.NOT_AVAILABLE
        except Exception as e:
            kodi.log(__name__, 'failed to connect to Addic7ed service for subtitle search (%s)' % e, kodi.LOGNOTICE)
            return SubtitleResult.NOT_AVAILABLE

    def __exit__(self, exc_type, exc_value, traceback):
        self.languagehelper = None
        del self.languagehelper
