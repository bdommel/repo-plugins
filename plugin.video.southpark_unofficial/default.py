#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import json as _json
import time
import socket
import urllib
import urllib2
import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon
import xml.etree.ElementTree as ET

addonID = 'plugin.video.southpark_unofficial'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
defaultFanart = xbmc.translatePath('special://home/addons/'+addonID+'/fanart.png')
forceViewMode = True
audio_pos = int(addon.getSetting('audio_lang'))
audio = ["en","es","de"]
audio = audio[audio_pos]
mainweb_geo = ["southpark.cc.com","southpark.cc.com","www.southpark.de"]
fullep_geo = ["/full-episodes/","/episodios-en-espanol/","/alle-episoden/"]
pageurl_geo = ["southpark.cc.com","southpark.cc.com","southpark.de"]
mediagen_geo = ["player","player","video-player"]
rtmp_geo = ["rtmpe://viacommtvstrmfs.fplive.net:1935/viacommtvstrm","rtmpe://viacommtvstrmfs.fplive.net:1935/viacommtvstrm","rtmpe://cp75298.edgefcs.net/ondemand"]
mediagenopts_geo = ["&suppressRegisterBeacon=true&lang=","&suppressRegisterBeacon=true&lang=","&device=Other&aspectRatio=16:9&lang="]
geolocation_pos = int(addon.getSetting('geolocation'))
geolocation = ["US","UK","ES","DE","IT"]
geolocation = geolocation[geolocation_pos]
cc_settings = addon.getSetting('cc') == "true"
viewMode = str("504")

def index():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = ""
    content = getUrl("http://"+mainweb_geo[audio_pos])
    if "/messages/geoblock/" in content or "/geoblock/messages/" in content:
        notifyText(translation(30002), 7000)
	
    addDir(translation(30005), "Featured", 'listVideos', icon)
    addLink(translation(30006), "Random", 'listVideos', icon)
    for i in range(1, 19):
        addDir(translation(30007)+" "+str(i), 'season-'+str(i), 'listVideos', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    xbmcplugin.setContent(pluginhandle, "episodes")
    if url == "Featured":
        jsonrsp = getUrl(getCarousel())
        promojson = _json.loads(jsonrsp)
        for episode in promojson['results']:
			if episode['_availability'] == "banned":
				addLink(episode['title'], "banned", 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
			else:
				addLink(episode['title'], episode['itemId'], 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
    elif url == "Random":
		notifyText(translation(30003), 2000)
		rand = getUrl("http://"+mainweb_geo[audio_pos]+fullep_geo[audio_pos]+"random")
		rand = rand.split("<link rel=\"canonical\" href=\"")[1].split("\" />")[0]
		where = "http://"+mainweb_geo[audio_pos]+fullep_geo[audio_pos]+"s"
		rand = rand.split(where)[1].split("-")[0]
		rand = rand.split("e")
		# cc.com is the ony one with jsons so descriptions will be in english
		jsonrsp = getUrl("http://southpark.cc.com/feeds/carousel/video/57baee9c-b611-4260-958b-05315479a7fc/30/1/json/!airdate/season-"+str(int(rand[0])))
		seasonjson = _json.loads(jsonrsp)
		ep = int(rand[1])-1
		episode = seasonjson['results'][ep]
		if episode['_availability'] == "banned":
			addLink(episode['title'], "banned", 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
		else:
			addLink(episode['title'], episode['itemId'], 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
    else:
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
        jsonrsp = getUrl("http://southpark.cc.com/feeds/carousel/video/57baee9c-b611-4260-958b-05315479a7fc/30/1/json/!airdate/"+url)
        seasonjson = _json.loads(jsonrsp)
        for episode in seasonjson['results']:
            if episode['_availability'] == "banned":
				addLink(episode['title'], "banned", 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
            else:
				addLink(episode['title'], episode['itemId'], 'playVideo', episode['images'], episode['description'], episode['episodeNumber'][0]+episode['episodeNumber'][1], episode['episodeNumber'][2]+episode['episodeNumber'][3],episode['originalAirDate'])
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playTest(url, title, thumbnail):
	if url == "banned":
		notifyText(translation(30011), 7000)
		return
	mediagen = getMediagen(url)
	if len(mediagen) == 0:
		notifyText(translation(30011), 7000)
		return
	notifyText(translation(30009)+" " + title, 3000)
	swfVfy = "http://media.mtvnservices.com/player/prime/mediaplayerprime.2.7.11.swf" 
	flashVer = "WIN 12,0,0,70"
	conn = "B:0"
	rtmp = ""
	pageUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.2.7.11.swf?uri=mgid:arc:episode:"+pageurl_geo[audio_pos]+":"+url
	if audio != "de":
		pageUrl += "&type=network&ref=southpark.cc.com&geo="+ geolocation +"&group=entertainment&network=None&device=Other&"
	pageUrl += "&CONFIG_URL=http://media.mtvnservices.com/pmt/e1/players/mgid:arc:episode:"+pageurl_geo[audio_pos]+":/context3/config.xml?"
	pageUrl += "uri=mgid:arc:episode:"+pageurl_geo[audio_pos]+":"+url+"&type=network&ref="+pageurl_geo[audio_pos]+"&geo="+ geolocation +"&group=entertainment&network=None&device=Other"
	i = 0
	parts = str(len(mediagen))
	player = xbmc.Player()
	ccs = []
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	for media in mediagen:
		data = getVideoData(media)
		rtmpe = data[0]
		cc = data[2]
		best = len(rtmpe)-1
		rtmpgeo = audio_pos
		if audio == "de" and "viacomccstrm" in rtmpe[best]:
			rtmpgeo = 0
		rtmp = rtmp_geo[rtmpgeo]
		if audio == "de" and "ondemand" in rtmpe[best]:
			playpath = "mp4:"+rtmpe[best].split('ondemand/')[1]
		else:
			playpath = "mp4:"+rtmpe[best].split('viacomccstrm/')[1]
		videoname = title + " (" + str(i+1) + " of " + parts +")"
		li = xbmcgui.ListItem(videoname, iconImage=thumbnail, thumbnailImage=thumbnail)
		li.setInfo('video', {'Title': videoname})
		li.setProperty('PlayPath', playpath)
		li.setProperty('conn', conn)
		# li.setProperty('rtmp', rtmp)
		li.setProperty('flashVer', flashVer)
		li.setProperty('pageUrl', pageUrl)
		li.setProperty('SWFPlayer', swfVfy)
		li.setProperty("SWFVerify", "true")
		if len(cc) >= 3:
			ccs.append(cc[2])
		playlist.add(url=rtmp, listitem=li, index=i)
		i += 1
	player.play(playlist)
	i = 0
	for s in xrange(1):
		if player.isPlaying():
			break
		time.sleep(1)
	if not player.isPlaying():
		notifyText(translation(30004), 4000)
		player.stop()
	pos = playlist.getposition()
	if len(ccs) >= 3:
		player.setSubtitles(ccs[pos])
		player.showSubtitles(cc_settings)
	while player.isPlaying():
		if pos != playlist.getposition():
			pos = playlist.getposition()
			if len(ccs) >= playlist.size():
				player.setSubtitles(ccs[pos])
				player.showSubtitles(cc_settings)
		time.sleep(1)
	player.stop()
	playlist.clear()
	return

def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')
	
def notifyText(text, time=5000):
	addonname   = addon.getAddonInfo('name')
	xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(addonname, text, time, icon))

def getUrl(url):
	link = ""
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except urllib2.URLError:
		notifyText(translation(30010), 3000)
		raise
	return link

def addLink(name, url, mode, iconimage, desc="", season="", episode="", date=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+str(name)+"&thumbnail="+str(iconimage)
    convdate = ""
    if date != "":
        convdate = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S')
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Season": season, "Episode": episode, "Aired": convdate})
    liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def getCarousel():
	html = getUrl("http://southpark.cc.com/")
	html = html.split("</section><section class=")
	data_url = html[1].split("data-url=\"")
	data_url = data_url[1]
	data_url = data_url.split("\"")[0]
	carousel = data_url.split("{resultsPerPage}/{currentPage}/json/{sort}")[0]
	carousel += "14/1/json/airdate"
	carousel += data_url.split("{resultsPerPage}/{currentPage}/json/{sort}")[1]
	return "http://southpark.cc.com" + carousel

def getMediagen(id):
	feed = ""
	feed = getUrl("http://"+mainweb_geo[audio_pos]+"/feeds/video-player/mrss/mgid:arc:episode:"+pageurl_geo[audio_pos]+":"+id+"?lang="+audio)
	root = ET.fromstring(feed)
	mediagen = []
	if sys.version_info >=  (2, 7):
		for item in root.iter('guid'):
			if item.text != None and item.text != "bumper":
				mediagen.append(item.text)
	else:
		for item in root.getiterator('guid'):
			if item.text != None and item.text != "bumper":
				mediagen.append(item.text)
	return mediagen

def getVideoData(mediagen):
	xml = ""
	xml = getUrl("http://"+mainweb_geo[audio_pos]+"/feeds/"+mediagen_geo[audio_pos]+"/mediagen?uri="+mediagen+mediagenopts_geo[audio_pos]+audio+"&acceptMethods=fms,hdn1,hds")
	root = ET.fromstring(xml)
	rtmpe = []
	duration = []
	captions = []
	if sys.version_info >=  (2, 7):
		for item in root.iter('src'):
			if item.text != None:
				rtmpe.append(item.text)
		for item in root.iter('rendition'):
			if item.attrib['duration'] != None:
				duration.append(int(item.attrib['duration']))
		for item in root.iter('typographic'):
			if item.attrib['src'] != None:
				captions.append(item.attrib['src'])
	else:
		for item in root.getiterator('src'):
			if item.text != None:
				rtmpe.append(item.text)
		for item in root.getiterator('rendition'):
			if item.attrib['duration'] != None:
				duration.append(int(item.attrib['duration']))
		for item in root.getiterator('typographic'):
			if item.attrib['src'] != None:
				captions.append(item.attrib['src'])

	return [rtmpe,duration,captions]
	
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
	
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
eptitle = urllib.unquote_plus(params.get('title', ''))
epthumbnail = urllib.unquote_plus(params.get('thumbnail', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playTest(url, eptitle, epthumbnail)
else:
    index()