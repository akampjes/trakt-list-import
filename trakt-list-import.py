#!/usr/bin/python

# vim: set expandtab:

import re
import sys
import urllib2
import json
import getopt
import time
import hashlib
import getpass


USERNAME = ''
PASSWORD = ''
APIKEY = ''


SOURCES = 'brrip|r5|dvdrip|src|dvdscr|pvvrip|cam|telesync| ts |wp|workprint|hdweb|bdrip|bluray'
CODECS = 'xvid|x264|264|h264|divx|aac|mp3|ac3|dts'
RESOLUTION = 'PAL|NTSC|720p|1080p|1080i|720|1080'
EXTENSION = 'mkv|avi|mp4|m4v|mov'

watchlist = 0
debug=0
dryrun=0
formatting=['title','disk','year','source','codec']

def get_data(filename):
    d = dict()

    print filename.strip()
    filename = re.sub(EXTENSION, '',  filename, flags=re.IGNORECASE)
    result = re.search('\d{4}', filename)
    if result and result.group() != 1080:
        d['year'] = result.group()
    filename = re.sub('_', ' ', filename, flags=re.IGNORECASE)
    filename = re.sub('\.', ' ', filename, flags=re.IGNORECASE)
    filename = re.sub('-', ' ', filename, flags=re.IGNORECASE)
    filename = re.sub(',', ' ', filename, flags=re.IGNORECASE)
    filename = re.sub('\s+', ' ', filename, flags=re.IGNORECASE)
    filename = re.sub('('+SOURCES+').*', '', filename, flags=re.IGNORECASE)
    filename = re.sub('('+CODECS+').*', '', filename, flags=re.IGNORECASE)
    filename = re.sub('('+RESOLUTION+').*', '', filename, flags=re.IGNORECASE)
    filename = re.sub('\d{4}', '', filename, flags=re.IGNORECASE)
    filename = re.sub('\[.*', '', filename, flags=re.IGNORECASE)
    filename = re.sub('\(.*', '', filename, flags=re.IGNORECASE)
    filename = re.sub('\{.*', '', filename, flags=re.IGNORECASE)

    filename = filename.strip()
    d['cleanname'] = filename

    return d

def send_data(imdb_id_data):
    pydata = {
            'username':USERNAME,
            'password':PASSWORD,
            'movies': imdb_id_data
            }
    json_data = json.dumps(pydata)
    clen = len(json_data)
    print json_data
    if watchlist == 1:
                req = urllib2.Request("https://api.trakt.tv/movie/watchlist/"+APIKEY, json_data, {'Content-Type': 'application/json', 'Content-Length': clen})
    else:
        req = urllib2.Request("https://api.trakt.tv/movie/seen/"+APIKEY, json_data, {'Content-Type': 'application/json', 'Content-Length': clen})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    print response

def get_imdb_info(title, year=None):
    if year != None:
        s='http://omdbapi.com/?t='+title+'&y='+str(year)
    else:
        s='http://omdbapi.com/?t='+title
    url = urllib2.urlopen(s.replace(' ','.'))
    data = url.read()
    res = json.loads(data)
    return res

def usage(argv0):
    print('usage: '+argv0+' [OPTION] FILE(s)...')
    print('''
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
    --apikey=       Your API key (get from here: http://trakt.tv/api-docs/authentication)
    --dry           Don't do anything, just show what would happen (not implemented)
    --debug         Turn on debuging mode (doesn't exist)

    EXAMPLE USAGE
        python trakt-list-import.py bestmovies.txt
    ''')
    sys.exit(1)

if __name__ == "__main__":
    try:
        args, files = getopt.gnu_getopt(sys.argv[1:], 'h',[
            'dry','debug','help','watchlist','username=','password=','apikey='])
    except:
        print "\nPlease  c h e c k   a r g u m e n t s\n\n"
        usage(sys.argv[0])

    for opt, arg in args:
        if opt in ['--help', '-h']:
            usage(sys.argv[0])
        elif opt in ['--dry']:
            dryrun=1
        elif opt in ['--debug']:
            debug=1
        elif opt in ['--seen']:
            watchlist = 0
        elif opt in ['--watchlist']:
            watchlist = 1
        elif opt in ['--username']:
            USERNAME = arg
        elif opt in ['--password']:
            PASSWORD = hashlib.sha1(arg).hexdigest()
        elif opt in ['--apikey']:
            APIKEY = arg
        else:
            print('unknown option '+opt)
            usage(sys.argv[0])

    if USERNAME == '':
        USERNAME = raw_input("enter trakt username: ")
    if APIKEY == '':
        APIKEY = raw_input("enter trakt apikey: ")
    if PASSWORD == '':
        PASSWORD = hashlib.sha1(getpass.getpass("enter trakt password (input hidden):")).hexdigest()

    for f in files:
        fin = open(f, 'r')
        fout_unknown = open(f+".unknown", 'w')
        imdb_id_list = []
        for name in fin:
            d=get_data(name)
            print "Cleanname: " + d['cleanname']
            if 'year' in d:
                print "Year: " + d['year']
                imdbinfo = get_imdb_info(d['cleanname'],d['year'])
            else:
                imdbinfo = get_imdb_info(d['cleanname'])
            if imdbinfo['Response'] != 'False':
                imdb_id = imdbinfo['imdbID']
                imdb_title = imdbinfo['Title']
                imdb_year = imdbinfo['Year']
                print "imdb: %s %s %s" % (imdb_title, imdb_year ,imdb_id)

                imdb_id_list.append({'imdb_id':imdb_id})

                # send batch of 100 IMDB IDs
                if len(imdb_id_list) >= 100:
                    send_data(imdb_id_list)
                    imdb_id_list = []
            else:
                # write out any names that can't be found in imdb so that you can fix them
                print('imdb: nothing found')
                fout_unknown.write(name.strip()+'\n')
            time.sleep(1)
            print ""
        # send unset IDs in list
        if len(imdb_id_list) > 0:
            send_data(imdb_id_list)

