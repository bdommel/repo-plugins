# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import urlparse,sys

from resources.lib import antenna

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))


try:
    action = params['action']
except:
    action = None
try:
    url = params['url']
except:
    url = None



if action == None:
    antenna.indexer().root()

elif action == 'addBookmark':
    from lamlib import bookmarks
    bookmarks.add(url)

elif action == 'deleteBookmark':
    from lamlib import bookmarks
    bookmarks.delete(url)

elif action == 'bookmarks':
    antenna.indexer().bookmarks()

elif action == 'tvshows':
    antenna.indexer().tvshows()

elif action == 'archive':
    antenna.indexer().archive()

elif action == 'episodes':
    antenna.indexer().episodes(url)

elif action == 'reverseEpisodes':
    antenna.indexer().episodes(url, reverse=True)

elif action == 'popular':
    antenna.indexer().popular()

elif action == 'news':
    antenna.indexer().news()

elif action == 'sports':
    antenna.indexer().sports()

elif action == 'weather':
    antenna.indexer().weather()

elif action == 'live':
    antenna.indexer().live()

elif action == 'play':
    antenna.indexer().play(url)

