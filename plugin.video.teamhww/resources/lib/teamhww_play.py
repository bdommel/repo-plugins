#
# Imports
#
from BeautifulSoup import BeautifulSoup
from teamhww_const import __addon__, __settings__, __language__, __images_path__, __date__, __version__
from teamhww_utils import HTTPCommunicator
import os
import re
import sys
import urllib, urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

#
# Main class
#
class Main:
	#
	# Init
	#
	def __init__( self ) :
		# Get plugin settings
		self.DEBUG = __settings__.getSetting('debug')
		
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s, %s = %s" % ( __addon__, __version__, __date__, "ARGV", repr(sys.argv), "File", str(__file__) ), xbmc.LOGNOTICE )
		
		# Parse parameters
		self.video_page_url = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)['video_page_url'][0]
		
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "self.video_page_url", str(self.video_page_url) ), xbmc.LOGNOTICE )

		#
		# Play video
		#
		self.playVideo()
	
	#
	# Play video
	#
	def playVideo( self ) :
		#
		# Init
		#
		no_url_found = False
		unplayable_media_file = False
		have_valid_url = False
		
		#
		# Get current list item details
		#
		title     = unicode( xbmc.getInfoLabel( "ListItem.Title"  ), "utf-8" )
		thumbnail =          xbmc.getInfoImage( "ListItem.Thumb"  )
		studio    = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "utf-8" )
		plot      = unicode( xbmc.getInfoLabel( "ListItem.Plot"   ), "utf-8" )
		genre     = unicode( xbmc.getInfoLabel( "ListItem.Genre"  ), "utf-8" )
		
		#
		# Show wait dialog while parsing data
		#
		dialogWait = xbmcgui.DialogProgress()
		dialogWait.create( __language__(30504), title )
		
		httpCommunicator = HTTPCommunicator()
		
		#Sometimes a page request gets a HTTP Error 500: Internal Server Error
		#f.e. http://www.gamekings.tv/videos/het-fenomeen-minecraft/
		try:
			html_data = httpCommunicator.get ( self.video_page_url )
		except urllib2.HTTPError, error:
			if (self.DEBUG) == 'true':
				xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "HTTPError", str(error) ), xbmc.LOGNOTICE )
			dialogWait.close()
			del dialogWait
			xbmcgui.Dialog().ok( __language__(30000), __language__(30507) % (str(error) ))
			exit(1)
			
		soup = BeautifulSoup(html_data)
		
		# Get the video url
		
		#<script type='text/javascript'>
		# showVideo('20130502_NieuwsDonderdag2.mp4','MjAxMzA1MDJfTmlldXdzRG9uZGVyZGFnMi5tcDQsaHR0cDovL3d3dy50ZWFtaHd3Lm5sL3dwLWNvbnRlbnQvdXBsb2Fkcy8yMDEzLzA1LzIwMTMwNTAyX1RCV1NwbGFzaC02MDB4MzQwLmpwZyxUZWFtIEJpam5hIEJpam5hIFdlZWtlbmQgb3ZlciBkZSBuaWV1d2UgTWFydmVsIGZpbG1zIGVuIEJsYWNrQmVycnk=','1');
		#</script>	
		pos_of_showVideo = html_data.find('showVideo')
		pos_of_mp4 = html_data.find('mp4')
		video_file_name = str(html_data[pos_of_showVideo + len("showVideo('"):pos_of_mp4 + len('mp4')])
		
		video_url = "http://stream.hardwarewoensdag.tv/" + video_file_name
		
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "video_url", str(video_url) ), xbmc.LOGNOTICE )
		
		if len(video_file_name) == 0:
			no_url_found = True
		else:
			if httpCommunicator.exists( video_url ):
				have_valid_url = True
			else:
				unplayable_media_file = True
				
		# Play video
		if have_valid_url:
			playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
			playlist.clear()
		
			listitem = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail )
			xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
			listitem.setInfo( "video", { "Title": title, "Studio" : "Gamekings", "Plot" : plot, "Genre" : genre } )
			playlist.add( video_url, listitem )
	
			# Close wait dialog
			dialogWait.close()
			del dialogWait
			
			# Play video
			xbmcPlayer = xbmc.Player()
			xbmcPlayer.play( playlist )
		#
		# Alert user
		#
	 	elif no_url_found:
			xbmcgui.Dialog().ok( __language__(30000), __language__(30505))
		elif unplayable_media_file:
			xbmcgui.Dialog().ok( __language__(30000), __language__(30506))
	
#
# The End
#