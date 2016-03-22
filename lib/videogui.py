from lib import kodi

class VideoGui:
    def __init__(self):
        self._init_vars()
                    
    def __enter__(self):
        return self

    def _init_vars(self):
        self.window = kodi.get_window(10025)  # MyVideoNav.xml (videolibrary)
        self.dialogwindow = kodi.get_window(12003)  # DialogVideoInfo.xml (movieinformation)

    def set_property(self, name, value):
        self.set_videolibrary_property(name, value)
        self.set_dialogvideoinfo_property(name, value)

    def set_videolibrary_property(self, name, value):
        self.window.setProperty(name, value)

    def set_dialogvideoinfo_property(self, name, value):
        self.dialogwindow.setProperty(name, value)

    def clear_videolibrary_property(self, name):
        self.window.clearProperty(name)

    def clear_dialogvideoinfo_property(self, name):
        self.dialogwindow.clearProperty(name)

    def property_videolibrary_empty(self, value):
        return kodi.get_condition_visibility('IsEmpty(Window(videolibrary).Property(%s))' % (value))

    def property_dialogvideoinfo_empty(self, value):
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
        self.window = None
        self.dialogwindow = None
        del self.window
        del self.dialogwindow