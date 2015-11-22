trakt-list-import
=================

**This script is broken at the moment. Needs upgrading to the trakt API version 2**

Python script to help you import a list of movies in a file into trakt.

ABOUT
Movie names are one per line. The ideal format is "<name> <year>"
It is not required to have a year in the name but it helps IMDB
The whole idea is that this script will clean up the names before searching
IMDB for the movie so that it can be added by imdb_id to your trakt account

Titles that can't be added will be put in a file named FILE.unknown

Often you can make a listing of all your movies by running something like 'ls -1 > movies.txt'
on the directory that you dump all your movies in.

Examples of dirty movie names that can be cleaned:
	Shame.2011.720p.BluRay.x264.YIFY.mp4
	Quadrophenia.1979.DVDRIP-ZEKTORM.mp4
	Lars.and.the.Real.Girl.2007.720p.BluRay.X264-AMIABLE.mkv

OPTIONS
-h
--help          Show help
--seen          Add movies to library (default setting, not required)
--watchlist     Add movies to watchlist
--username=     Your username
--password=     Your password (not recommended, instead enter password when prompted)
--apikey=       Your API key (get from here: http://trakt.tv/settings/api)
--dry           Don't do anything, just show what would happen (not implemented)
--debug         Turn on debuging mode (doesn't exist)

EXAMPLE USAGE
	python trakt-list-import.py bestmovies.txt                                                              
