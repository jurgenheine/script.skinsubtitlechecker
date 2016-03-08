script.subtitlechecker
======================

Makes it possible to show if there is a subtitle available for a movie or an episode while navigating in Kodi.

###Properties

When launched the script provides those properties :
* skinsubtitlechecker.available  
	- Depending of result, the values of the values of the folowing parameters are returned: 
		- `availabereturnvalue`
		- `notavailablereturnvalue`
		- `searchreturnvalue`  
	- `Window(videolibrary).Property(skinsubtitlechecker.available)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.available)`
* skinsubtitlechecker.language.iso_639_1  
	- The language of the subtitle search according ISO 639-1 (2 letters).  
	- Examples: `nl`, `fr`  
	- `Window(videolibrary).Property(skinsubtitlechecker.language.iso_639_1)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.language.iso_639_1)`
* skinsubtitlechecker.language.iso_639_2b  
	- The 3 letters language code of the subtitle search according ISO 639-2B.  
	- Examples: `dut`, `fre`  
	- `Window(videolibrary).Property(skinsubtitlechecker.language.iso_639_2b)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.language.iso_639_2b)`
* skinsubtitlechecker.language.iso_639_2t  
	- The 3 letters language code of the subtitle search according ISO 639-2T.  
	- Examples: `nld`, `fra`  
	- `Window(videolibrary).Property(skinsubtitlechecker.language.iso_639_2t)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.language.iso_639_2t)`
* skinsubtitlechecker.language.iso_639_2_kodi  
	- The 3 letters language code of the subtitle search according Kodi (ISO 639-2B or ISO 639-2T)  
	- Examples: `dut`, `fre`  
	- `Window(videolibrary).Property(skinsubtitlechecker.language.iso_639_2_kodi)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.language.iso_639_2_kodi)`
* skinsubtitlechecker.language.full  
	- The full language name of the subtitle search according Kodi.  
	- Examples:	`dutch`, `french`  
	- `Window(videolibrary).Property(skinsubtitlechecker.language.full)`  
	- `Window(movieinformation).Property(skinsubtitlechecker.language.full)`

###Parameters
All parameters are optional. If not given, the defaults are used.
*  flushcache   
	- Flush the cache.  
	- Allowed values: `True` or `False`.  
	- Default: `False`  
	- When `True`, **All** other parameters are ignored.  
	- Used in add-on Setting
*  backend  
	- Indicates if the script has to run in background.   
	- Allowed values: `True` or `False`.  
	- Default: `False`  
	- When `True`; `year`, `season`, `episode`, `tvshow`, `originaltitle`, `title` and `filename` are ignored. 
*  year  
	- Year of movie/episode.  
	- Default: `''`  
	- Ignored when `flushcache=True` or `backend=True`.
*  season  
	- Season of episode (empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.
*  episode  
	- Episode(empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  tvshow  
	- TV show title (empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  originaltitle  
	- Original title.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  title  
	- Title.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  filename  
	- Filename.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  availabereturnvalue  
	- Value returned if subtitle is available.  
	- Default `''`  
	- Ignored when `flushcache=True`.
*  notavailablereturnvalue  
	- Value returned if subtitle is not available.  
	- Default `''`  
	- Ignored when `flushcache=True`.
*  searchreturnvalue  
	- Value returned during search or when an error occured.  
	- Default `''`  
	- Ignored when `flushcache=True`.  

###Integration in your skin

To use it in your skin, just call it this way :

* for a one shot request
```
RunScript(script.skinsubtitlechecker,availabereturnvalue=subavailable&notavailablereturnvalue=subnotavailable&searchreturnvalue=subunknown&year=$INFO[ListItem.Year]&season=$INFO[ListItem.Season]&episode=$INFO[ListItem.Episode]&tvshow=$INFO[ListItem.TVShowTitle]&originaltitle=$INFO[ListItem.OriginalTitle]&title=$INFO[ListItem.Title]&filename=$INFO[ListItem.FileName])
```   
* to run in background
```
RunScript(script.skinsubtitlechecker,availabereturnvalue=subavailable&notavailablereturnvalue=subnotavailable&searchreturnvalue=subunknown&backend=True)
```  

On https://github.com/jurgenheine/skin.confluence_withsubcheck.git there is an example based on the confluence skin with detailed information how to use this script in a skin
