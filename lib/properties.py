import xbmcgui

class Properties:
    def __init__(self):
        self._init_vars()
                    
    def __enter__(self):
        return self

    def _init_vars(self):
        self.window = xbmcgui.Window(10025)  # MyVideoNav.xml (videolibrary)
        self.dialogwindow = xbmcgui.Window(12003)  # DialogVideoInfo.xml (movieinformation)

    def set_property(self,name, value):
        self.window.setProperty(name, value)
        self.dialogwindow.setProperty(name,value)

    def __exit__(self, exc_type, exc_value, traceback):
        self.window = None
        self.dialogwindow = None
        del self.window
        del self.dialogwindow