#!/usr/bin/python

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

from subprocess import call, Popen, PIPE
from os import chdir
import re

import liblo

target = liblo.Address(2000)
messageText = ""
messageTime = 0

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()

# Clear display and show greeting, pause 1 sec
lcd.clear()
lcd.message("microsynth\n")
sleep(1)

# Cycle through backlight colors
#col = lcd.BLUE #
#lcd.ON   , lcd.OFF)



#osc stuff ----------------------------------------------------------------
# create server, listening on port 2001
import liblo

try:
    server = liblo.ServerThread()
except liblo.ServerError, err:
    print str(err)

def messageCallback(path, args):
    global messageText, messageTime
    s = args[0]
    #print ("OSC: '%s'" % (s))
    messageText = args[0]
    #printText(messageText)
    messageTime = 10
 

server.add_method("/message", 's', messageCallback)
print("gui osc-server:")
print(server.get_port())
oscServerPort = server.get_port()
server.start()

#-------------------------------------------------------------------------


menuNum = 0
value = 50


def menuConnectMidi():
	lcd.clear()
	lcd.message("kopplar midi...")
	call(["aconnect", "16:0", "microsynth:0"])
	sleep(1)
	printMenu()

def menuJack():
	lcd.clear()
	lcd.message("startar jack...")
	call(["pkill", "jackd"]);
	Popen(["jackd", "-P70", "-p16", "-t2000", "-dalsa", "-dhw:1", "-p512", "-n3" ,"-r44100", "-s"])
	sleep(.5)
	printMenu()

def menuJack2():
	lcd.clear()
	lcd.message("startar jack...\n med in-port")
	call(["pkill", "jackd"]);
	Popen(["jackd", "-p20", "-t5000", "-dalsa", "-dhw:1", "-r44100", "-p512", "-n2", "-s"])
	sleep(.5)
	printMenu()

def menuMicroSynth():
	lcd.clear()
	lcd.message("startar microsynth")
	chdir("/home/pi/kod/microsynth/")
	call(["pkill", "microsynth"])
	Popen(["/home/pi/kod/microsynth/microsynth", "-n", "--osc", str(oscServerPort)])
	sleep(.5)
	menuConnectMidi()
	printMenu()
	

def menuConnectMidi():
	lcd.clear()
	lcd.message("kopplar midi...")
	sleep(.3)
	
	data_stream = Popen(["aconnect", "-i"], stdout=PIPE)
	for line in data_stream.stdout:
		if line.find("kernel") == -1:
			continue
		apa = re.search("[0-9]*:", line)
		print (line)
		bepa = apa.group(0)[:-1]
		if bepa == "0" or bepa == "14": #midithrough
			continue
		print (bepa)
		if not call (["aconnect", bepa, "microsynth"]):
			cepa = re.search("'.*'", line).group(0)[1:-1]
			print (" ".join(["kopplar", cepa]))
			printText(" ".join(["kopplar", cepa, "\n", bepa]))
			sleep(.5)
	
	#call(["aconnect", "16:0", "microsynth:0"])
	#call(["aconnect", "nanoKONTROL:0", "microsynth:0"])
	#sleep(1)
	printMenu()

def menuRestart():
	lcd.clear()
	lcd.message("startar om...")
	lcd.backlight(lcd.ON)
	call(["reboot", "-f"])

def printText(text):
	lcd.clear()
	lcd.message(text)

def menuUpdate():
	printText("Uppdaterar\n>---|")
	sleep(.3)
	printText("Laddar ner\n->--|")
	chdir("/home/pi/kod/microsynth/")
	call(["git", "pull", "origin", "master"])
	printText("Kompilerar...\n-->-|")
	call(["make", "-C", "/home/pi/kod/microsynth/"])
	printText("Klart!!\n----x|")
	sleep(.1)
	menuMicroSynth()
	printMenu()
	
def menuNoteOn():
	liblo.send(target, "/midi", ('m', (0, 144, 60, 100)))
	printText("noteon\n");
	while(lcd.buttonPressed(lcd.SELECT)):
		sleep(.1)
	liblo.send(target, "/midi", ('m', (0, 128, 60, 100)))
	printMenu()
	
menuInstrument = 0 #Forward declaration only

def menuGotoInstrumentSelect():
	global menu, menuInstrument
	menu = menuInstrument
	sleep(1)
	printMenu()

menuMain = (("Connect midi", menuConnectMidi),
		("starta jack\n bara ut", menuJack),
		("starta jack\n med in/ut", menuJack2),
		("starta microsynth", menuMicroSynth),
		("Restart\nsystem", menuRestart),
		("Uppdatera\nmicrosynth", menuUpdate),
		("Skicka not\n", menuNoteOn),
		("select\ninstrument", menuGotoInstrumentSelect))
		
		
menu = menuMain


def menuGotoMain():
	global menu, menuMain
	menu = menuMain
	printMenu()

#------------------Change instrument menu----------------------


def menuInstrumentOrgan():
	liblo.send(target, "/program", ('i', 0))
	menuGotoMain()

def menuInstrumentOsc():
	liblo.send(target, "/program", ('i', 1))
	menuGotoMain()

def menuInstrumentSampler():
	liblo.send(target, "/program", ('i', 2))
	menuGotoMain()
	
def menuInstrumentDrumMachine():
	liblo.send(target, "/program", ('i', 3))
	menuGotoMain()

menuInstrument = (("instrument\nback", menuGotoMain),
				("select\norgan", menuInstrumentOrgan),
				("select\nosc", menuInstrumentOsc),
				("select\nsampler", menuInstrumentSampler),
				("select\ndrum machine", menuInstrumentDrumMachine))

#--------------------------------------------------------------




def printMenu():
	global menuNum
	lcd.clear()
	if menuNum < 0:
		menuNum = len(menu)
	if menuNum >= len(menu):
		menuNum = 0
	
	lcd.message("{0}: {1}".format(menuNum, menu[menuNum][0]))

def menuUp():
    lcd.clear()
    global menuNum
    menuNum += 1
    printMenu()

def menuDown():
	global menuNum
	menuNum -= 1
	printMenu()

def menuLeft():
	global value
	value -= 1
	printMenu()
	
def menuRight():
	global value
	value += 1
	printMenu()

def menuSelect():
	menu[menuNum][1]()
	#call(["mplayer", "/home/pi/Adafruit/Pling.mp3"])



sleep(.5)
lcd.backlight(lcd.ON)
sleeptime = 0

# Poll buttons, display message & set backlight accordingly
btn = ((lcd.LEFT  , menuLeft),
       (lcd.UP    , menuUp),
       (lcd.DOWN  , menuDown),
       (lcd.RIGHT , menuRight),
       (lcd.SELECT, menuSelect))
prev = -1

menuJack()
menuMicroSynth()
printMenu()

while True:
    sleep(.1)
    if messageTime == 10:
    	printText(messageText)
    if messageText:
    	messageTime -= 1
    	if messageTime <= 0:
    		messageText = ""
    		printMenu()
    
    for b in btn:
        if lcd.buttonPressed(b[0]):
            func = b[1]
            func()
            sleeptime = sleeptime / 1.1
            if b is not prev:
            	sleeptime = .2
            sleep(sleeptime)
            prev = b
            break
        else:
        	if prev is b:
        	    sleeptime = .2
        	    


