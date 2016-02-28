script.subtitlechecker
======================

Displays if subtitle is present while navigating in Kodi library.

When launched the script provides those properties :

* SubTitleAvailable  
	- Depending of result, the values of the folowing parameters are returned: `availabereturnvalue`, `notavailablereturnvalue`, `searchreturnvalue`  
	- `Window(videolibrary).Property(SubTitleAvailable)`  
	- `Window(movieinformation).Property(SubTitleAvailable)`
* SubTitleAvailabeleLanguage  
	- The language of the subtitle search according ISO 639-2T. **Beware**: This is different then Kodi, which is returning ISO 639-2B or ISO 639-2T  
	- `Window(videolibrary).Property(SubTitleAvailabeleLanguage)`  
	- `Window(movieinformation).Property(SubTitleAvailabeleLanguage)`

To use it in your skin, just call it this way :

* `RunScript(script.skinsubtitlechecker,availabereturnvalue=subavailable&notavailablereturnvalue=subnotavailable&searchreturnvalue=subunknown&year=$INFO[ListItem.Year]&season=$INFO[ListItem.Season]&episode=$INFO[ListItem.Episode]&tvshow=$INFO[ListItem.TVShowTitle]&originaltitle=$INFO[ListItem.OriginalTitle]&title=$INFO[ListItem.Title]&filename=$INFO[ListItem.FileName])`   
for a one shot request
* `RunScript(script.skinsubtitlechecker,availabereturnvalue=subavailable&notavailablereturnvalue=subnotavailable&searchreturnvalue=subunknown&backend=True)`  
to run in background

##Parameters
All parameters are optional. If not given, the defaults are used.
*  `flushcache`   
	- Flush the cache.  
	- Allowed values: `True` or `False`.  
	- Default: `False`  
	- When `True`, **All** other parameters are ignored.  
	- Used in add-on Setting
*  `backend`  
	- Indicates if the script has to run in background.   
	- Allowed values: `True` or `False`.  
	- Default: `False`  
	- When `True`, `year`, `season`, `episode`, `tvshow`, `originaltitle`, `title` and `filename` are ignored. 
*  `year`  
	- Year of movie/episode.  
	- Default: `''`  
	- Ignored when `flushcache=True` or `backend=True`.
*  `season`  
	- Season of episode (empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.
*  `episode`  
	- Episode(empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  `tvshow`  
	- TV show title (empty for movie).  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  `originaltitle`  
	- Original title.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  `title`  
	- Title.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  `filename`  
	- Filename.  
	- Default `''`  
	- Ignored when `flushcache=True` or `backend=True`.  
*  `availabereturnvalue`  
	- Value returned if subtitle is available.  
	- Default `''`  
	- Ignored when `flushcache=True`.
*  `notavailablereturnvalue`  
	- Value returned if subtitle is not available.  
	- Default `''`  
	- Ignored when `flushcache=True`.
*  `searchreturnvalue`  
	- Value returned during search or when an error occured.  
	- Default `''`  
	- Ignored when `flushcache=True`.  

##Integration in your skin

On https://github.com/jurgenheine/skin.confluence_withsubcheck.git there is an example based on the confluence skin with detailed information how to use this script in a skin
