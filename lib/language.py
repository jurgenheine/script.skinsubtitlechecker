import skinsubtitlekodi as kodi
from skinsubtitlesetting import Setting
from skinsubtitlelanguage import LanguageHelper

class Language:
    def __init__(self):
        self.languagehelper = LanguageHelper()
        self.searchlanguages = []
        self.__set_searchlanguages()
        if(self.searchlanguages):
            for slang in self.searchlanguages:
                if slang != "" and slang != None:
                    self.__set_subtitlelanguages(slang)
                    break
        else:
            self.set_subtitlelanguages("")
                    
    def __enter__(self):
        return self

    def __set_searchlanguages(self):
        with Setting() as settings:
            lan = settings.get_kodi_setting('locale.subtitlelanguage')
            langs= settings.get_kodi_setting('subtitles.languages')
        intlan = kodi.get_interface_language()
        self.searchlanguages = []
        if(lan != "" and lan != None):
            self.searchlanguages.append(self.languagehelper.get_ISO_639_2(lan))
        
        if langs != None:
            for lang in langs:
                if( lang !="" and lang != None and lang not in self.searchlanguages):
                    #add language if not empty and not already exist
                    self.searchlanguages.append(self.languagehelper.get_ISO_639_2(lang))
        
        if(intlan != "" and intlan != None and intlan not in self.searchlanguages):
            self.searchlanguages.append(self.languagehelper.get_ISO_639_2(intlan))

    def __set_subtitlelanguages(self, lan):
        if lan == "":
            self.language_full = ""
            self.language_iso_639_1 = ""
            self.language_iso_639_2 = ""
            self.language_iso_639_2t = ""
            self.language_iso_639_2b = ""
        else:
            self.language_full = self.languagehelper.get_english_name(lan)
            self.language_iso_639_1 = kodi.convert_language(self.language_full, kodi.ISO_639_1)
            self.language_iso_639_2 = kodi.convert_language(self.language_full, kodi.ISO_639_2)
            self.language_iso_639_2t = self.languagehelper.get_ISO_639_2_T(self.language_iso_639_2)
            self.language_iso_639_2b = self.languagehelper.get_ISO_639_2_B(self.language_iso_639_2)

    def __exit__(self, exc_type, exc_value, traceback):
        self.preferedsub= None
        self.language_iso_639_2 = None
        self.language_iso_639_1 = None
        self.language_iso_639_2t = None
        self.language_iso_639_2b = None
        self.searchlanguages = None

        del self.preferedsub
        del self.language_iso_639_2
        del self.language_iso_639_1
        del self.language_iso_639_2t
        del self.language_iso_639_2b
        del self.searchlanguages
