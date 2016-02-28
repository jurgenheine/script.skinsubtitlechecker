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

* `RunScript(script.skinsubtitlechecker, year=$INFO[ListItem.Year], season=$INFO[ListItem.Season], episode==$INFO[ListItem.Episode], tvshow=$INFO[ListItem.TVShowTitle], originaltitle=$INFO[ListItem.OriginalTitle], title=$INFO[ListItem.Title], filename=$INFO[ListItem.FileName], availabereturnvalue=Yes,notavailablereturnvalue=No,searchreturnvalue=)`   
for a one shot request
* `RunScript(script.skinsubtitlechecker,availabereturnvalue=OSDSubtitlesNF.png&notavailablereturnvalue=searchreturnvalue,&backend=True)`  
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

##Integration in your skin (confluence as example)

5 files need to be modified as follow :

###includes.xml

Add this new variable at the end of the file (before the `</include>`) :  
`<variable name="SubTitleAvailable">`  
>`<value condition="System.HasAddon(script.skinsubtitlechecker)">$INFO[window.Property(SubTitleAvailable)]</value>`  
>`<value></value>`
 
`</variable>`  
 
`<variable name="SubTitleAvailabeleLanguage">`  
>`<value condition="System.HasAddon(script.skinsubtitlechecker)">$INFO[window.Property(SubTitleAvailabeleLanguage)]</value>`  
>`<value></value>` 
 
`</variable>`  

###IncludesCodecFlagging.xml

Add this new variable at the end of the file (before the `</include>`) :  
`<include name="SubtitlePresentConditions">`
>`<control type="image">`
>>`<description>Subtitle Present Image</description>`  
>>`<width>80</width>`  
>>`<height>35</height>`  
>>`<aspectratio align="left">keep</aspectratio>`  
>>`<texture>$VAR[SubTitleAvailable]</texture>`

>`</control>`

`</include>`

###MyVideoNav.xml

Add `<onload>RunScript(script.skinsubtitlechecker,availabereturnvalue=OSDSubtitlesNF.png&backend=True)</onload>`  at the beginning.
	
###DialogVideoInfo.xml

Add  `<onload>RunScript(script.skinsubtitlechecker,availabereturnvalue=OSDSubtitlesNF.png&year=$INFO[ListItem.Year]&season=$INFO[ListItem.Season]&episode=$INFO[ListItem.Episode]&tvshow=$INFO[ListItem.TVShowTitle]&originaltitle=$INFO[ListItem.OriginalTitle]&title=$INFO[ListItem.Title]&filename=$INFO[ListItem.FileName])</onload>`   at the beginning.



###ViewsVideoLibrary.xml

Add the following line to each view under Media Codec Flagging Images
`<include>SubtitlePresentConditions</include>`

______________________

_This is my first kodi addon, for any suggestions, do not hesitate to email me :)_