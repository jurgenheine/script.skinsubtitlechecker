import xbmc
from lib.properties import Properties
from lib.setting import Setting
 
class Language:
    def __init__(self):
        self.preferredsub = None
        self.init_languages()
        self.settings = Setting()
        self.subtitlelanguage = self.settings.get_kodi_setting('locale.subtitlelanguage')
                    
    def __enter__(self):
        return self

    def set_language(self):
        self.set_language_properties(self.subtitlelanguage)
    
    def reset_language(self):
        self.set_language_properties("")

    def set_language_properties(self, lan):
        if lan == "Portuguese (Brazil)":
            self.preferredsub = "pob"
        elif lan == "Greek":
            self.preferredsub = "ell"
        elif lan == "":
            self.preferredsub = ""
        else:
            self.preferredsub = xbmc.convertLanguage(lan, xbmc.ISO_639_2)

        if lan =="":
            language_iso_639_1 = ""
            language_iso_639_2t = ""
            language_iso_639_2b = ""
        
        else:
            language_iso_639_1 = xbmc.convertLanguage(lan, xbmc.ISO_639_1)
            language_iso_639_2t = self.get_ISO_639_2_T(self.preferredsub)
            language_iso_639_2b = self.get_ISO_639_2_B(self.preferredsub)
        
        with Properties() as properties:
            properties.set_property('skinsubtitlechecker.language.full', lan)
            properties.set_property('skinsubtitlechecker.language.iso_639_1', language_iso_639_1)
            properties.set_property('skinsubtitlechecker.language.iso_639_2t', language_iso_639_2t)
            properties.set_property('skinsubtitlechecker.language.iso_639_2b', language_iso_639_2b)
            properties.set_property('skinsubtitlechecker.language.iso_639_2_kodi', self.preferredsub)
            
    def get_ISO_639_2_B(self, iso_639_2_code):
        for x in self.languages:
            if iso_639_2_code == x[2] or iso_639_2_code == x[3]:
                return x[2]

    def get_ISO_639_2_T(self, iso_639_2_code):
        for x in self.languages:
            if iso_639_2_code == x[2] or iso_639_2_code == x[3]:
                return x[3]

    def __exit__(self, exc_type, exc_value, traceback):
        self.settings.__exit__(exc_type, exc_value, traceback)

        self.settings=None
        self.preferredsub = None
        self.languages = None
        del self.preferredsub
        del self.languages
        del self.settings

    def init_languages(self):
       self.languages = (

                            # Full Language name[0]       ISO 639-1          ISO 639-2B             ISO 639-2T

                            ("Albanian"                   , "sq",            "alb",                 "sqi"  ),
                            ("Armenian"                   , "hy",            "arm",                 "hye"  ),
                            ("Basque"                     , "eu",            "baq",                 "eus"  ),
                            ("Burmese"                    , "my",            "bur",                 "mya"  ),
                            ("Chinese"                    , "zh",            "chi",                 "zho"  ),
                            ("Czech"                      , "cs",            "cze",                 "ces"  ),
                            ("Dutch"                      , "nl",            "dut",                 "nld"  ),
                            ("French"                     , "fr",            "fre",                 "fra"  ),
                            ("Georgian"                   , "ka",            "geo",                 "kat"  ),
                            ("German"                     , "de",            "ger",                 "deu"  ),
                            ("Greek"                      , "el",            "gre",                 "ell"  ),
                            ("Icelandic"                  , "is",            "ice",                 "isl"  ),
                            ("Persian"                    , "fa",            "per",                 "fas"  ),
                            ("Macedonian"                 , "mk",            "mac",                 "mkd"  ),
                            ("Malay"                      , "ms",            "may",                 "msa"  ),
                            ("Maori"                      , "mi",            "mao",                 "mri"  ),
                            ("Romanian"                   , "ro",            "rum",                 "ron"  ),
                            ("Slovak"                     , "sk",            "slo",                 "slk"  ),
                            ("Tibetan"                    , "bo",            "tib",                 "bod"  ),
                            ("Welsh"                      , "cy",            "wel",                 "cym"  ),
                        )