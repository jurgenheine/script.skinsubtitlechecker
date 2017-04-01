import os
import time
import urllib2
import re
import xbmcvfs
from skinsubtitleresult import SubtitleResult
import skinsubtitlekodi as kodi

BASE_URL = 'http://www.addic7ed.com'

class Adic7edServer_TVShows():
    def get_tvshow_id(self, title, year=None):
        match_title = title.lower()
        
        html = self.__get_cached_url(BASE_URL, 24)
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

    def get_subtitles(self, tvshow_id, searchseason, searchepisode, langs):
        url = BASE_URL + '/ajax_loadShow.php?show=%s&season=%s&langs=&hd=%s&hi=%s' % (tvshow_id, searchseason, 0, 0)
        html = self.__get_cached_url(url)
 
        regex = re.compile('<td>(\d+)</td><td>(\d+)</td><td>.*?</td><td>(.*?)</td><td.*?>(.*?)</td>.*?<td.*?>(.+?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?><a\s+href="(.*?)">.+?</td>',
                           re.DOTALL)
        for match in regex.finditer(html):
            season, episode, srt_lang, version, completed, hi, corrected, hd, srt_url = match.groups()
            try:
                lang = self.get_language_info(srt_lang)
            except:
                lang = {'name': '', '2let': '', '3let': ''}
            if completed.lower() == 'completed' and lang['3let'] != '' and (lang['3let'] in langs) and episode == searchepisode and season == searchseason:
                return SubtitleResult.AVAILABLE
        return SubtitleResult.NOT_AVAILABLE

    def __get_cached_url(self, url):
        kodi.log(__name__, 'Fetching Cached URL: %s' % url, log_utils.LOGDEBUG)
        req = urllib2.Request(url)

        host = BASE_URL.replace('http://', '')
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Host', host)
        req.add_header('Referer', BASE_URL)
        try:
            response = urllib2.urlopen(req, timeout=10)
            html = response.read()
            html = self.cleanse_title(html)
        except Exception as e:
            kodi.log(__name__, 'Failed to connect to URL %s: (%s)' % (url, e), kodi.LOGDEBUG)
            return ''

        return html

    def cleanse_title(self, text):
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

    @staticmethod
    def get_language_info(language):
        for lang in LANGUAGES:
            if lang[0] == language:
                return {'name': lang[0], '2let': lang[2], '3let': lang[3]}

    def searchsubtitles(self, item):
        # noinspection PyBroadException
        try:
            if item['tvshow']:
                tvshow_id = self.get_tvshow_id(item['tvshow'])
                return self.get_subtitles(tvshow_id, item['season'], item['episode'], item['3let_language'])
            else:
                return SubtitleResult.NOT_AVAILABLE
        except:
            kodi.log(__name__, "failed to connect to Addic7ed service for subtitle search", kodi.LOGNOTICE)
            return SubtitleResult.NOT_AVAILABLE


LANGUAGES = (("Albanian", "29", "sq", "alb", "0", 30201),
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
  ("Espa�ol (Latinoam�rica)", "28", "es", "spa", "100", 30240),
  ("Espa�ol (Espa�a)", "28", "es", "spa", "100", 30240),
  ("Spanish (Latin America)", "28", "es", "spa", "100", 30240),
  ("Espa�ol", "28", "es", "spa", "100", 30240),
  ("SerbianLatin", "36", "sr", "scc", "100", 30237),
  ("Spanish (Spain)", "28", "es", "spa", "100", 30240),
  ("Chinese (Traditional)", "17", "zh", "chi", "100", 30207),
  ("Chinese (Simplified)", "17", "zh", "chi", "100", 30207))
