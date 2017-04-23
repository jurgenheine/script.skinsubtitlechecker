import os
import time
import skinsubtitlekodi as kodi
from skinsubtitlesetting import Setting
from sqlite3 import dbapi2
from sqlite3 import OperationalError as OperationalError
from sqlite3 import DatabaseError as DatabaseError


class DatabaseRecoveryError(Exception):
    pass

MAX_TRIES = 5


class DBConnection():
    def __init__(self):
        self.db = None
        self.settings = Setting()
        db_dir = kodi.translate_path("special://database")
        self.db_path = os.path.join(db_dir, 'subtitlecheckercache.db')
        self.db_lib = dbapi2
        if not kodi.file_exists(self.db_path):
                self.__create_db()
        else:
            self.__connect_to_db()
            self.__update_database()
            

    def __enter__(self):
        return self

    def flush_subtitle_cache(self):
        sql = 'DELETE FROM subtitle_cache'
        self.__execute(sql)
        self.__execute('VACUUM')

    def cleanup_subtitle_cache(self):
        now = time.time()
        minimal_timestamp_found_value = now - self.settings.get_cache_found_timeout()
        minimal_timestamp_not_found_value = now - self.settings.get_cache_not_found_timeout()
        sql = 'DELETE FROM subtitle_cache WHERE ( timestamp < ? AND subtitle < 1) OR ( timestamp < ? AND subtitle > 0)'
        self.__execute(sql, (minimal_timestamp_not_found_value, minimal_timestamp_found_value))
        self.__execute('VACUUM')

    def cache_subtitle(self, item, subtitle_present):
        now = time.time()
        sql = 'REPLACE INTO subtitle_cache (year, season, episode, tvshow, title, filename, subtitle, timestamp) VALUES(?, ?, ?, ?, ?, ?, ?, ?)'
        self.__execute(sql, (item['year'], item['season'], item['episode'], item['tvshow'], item['title'], item['filename'],int(subtitle_present), now))

    def delete_cached_subtitle(self, item):
        sql = 'DELETE FROM subtitle_cache WHERE year = ? AND season = ? AND episode = ? AND tvshow = ? AND title = ? AND filename = ?'
        self.__execute(sql, (item['year'], item['season'], item['episode'], item['tvshow'], item['title'], item['filename']))
        
    def get_cached_subtitle(self, item):
        created = 0
        now = time.time()
        limit_found = self.settings.get_cache_found_timeout()
        limit_not_found = self.settings.get_cache_not_found_timeout()
        sql = 'SELECT timestamp, subtitle FROM subtitle_cache WHERE year = ? AND season = ? AND episode = ? AND tvshow = ? AND title = ? AND filename = ?'
        rows = self.__execute(sql, (item['year'], item['season'], item['episode'], item['tvshow'], item['title'], item['filename']))

        if rows:
            created = float(rows[0][0])
            subtitle_present = int(rows[0][1])
            createddate = time.ctime(created)
            age = now - created
            if age < limit_not_found and subtitle_present < 1:
                kodi.log(__name__, 'DB Cache: Item: %s, Cache Hit: True, created: %s, age: %s hour, limit: False' % (item, createddate, (now - created)/ 3600), kodi.LOGDEBUG)
                return subtitle_present
            elif age < limit_found and subtitle_present == 1:
                kodi.log(__name__, 'DB Cache: Item: %s, Cache Hit: True, created: %s, age: %s days, limit: False' % (item, createddate, (now - created)/ 3600/ 24), kodi.LOGDEBUG)
                return subtitle_present
            elif age >= limit_found and subtitle_present == 1:
                kodi.log(__name__, 'DB Cache: Item: %s, Cache Hit: True, created: %s, age: %s days, limit: True' % (item, createddate, (now - created)/ 3600/ 24), kodi.LOGDEBUG)
                self.delete_cached_subtitle(item)
            else:
                kodi.log(__name__, 'DB Cache: Item: %s, Cache Hit: True, created: %s, age: %s, limit: True' % (item, createddate, (now - created)/ 3600), kodi.LOGDEBUG)
                self.delete_cached_subtitle(item)
        else:
            kodi.log(__name__, 'DB Cache: Item: %s, Cache Hit: False' % (item), kodi.LOGDEBUG)
        return -1
   
    def flush_provider_cache(self):
        sql = 'DELETE FROM provider_cache'
        self.__execute(sql)
        self.__execute('VACUUM')

    def cache_provider(self, addonid):
        sql = 'REPLACE INTO provider_cache (addonid) VALUES(?)'
        self.__execute(sql, (addonid))

    def delete_cached_provider(self, addonid):
        sql = 'DELETE FROM provider_cache WHERE addonid = ?'
        self.__execute(sql, (addonid))

    def get_cached_providers(self):
        sql = 'SELECT addonid FROM provider_cache'
        rows = self.__execute(sql, (addonid))
        return rows

    def update_cached_providers(self, newaddonids):
        # first get current providers from cache
        currentaddonids= self.get_cached_providers()
        # add providers not in cache
        for addonid in newaddonids:
            if addonid not in currentaddonids:
                self.cache_provider(addonid)
        # remove providers from cache who are not installed anymore
        for addonid in currentaddonids:
            if addonid not in newaddonids:
                self.delete_cached_provider(addonid)
    
    def __init_database(self):
        # intended to be a common method for creating a db from scratch
        kodi.log(__name__, 'Building Subtitle checker Database', kodi.LOGDEBUG)
            
        self.__execute('PRAGMA journal_mode=WAL')
        self.__update_database()
 
    def __update_database(self):
        self.__execute('CREATE TABLE IF NOT EXISTS subtitle_cache (year TEXT, season TEXT, episode TEXT, tvshow TEXT, title TEXT, filename TEXT, subtitle INTEGER, timestamp, PRIMARY KEY(year, season, episode, tvshow, title, filename))')
        self.__execute('CREATE TABLE IF NOT EXISTS provider_cache (addonid TEXT , PRIMARY KEY(addonid))')

    def __close_db(self):
        try: self.db.close()
        except: pass
        self.db = None
        del self.db

    def __create_db(self):
        # noinspection PyBroadException
        try:
            self.db.close()
        except:
            pass
        self.db = None
        self.__create_sqlite_db()
        self.__connect_to_db()
        self.__init_database()

    def __execute(self, sql, params=None):
        if params is None:
            params = []

        rows = None
        sql = self.__format(sql)
        tries = 1
        while True:
            try:
                cur = self.db.cursor()
#                 kodi.log(__name__, 'Running: %s with %s' % (sql, params), kodi.LOGDEBUG)
                cur.execute(sql, params)
                if sql[:6].upper() == 'SELECT' or sql[:4].upper() == 'SHOW':
                    rows = cur.fetchall()
                cur.close()
                self.db.commit()
                return rows
            except OperationalError as e:
                if tries < MAX_TRIES:
                    tries += 1
                    kodi.log(__name__, 'Retrying (%s/%s) SQL: %s Error: %s' % (tries, MAX_TRIES, sql, e), kodi.LOGWARNING)
                    self.db = None
                    self.__connect_to_db()
                elif any(s for s in ['no such table', 'no such column'] if s in str(e)):
                    self.db.rollback()
                    raise DatabaseRecoveryError(e)
                else:
                    raise
            except DatabaseError as e:
                self.db.rollback()
                raise DatabaseRecoveryError(e)

    def __create_sqlite_db(self):
        if not kodi.file_exists(kodi.dirname(self.db_path)):
            kodi.mkdirs(kodi.dirname(self.db_path))
            
    def __connect_to_db(self):
        if not self.db:
            self.db = self.db_lib.connect(self.db_path)
            self.db.text_factory = str
            
    # apply formatting changes to make sql work with a particular db driver
    @staticmethod
    def __format(sql):
        if sql[:7] == 'REPLACE':
            sql = 'INSERT OR ' + sql

        return sql
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__close_db()
        self.settings.__exit__(exc_type, exc_value, traceback)
        self.db_lib = None
        self.db_path = None
        self.settings = None
        del self.db_lib
        del self.db_path 
        del self.settings