from lib import kodi

class VideoItem:

    def __init__(self):
        self.item = None
                    
    def __enter__(self):
        return self

    @staticmethod
    def item_not_empty(newitem):
        if(newitem['title'] == "" and newitem['tvshow'] == ""):
            # no item data for search
            return False
        return True
    
    def item_changed(self, newitem):
        if(self.item['year'] != newitem['year'] or self.item['season'] != newitem['season'] or self.item['episode'] != newitem['episode'] or self.item['tvshow'] != newitem['tvshow'] or self.item['title'] != newitem['title'] or self.item['filename'] != newitem['filename']):
            return True
        return False

    def current_item_changed(self,language_iso_639_2):
        newitem = self.get_current_listitem(language_iso_639_2)
        if self.item_not_empty(newitem) and (not self.item or self.item_changed(newitem)):
            self.item = newitem
            return True
        return False

    def get_current_listitem(self,language_iso_639_2):
        return self.create_item(kodi.get_info_label("ListItem.Year"), 
                                kodi.get_info_label("ListItem.Season"), 
                                kodi.get_info_label("ListItem.Episode"), 
                                kodi.get_info_label("ListItem.TVShowTitle"),
                                kodi.get_info_label("ListItem.OriginalTitle"), 
                                kodi.get_info_label("ListItem.Title"),
                                kodi.get_info_label("ListItem.FileName"))
    
    def set_parameter_listitem(self, params,language_iso_639_2):
        self.item = self.create_item(params.get('year', ''),
                                     params.get('season', ''),
                                     params.get('episode', ''),
                                     params.get('tvshow', ''),
                                     params.get('originaltitle', ''),
                                     params.get('title', ''),
                                     params.get('filename', ''))

    def create_item(self, year, season, episode, tvshow, originaltitle, title, filename,language_iso_639_2):
        item = {'year': kodi.normalize_string(year),  # Year
                'season': kodi.normalize_string(season),  # Season
                'episode': kodi.normalize_string(episode),  # Episode
                'tvshow': kodi.normalize_string(tvshow),
                'title': kodi.normalize_string(originaltitle),  # try to get original title
                'filename': kodi.normalize_string(filename),
                '3let_language': []}

        item['3let_language'].append(language_iso_639_2)
#         log(__name__, "3let language: %s" % item['3let_language'])
        
        if item['title'] == "":
            item['title'] = kodi.normalize_string(title)      # no original title, get just Title
        
        if item['year'] == "":
            item['title'], year = kodi.get_clean_movie_title(item['title'])
            item['year'] = str(year)
                    
        if item['episode'].lower().find("s") > -1:  # Check if season is "Special"
            item['season'] = "0"
            item['episode'] = item['episode'][-1:]
        
        return item

    def __exit__(self, exc_type, exc_value, traceback):
        self.item = None
        del self.item

