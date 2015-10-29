import requests
import cookielib
import bs4
import time
import re
import subprocess
import sys
import os
import json
import logging
import datetime
import ctypes
from colorama import init, Fore, Back, Style
init()

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

logging.basicConfig(filename="idlemaster-helper.log",filemode="w",format="[ %(asctime)s ] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p",level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter("[ %(asctime)s ] %(message)s", "%m/%d/%Y %I:%M:%S %p"))
logging.getLogger('').addHandler(console)

if sys.platform.startswith('win32'):
	ctypes.windll.kernel32.SetConsoleTitleA("Idle Master Helper")

logging.warning(Fore.GREEN + "WELCOME TO IDLE MASTER HELPER" + Fore.RESET)

logging.warning("This program will idle every game you own ")
logging.warning("that has cards and less than 2 hours of playtime.")
logging.warning("Doing so will mean you will be unable to request a")
logging.warning("refund for any game that isn't currently in the")
logging.warning("blacklist.txt file.  Are you sure you want")
logging.warning("to continue?  [y/n]")
valid = {"yes", "y"}
choice = raw_input("").lower()

if choice not in valid:
	logging.warning("Goodbye!")
	sys.exit()
	
try:
	authData={}
	authData["sort"]=""
	authData["steamparental"]=""
	authData["hasPlayTime"]="false"
	execfile("./settings.txt",authData)
	myProfileURL = "http://steamcommunity.com/profiles/"+authData["steamLogin"][:17]
except:
	logging.warning(Fore.RED + "Error loading config file" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()
	
if not authData["sessionid"]:
	logging.warning(Fore.RED + "No sessionid set" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()
	
if not authData["steamLogin"]:
	logging.warning(Fore.RED + "No steamLogin set" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()

def generateCookies():
	global authData
	try:
		cookies = dict(sessionid=authData["sessionid"], steamLogin=authData["steamLogin"], steamparental=authData["steamparental"])
	except:
		logging.warning(Fore.RED + "Error setting cookies" + Fore.RESET)
		raw_input("Press Enter to continue...")
		sys.exit()

	return cookies
	
def getAppName(appID):
	try:
		api = requests.get("http://store.steampowered.com/api/appdetails/?appids=" + str(appID) + "&filters=basic")
		api_data = json.loads(api.text)
		return Fore.CYAN + api_data[str(appID)]["data"]["name"].encode('ascii', 'ignore') + Fore.RESET
	except:
		return Fore.CYAN + "App "+str(appID) + Fore.RESET
		
def get_blacklist():
	try:
		with open('blacklist.txt', 'r') as f:
			lines = f.readlines()
		blacklist = [int(n.strip()) for n in lines]
	except:
		blacklist = [];

	if not blacklist:
		logging.warning("No games have been blacklisted")

	return blacklist
	
logging.warning("Finding games that have less than two hours playtime")

try:
	cookies = generateCookies()
	r = requests.get(myProfileURL+"/badges/",cookies=cookies)
except:
	logging.warning(Fore.RED + "Error reading badge page" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()

try:
	badgesLeft = []
	badgePageData = bs4.BeautifulSoup(r.text)
	badgeSet = badgePageData.find_all("div",{"class": "badge_title_stats"})
except:
	logging.warning(Fore.RED + "Error finding drop info" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()

# For profiles with multiple pages
try:
	badgePages = int(badgePageData.find_all("a",{"class": "pagelink"})[-1].text)
	if badgePages:
		logging.warning(str(badgePages) + " badge pages found.  Gathering additional data")
		currentpage = 2
		while currentpage <= badgePages:
			r = requests.get(myProfileURL+"/badges/?p="+str(currentpage),cookies=cookies)
			badgePageData = bs4.BeautifulSoup(r.text)
			badgeSet = badgeSet + badgePageData.find_all("div",{"class": "badge_title_stats"})
			currentpage = currentpage + 1
except:
	logging.warning("Reading badge page, please wait")

userinfo = badgePageData.find("a",{"class": "user_avatar"})
if not userinfo:
	logging.warning(Fore.RED + "Invalid cookie data, cannot log in to Steam" + Fore.RESET)
	raw_input("Press Enter to continue...")
	sys.exit()

blacklist = get_blacklist()

for badge in badgeSet:

	try:
		badge_text = badge.get_text()
		dropCount = badge.find_all("span",{"class": "progress_info_bold"})[0].contents[0]	
		has_playtime = re.search("hrs on record", badge_text) != None

		if "No card drops" in dropCount :
			continue
		else:
			if (has_playtime == False) :
				# Remaining drops
				dropCountInt, junk = dropCount.split(" ",1)
				dropCountInt = int(dropCountInt)
				linkGuess = badge.find_parent().find_parent().find_parent().find_all("a")[0]["href"]
				junk, badgeId = linkGuess.split("/gamecards/",1)
				badgeId = int(badgeId.replace("/",""))
				if badgeId in blacklist:
					logging.warning(getAppName(badgeId) + " on blacklist, skipping game")
					continue
				else:				
					push = [badgeId]
					badgesLeft.append(push)
			else:
				search_playtime = re.search("([0-1]\.[0-9]) hrs on record", badge_text)
				playtime = search_playtime.group(1)
				if int(float(playtime)) < 2:				
					dropCountInt, junk = dropCount.split(" ",1)
					dropCountInt = int(dropCountInt)
					linkGuess = badge.find_parent().find_parent().find_parent().find_all("a")[0]["href"]
					junk, badgeId = linkGuess.split("/gamecards/",1)
					badgeId = int(badgeId.replace("/",""))
					if badgeId in blacklist:
						logging.warning(getAppName(badgeId) + " on blacklist, skipping game")
						continue
					else:				
						push = [badgeId]
						badgesLeft.append(push)
	except:
		continue

logging.warning("Idle Master needs to idle " + Fore.GREEN + str(len(badgesLeft)) + Fore.RESET + " games")
rounds = len(badgesLeft) / 25 + (len(badgesLeft) % 25 > 0)
logging.warning ("The games will run in " + str(rounds) + " sets of 25 for 2 hours each")
logging.warning ("This process will take approximately " + str(rounds*2) + " hours")

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def IdleBatch(appids):
	try:
		global process_idle1, process_idle2, process_idle3, process_idle4, process_idle5, process_idle6, process_idle7, process_idle8, process_idle9, process_idle10, process_idle11, process_idle12, process_idle13, process_idle14, process_idle15, process_idle16, process_idle17, process_idle18, process_idle19, process_idle20, process_idle21, process_idle22, process_idle23, process_idle24, process_idle25
		global idle_time

		idle_time = time.time()

		if sys.platform.startswith('win32'):
			start_text = "steam-idle.exe "
		elif sys.platform.startswith('darwin'):
			start_text = "./steam-idle "
		elif sys.platform.startswith('linux'):
			start_text = "./steam-idle.py "
					
		process_idle1 = subprocess.Popen(start_text + str(appids[0][0]), shell=True)
		process_idle2 = subprocess.Popen(start_text + str(appids[1][0]), shell=True)
		process_idle3 = subprocess.Popen(start_text + str(appids[2][0]), shell=True)
		process_idle4 = subprocess.Popen(start_text + str(appids[3][0]), shell=True)
		process_idle5 = subprocess.Popen(start_text + str(appids[4][0]), shell=True)
		process_idle6 = subprocess.Popen(start_text + str(appids[5][0]), shell=True)
		process_idle7 = subprocess.Popen(start_text + str(appids[6][0]), shell=True)
		process_idle8 = subprocess.Popen(start_text + str(appids[7][0]), shell=True)
		process_idle9 = subprocess.Popen(start_text + str(appids[8][0]), shell=True)
		process_idle10 = subprocess.Popen(start_text + str(appids[9][0]), shell=True)
		process_idle11 = subprocess.Popen(start_text + str(appids[10][0]), shell=True)
		process_idle12 = subprocess.Popen(start_text + str(appids[11][0]), shell=True)
		process_idle13 = subprocess.Popen(start_text + str(appids[12][0]), shell=True)
		process_idle14 = subprocess.Popen(start_text + str(appids[13][0]), shell=True)
		process_idle15 = subprocess.Popen(start_text + str(appids[14][0]), shell=True)
		process_idle16 = subprocess.Popen(start_text + str(appids[15][0]), shell=True)
		process_idle17 = subprocess.Popen(start_text + str(appids[16][0]), shell=True)
		process_idle18 = subprocess.Popen(start_text + str(appids[17][0]), shell=True)
		process_idle19 = subprocess.Popen(start_text + str(appids[18][0]), shell=True)
		process_idle20 = subprocess.Popen(start_text + str(appids[19][0]), shell=True)
		process_idle21 = subprocess.Popen(start_text + str(appids[20][0]), shell=True)
		process_idle22 = subprocess.Popen(start_text + str(appids[21][0]), shell=True)
		process_idle23 = subprocess.Popen(start_text + str(appids[22][0]), shell=True)
		process_idle24 = subprocess.Popen(start_text + str(appids[23][0]), shell=True)
		process_idle25 = subprocess.Popen(start_text + str(appids[24][0]), shell=True)
	except:
		logging.warning("All games started")
		
i = 1
		
for apps in chunks(badgesLeft, 25):
	logging.warning("Starting batch #" + str(i))
	IdleBatch(apps)
	time.sleep(7200)
	
	try:
		process_idle1.terminate()
		process_idle2.terminate()
		process_idle3.terminate()
		process_idle4.terminate()
		process_idle5.terminate()
		process_idle6.terminate()
		process_idle7.terminate()
		process_idle8.terminate()
		process_idle9.terminate()
		process_idle10.terminate()
		process_idle11.terminate()
		process_idle12.terminate()
		process_idle13.terminate()
		process_idle14.terminate()
		process_idle15.terminate()
		process_idle16.terminate()
		process_idle17.terminate()
		process_idle18.terminate()
		process_idle19.terminate()
		process_idle20.terminate()
		process_idle21.terminate()
		process_idle22.terminate()
		process_idle23.terminate()
		process_idle24.terminate()
		process_idle25.terminate()
	except:		
		logging.warning("All games closed")
	
	logging.warning("Completed batch #" + str(i))
	i = i + 1
	
logging.warning(Fore.GREEN + "Successfully completed idling process" + Fore.RESET)
logging.warning("You're now ready to run Idle Master!")
raw_input("Press Enter to continue...")