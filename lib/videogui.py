import kodi
from lib.language import Language
from lib.videoitem import VideoItem
from subtitleresult import SubtitleResult

class VideoGui:
    def __init__(self):
        self._init_vars()
                    
    def __enter__(self):
        return self

    def _init_vars(self):
        self.window = kodi.get_window(10025)  # MyVideoNav.xml (videolibrary)
        self.dialogwindow = kodi.get_window(12003)  # DialogVideoInfo.xml (movieinformation)
        self.language = Language()
        self.videoitem = VideoItem()
        self.present_text=""
        self.not_present_text =""
        self.search_text =""

    def set_gui_params(self, params):
        self.present_text = params.get('availabereturnvalue', '')
        self.not_present_text = params.get('notavailablereturnvalue', '')
        self.search_text = params.get('searchreturnvalue', '')
        self.videoitem.set_parameter_listitem(params,self.language.language_iso_639_2)
    
    def set_subtitle_properties(self, subtitle_present):
        if subtitle_present == SubtitleResult.SEARCH:
            self.set_property('skinsubtitlechecker.available', self.search_text)
        elif subtitle_present == SubtitleResult.AVAILABLE:
            kodi.log(__name__, 'subtitle found.')
            self.set_property('skinsubtitlechecker.available', self.present_text)
        elif subtitle_present == SubtitleResult.NOT_AVAILABLE:
            kodi.log(__name__, 'no subtitle found')
            self.set_property('skinsubtitlechecker.available', self.not_present_text)
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
        if not self.is_scrolling() and (self.is_movie() or self.is_episode()):
            return self.videoitem.current_item_changed(self.language.language_iso_639_2)
        else: 
            # clear subtitle check if not movie or episode or if scrolling
            self.set_subtitle_properties(SubtitleResult.HIDE)
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
        kodi.log(__name__,'set videolibray property %s with %s' %(name, value))
        self.window.setProperty(name, value)

    def set_dialogvideoinfo_property(self, name, value):
        kodi.log(__name__,'set video dialog property %s with %s' %(name, value))
        self.dialogwindow.setProperty(name, value)
    
    def clear_property(self, name):
        self.clear_videolibrary_property(name)
        self.clear_dialogvideoinfo_property(name)

    def clear_videolibrary_property(self, name):
        self.window.clearProperty(name)

    def clear_dialogvideoinfo_property(self, name):
        self.dialogwindow.clearProperty(name)

    def is_property_videolibrary_empty(self, value):
        return kodi.get_condition_visibility('IsEmpty(Window(videolibrary).Property(%s))' % (value))

    def is_property_dialogvideoinfo_empty(self, value):
        return kodi.get_condition_visibility('IsEmpty(Window(movieinformation).Property(%s))' % (value))

    def is_scrolling(self):
        return kodi.get_condition_visibility("Container.Scrolling")

    def is_movie(self):
        return kodi.get_condition_visibility("Container.Content(movies)")

    def is_episode(self):
        return kodi.get_condition_visibility("Container.Content(episodes)")

    def videolibray_is_visible(self):
        return kodi.get_condition_visibility("Window.IsVisible(videolibrary)")

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up_language(exc_type, exc_value, traceback)
        self.clean_up_videoitem(exc_type, exc_value, traceback)
        self.window = None
        self.dialogwindow = None
        self.not_present_text = None
        self.present_text = None
        self.search_text = None
        del self.window
        del self.dialogwindow
        del self.not_present_text
        del self.present_text
        del self.search_text

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
        