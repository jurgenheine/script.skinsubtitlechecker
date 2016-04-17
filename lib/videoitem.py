import kodi
from basevideoitem import BaseVideoItem

class VideoItem(BaseVideoItem):

    def __init__(self):
        pass
                    
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
                                kodi.get_info_label("ListItem.FileName"),
                                language_iso_639_2)
    

    def __exit__(self, exc_type, exc_value, traceback):
        pass

