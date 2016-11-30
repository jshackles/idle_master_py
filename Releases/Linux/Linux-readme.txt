The script needs these Python 2 packages to run:
requests
beautifulsoup4
pillow (with jpeg and tk support)
colorama


Example of packages installation:
Ubuntu: sudo apt install python-bs4 python-requests python-pil.imagetk python-colorama -y
Arch Linux: pacman -S python2-beautifulsoup4 python2-requests python2-pillow tk python2-colorama


In the spirit of open source and free software there are no Linux binaries provided. Instead, run the Python script directly using the command "python start.py".

If you run the idle and recive the message "No sessionid set" the program is working.


Connecting idle with steam:

 - log in your steam account on chrome
 - go to chrome settings
 - Show advanced settings
 - In Privacy > Content Settings
 - In Cookies > All cookies and site data
 - Search for "store.steampowered"
 - copy the content in "sessionid" and "steamLogin"
 - paste in the seetings.txt inside the Linux idle master
 
Now run the start.py again and it will probably start to idle your games!
