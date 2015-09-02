from __future__ import print_function
import os
import sys
import platform
from ctypes import CDLL
try: #Python 2
    from urllib2 import urlopen
except ImportError: # Python 3
    from urllib.request import urlopen

import gtk
import gtk.gdk
import pynotify

def get_steam_api():
    if sys.platform.startswith('win32'):
        print('Loading Windows library')
        steam_api = CDLL('steam_api.dll')
    elif sys.platform.startswith('linux'):
        if platform.architecture()[0].startswith('32bit'):
            print('Loading Linux 32bit library')
            steam_api = CDLL('./libsteam_api32.so')
        elif platform.architecture()[0].startswith('64bit'):
            print('Loading Linux 64bit library')
            steam_api = CDLL('./libsteam_api64.so')
        else:
            print('Linux architecture not supported')
    elif sys.platform.startswith('darwin'):
        print('Loading OSX library')
        steam_api = CDLL('./libsteam_api.dylib')
    else:
        print('Operating system not supported')
        sys.exit()
        
    return steam_api

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit()
        
    str_app_id = sys.argv[1]
    
    os.environ["SteamAppId"] = str_app_id
    try:
        get_steam_api().SteamAPI_Init()
    except:
        print("Couldn't initialize Steam API")
        sys.exit()
        
    if pynotify.init("Idle-Master"):
        # Image URI
        uri = "http://cdn.akamai.steamstatic.com/steam/apps/" + str_app_id + "/header_292x136.jpg"
        image_bytes = urlopen(uri).read()

        loader = gtk.gdk.PixbufLoader();
        loader.write(image_bytes)
        loader.close()

        n = pynotify.Notification("Now idling", "App " + str_app_id)
        n.set_icon_from_pixbuf(loader.get_pixbuf())
        if not n.show():
            print("Failed to send notification")
    else:
        print("Failed to init notifications")
