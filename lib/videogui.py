import skinsubtitlekodi as kodi
from lib.language import Language
from lib.videoitem import VideoItem
from skinsubtitleresult import SubtitleResult
from skinsubtitlesetting import Setting
from skinsubtitlenotificationmethod import NotificationMethod

class VideoGui:
    def __init__(self):
        self._init_vars()
                    
    def __enter__(self):
        return self

    def _init_vars(self):
        self.window = kodi.get_window(10025)  # MyVideoNav.xml (videos)
        self.dialogwindow = kodi.get_window(12003)  # DialogVideoInfo.xml (movieinformation)
        self.language = Language()
        self.videoitem = VideoItem()
        with Setting() as settings:
            self.notification_method = settings.get_notification_method()
            self.notification_duration = settings.get_notification_duration()
        if (self.notification_method == NotificationMethod.AUTO):
            self.set_property('skinsubtitlechecker.skinsupport', str(False))
            kodi.log(__name__, 'Skin support set to Auto')
        elif(NotificationMethod.POPUP):
            self.set_property('skinsubtitlechecker.skinsupport', str(False))
            kodi.log(__name__, 'Skin support set to Pop-up')
        else:  
            self.set_property('skinsubtitlechecker.skinsupport', str(True))
            kodi.log(__name__, 'notification set to skin support')

    def set_gui_params(self, params,skinsupport):
        if(self.notification_method == NotificationMethod.AUTO):
            self.set_property('skinsubtitlechecker.skinsupport', str(skinsupport))
            if (skinsupport == True):
                kodi.log(__name__, 'notification set by skin to skin support')    
            else:  
                kodi.log(__name__, 'notification set by skin to Pop-up ') 

        self.set_property('skinsubtitlechecker.search_text', params.get('searchreturnvalue', ''))
        self.set_property('skinsubtitlechecker.present_text', params.get('availabereturnvalue', ''))
        self.set_property('skinsubtitlechecker.not_present_text', params.get('notavailablereturnvalue', ''))
        self.videoitem.set_parameter_listitem(params,self.language.language_iso_639_2)
    
    def show_subtitle(self, subtitle_present):
        if(self.get_skin_support() == True):
            self.set_subtitle_properties(subtitle_present)
        else:
            self.send_subtitle_notification(subtitle_present)

    def send_subtitle_notification(self, subtitle_present):
        if subtitle_present == SubtitleResult.SEARCH:
            header = kodi.get_localized_string(32016)
        elif subtitle_present == SubtitleResult.AVAILABLE:
            header = kodi.get_localized_string(32014)
        elif subtitle_present == SubtitleResult.NOT_AVAILABLE:
            header = kodi.get_localized_string(32015)
        else: 
            return
        caption = self.language.language_iso_639_2t + " " + header
        message = self.videoitem.item['title']
        if self.is_episode():
            message = self.videoitem.item['tvshow'] + ", " + message + " S" + self.videoitem.item['season'] + "E" + self.videoitem.item['episode']

        kodi.send_notification(caption, message, self.notification_duration)

    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == SubtitleResult.SEARCH:
            self.set_property('skinsubtitlechecker.available', self.get_search_text())
        elif subtitle_present == SubtitleResult.AVAILABLE:
            kodi.log(__name__, 'subtitle found.')
            self.set_property('skinsubtitlechecker.available', self.get_present_text())
        elif subtitle_present == SubtitleResult.NOT_AVAILABLE:
            kodi.log(__name__, 'no subtitle found')
            self.set_property('skinsubtitlechecker.available', self.get_not_present_text())
        else:
            kodi.log(__name__, 'no subtitle search for item')
            self.reset_property('skinsubtitlechecker.available')
        self.set_language_properties(subtitle_present)

    def set_language_properties(self, subtitle_present):
        if(subtitle_present == SubtitleResult.HIDE):
            self.reset_property('skinsubtitlechecker.language.full')
            self.reset_property('skinsubtitlechecker.language.iso_639_1')
            self.reset_property('skinsubtitlechecker.language.iso_639_2t')
            self.reset_property('skinsubtitlechecker.language.iso_639_2b')
            self.reset_property('skinsubtitlechecker.language.iso_639_2_kodi')
        else:
            self.set_property('skinsubtitlechecker.language.full', self.language.language_full)
            self.set_property('skinsubtitlechecker.language.iso_639_1', self.language.language_iso_639_1)
            self.set_property('skinsubtitlechecker.language.iso_639_2t', self.language.language_iso_639_2t)
            self.set_property('skinsubtitlechecker.language.iso_639_2b', self.language.language_iso_639_2b)
            self.set_property('skinsubtitlechecker.language.iso_639_2_kodi', self.language.language_iso_639_2)

    def get_search_languages(self):
        return self.language.language_iso_639_2

    def get_video_item(self):
        return self.videoitem.item

    def subtitlecheck_needed(self):
        if (not self.is_scrolling() and (self.movieinformation_is_visible() or self.videolibray_is_visible()) and (self.is_movie() or self.is_episode())):
            return self.videoitem.current_item_changed(self.language.language_iso_639_2)
        else: 
            # clear subtitle check if not movie or episode or if scrolling
            self.show_subtitle(SubtitleResult.HIDE)
            return False

    def is_running_backend(self):
        return not self.is_property_videolibrary_empty("skinsubtitlechecker.backend_running")

    def set_running_backend(self):
        self.set_videolibrary_property("skinsubtitlechecker.backend_running","true")

    def reset_running_backend(self):
        self.clear_videolibrary_property("skinsubtitlechecker.backend_running")

    def reset_property(self, name):
        self.set_videolibrary_property(name, "")
        self.set_dialogvideoinfo_property(name, "")

    def set_property(self, name, value):
        self.set_videolibrary_property(name, value)
        self.set_dialogvideoinfo_property(name, value)

    def set_videolibrary_property(self, name, value):
        kodi.log(__name__,'set videolibray property %s with %s' % (name, value))
        self.window.setProperty(name, value)

    def set_dialogvideoinfo_property(self, name, value):
        kodi.log(__name__,'set video dialog property %s with %s' % (name, value))
        self.dialogwindow.setProperty(name, value)
    
    def clear_property(self, name):
        self.clear_videolibrary_property(name)
        self.clear_dialogvideoinfo_property(name)

    def clear_videolibrary_property(self, name):
        self.window.clearProperty(name)

    def clear_dialogvideoinfo_property(self, name):
        self.dialogwindow.clearProperty(name)

    def get_search_text(self):
        return self.get_property('skinsubtitlechecker.search_text')

    def get_present_text(self):
            return self.get_property('skinsubtitlechecker.present_text')

    def get_not_present_text(self):
            return self.get_property('skinsubtitlechecker.not_present_text')

    def get_skin_support(self):
            skinsupport = self.get_property('skinsubtitlechecker.skinsupport')
            if skinsupport == "":
                return False
            return skinsupport.lower() =='true'

    def get_property(self,name):
        if(self.videolibray_is_visible()):
            return self.get_videolibrary_property(name)
        return self.get_dialogvideoinfo_property(name)
    
    def get_videolibrary_property(self, name):
        propvalue = self.window.getProperty(name)
        kodi.log(__name__,'videolibray property %s = %s' % (name, propvalue))
        return propvalue

    def get_dialogvideoinfo_property(self, name):
        propvalue = self.dialogwindow.getProperty(name)
        kodi.log(__name__,'get videolibray property %s = %s' % (name, propvalue))
        return propvalue

    def is_property_videolibrary_empty(self, value):
        return self.window.getProperty(value) == "";
        #return kodi.get_condition_visibility('IsEmpty(Window(10025).Property(%s))' % (value))

    def is_property_dialogvideoinfo_empty(self, value):
        return self.window.getProperty(value) == "";
        #return kodi.get_condition_visibility('IsEmpty(Window(12003).Property(%s))' % (value))

    def is_scrolling(self):
        return kodi.get_condition_visibility("Container.Scrolling")

    def is_movie(self):
        return kodi.get_condition_visibility("Container.Content(movies)")

    def is_episode(self):
        return kodi.get_condition_visibility("Container.Content(episodes)")

    def videolibray_is_visible(self):
        if kodi.get_kodi_version() < 17:
            return kodi.get_condition_visibility("Window.IsVisible(videolibrary)")
        else:
            return kodi.get_condition_visibility("Window.IsVisible(videos)")

    def movieinformation_is_visible(self):
        return kodi.get_condition_visibility("Window.IsVisible(movieinformation)")

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up_language(exc_type, exc_value, traceback)
        self.clean_up_videoitem(exc_type, exc_value, traceback)
        self.window = None
        self.dialogwindow = None
        del self.window
        del self.dialogwindow

    def clean_up_language(self, exc_type, exc_value, traceback):
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the language class, it is not
            # used within with statement
            self.language.__exit__(exc_type, exc_value, traceback)
            self.language = None
            del self.language
        except:
            # database is not yet set
            pass

    def clean_up_videoitem(self, exc_type, exc_value, traceback):
        # noinspection PyBroadException
        try:    
            # call explicit the exit function of the videoitem class, it is not
            # used within with statement
            self.videoitem.__exit__(exc_type, exc_value, traceback)
            self.videoitem = None
            del self.videoitem
        except:
            # database is not yet set
            pass
        