# -*- coding: utf-8 -*-
# Portico.TV XBMC Addon

import sys
import httplib

import urllib, urllib2, cookielib, datetime, time, re, os, string
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs, xbmc
import cgi, gzip
import json
from StringIO import StringIO


USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
GENRE_TV  = "TV"
UTF8          = 'utf-8'
MAX_PER_PAGE  = 25
URL_BASE      = 'http://www.portico.tv%s'

addon         = xbmcaddon.Addon('plugin.video.portico.tv')
__addonname__ = addon.getAddonInfo('name')
__language__  = addon.getLocalizedString


home          = addon.getAddonInfo('path').decode(UTF8)
icon          = xbmc.translatePath(os.path.join(home, 'icon.png'))
addonfanart   = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))

#play = False

def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

def cleanfilename(name):    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)

def demunge(munge):
        try:
            munge = urllib.unquote_plus(munge).decode(UTF8)
        except:
            pass
        return munge

def getEpoch():
    return str(int(time.mktime(time.gmtime())*1000))


def getRequest(url, user_data=None, headers = {'User-Agent':USER_AGENT, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8'}  ):
              log("getRequest URL:"+str(url))
              req = urllib2.Request(url.encode(UTF8), user_data, headers)

              try:
                 response = urllib2.urlopen(req)
                 if response.info().getheader('Content-Encoding') == 'gzip':
                    log("Content Encoding == gzip")
                    buf = StringIO( response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    link1 = f.read()
                 else:
                    link1=response.read()
              except:
                 link1 = ""

              link1 = str(link1).replace('\n','')
              return(link1)




def getSources(fanart):
    html = getRequest('http://www.portico.tv/menu/home')
    a = json.loads(html)
    x = a['items']
    for y in x:
          b=y['menuItemRef']
          name = b['name']
          title = y['text']
          addDir(title, name , 'GC', icon, fanart, '', '', '')


def getCats(url):
    if '#' in url:
      (url,mname) = url.split('#',1)
    else:
      mname = 'home'
    html = getRequest('http://www.portico.tv/menu/%s' % mname)
    a = json.loads(html)
    x = a['items']
    for y in x:
          b=y['menuItemRef']['name']
          if b == url:
           if b != 'categories':
            z = y['menuItemRef']['thumbnails']
            for c in z:
              c = c['channelItemRef']
              url    = "%s/%s" % (urllib.quote_plus(c['provider']), urllib.quote_plus(c['channelName']))
              desc   = c['description']
              fanart = URL_BASE % c['background']
              img    = URL_BASE % c['icon']
              title  = c['title']
              addDir(title, url , 'GS', img, fanart, desc, '', '')
           else:
            z = y['menuItemRef']['thumbnails']
            for c in z:
              name = c['categoryName']
              fanart = URL_BASE % c['menubg']
              c = c['categoryInfo']
              url    = "%s-shows#%s" % (urllib.quote_plus(name),urllib.quote_plus(name))
              desc   = c['description']
              img    = URL_BASE % c['icon']
              title  = c['title']
              addDir(title, url , 'GC', img, fanart, desc, '', '')
            

def getShow(url,fanart,poster):
      url  = ('http://www.portico.tv/playlist/%s?clientid=&_=%s') %(urllib.unquote_plus(url).replace(' ','%20'), getEpoch())
      html = getRequest(url)
      a = json.loads(html)
      x = a["episodes"]
      for a in x:
        try:
           duration = ' (%s)' %str(datetime.timedelta(seconds=a['duration']))
        except:
           duration = ''
        title  = a['title']+ duration
        desc   = a['description']
        x = a["content"]
        xlist = ''
        for a in x:
         if a['_type'] == 'Content':
           a = a['videoURLs']
           a = a['mp4']
           a = a['720p']
           a = a['2500']
           xlist = '%s%s,' % (xlist, a)
        xlist = xlist.rstrip(',')
        if ',' in xlist:
           surl = sys.argv[0]+"?playlist="+urllib.quote_plus(xlist.encode(UTF8))+"&name="+urllib.quote_plus(title.encode(UTF8))+"&desc="+urllib.quote_plus(desc.encode(UTF8))+"&mode=PP"
        else:
           surl = xlist
        addLink(surl.encode(UTF8),title,poster,fanart,desc,'','',False)



def play_playlist(name, list, desc):
        playlist = xbmc.PlayList(1)
        playlist.clear()
        item = 0
        list = list.split(',')
        for i in list:
            item += 1
            info = xbmcgui.ListItem('%s - Part %s' %(name, str(item)))
            info.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
            playlist.add(i, info)
        xbmc.executebuiltin('XBMC.Playlist.PlayOffset(-1)')

def addDir(name,url,mode,iconimage,fanart,description,genre,date,showcontext=True,playlist=None,autoplay=False):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+mode
        dir_playable = False
        cm = []

        if mode != 'SR':
            u += "&name="+urllib.quote_plus(name)
            if (fanart is None) or fanart == '': fanart = addonfanart
            u += "&fanart="+urllib.quote_plus(fanart)
            u += "&poster="+urllib.quote_plus(iconimage)
            dir_image = "DefaultFolder.png"
            dir_folder = True
        else:
            dir_image = "DefaultVideo.png"
            dir_folder = False
            dir_playable = True

        ok=True
        liz=xbmcgui.ListItem(name, iconImage=dir_image, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "Year": date } )
        liz.setProperty( "Fanart_Image", fanart )

        if dir_playable == True:
         liz.setProperty('IsPlayable', 'true')
        liz.addContextMenuItems(cm)
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=dir_folder)

def addLink(url,name,iconimage,fanart,description,genre,date,showcontext=True,playlist=None, autoplay=False):
        return addDir(name,url,'SR',iconimage,fanart,description,genre,date,showcontext,playlist,autoplay)



# MAIN EVENT PROCESSING STARTS HERE

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

parms = {}
try:
    parms = dict( arg.split( "=" ) for arg in ((sys.argv[2][1:]).split( "&" )) )
    for key in parms:
       parms[key] = demunge(parms[key])
except:
    parms = {}

p = parms.get

mode = p('mode', None)

if mode==  None:  getSources(p('fanart'))
elif mode=='SR':  xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=p('url')))
elif mode=='PP':  play_playlist(p('name'), p('playlist'),p('desc'))
elif mode=='GC':  getCats(p('url'))
elif mode=='GS':  getShow(p('url'),p('fanart'),p('poster'))

xbmcplugin.endOfDirectory(int(sys.argv[1]))




