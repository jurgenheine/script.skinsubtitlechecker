from lib import kodi
from lib.setting import Setting
 
class Language:
    def __init__(self):
        self.init_languages()
        self.settings = Setting()
        self.set_subtitlelanguages()
                    
    def __enter__(self):
        return self

    def set_subtitlelanguages(self):
        lan = self.settings.get_kodi_setting('locale.subtitlelanguage')

        if lan == "":
            self.language_full = ""
            self.language_iso_639_1 = ""
            self.language_iso_639_2 = ""
            self.language_iso_639_2t = ""
            self.language_iso_639_2b = ""
        else:
            self.language_full = kodi.convert_language(lan, kodi.ENGLISH_NAME)
            self.language_iso_639_1 = kodi.convert_language(self.language_full, kodi.ISO_639_1)

            if self.language_full == "Portuguese (Brazil)":
                self.language_iso_639_2 = "pob"
            elif self.language_full == "Greek":
                self.language_iso_639_2 = "ell"
            else:
                self.language_iso_639_2 = kodi.convert_language(self.language_full, kodi.ISO_639_2)
       
            self.language_iso_639_2t = self.get_ISO_639_2_T(self.language_iso_639_2)
            self.language_iso_639_2b = self.get_ISO_639_2_B(self.language_iso_639_2)

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
        self.language_iso_639_2 = None
        self.languages = None
        self.language_iso_639_1 = None
        self.language_iso_639_2t = None
        self.language_iso_639_2b = None
        del self.language_iso_639_2
        del self.languages
        del self.settings
        del self.language_iso_639_1
        del self.language_iso_639_2t
        del self.language_iso_639_2b

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