# PocketMiku player with raspberry pi + original HAT
# paython3
# ./user/(python) 
# pip mido, (python-rtmidi), 
# requireed files: AQM_PLC.py, character_table.py
import sys, os, glob
import mido
import time
import threading, queue
import RPi.GPIO as GPIO
from AQM_LCD import i2clcd
from gpiozero import MCP3204
# set Value
LCDLEN = 16 # LCD char/line
# SW asign
UP = 0
DOWN = 1
ENTER = 2 # PAUSE = 2
SETZERO = 3
MINUS = 4
PLUS = 5
# set midi control value
CENTERAJ = 0.25
MAXVALUE = 127
MAXPITCH = 8191 
MINPITCH = -8192
CENTEREXP = 64
# set threading control
lock_port = threading.Lock()
q_bpm = queue.Queue() 
q_bpmc = queue.Queue()   # for send & receive BPM data
q_bpmf = queue.Queue() 
q_lyr = queue.Queue() 
## thread def
# play midi file
def play_song(outport, filemid, e, ep):
    # set initial bpm rate (slow > 1 or fast < 1) & velocity rate
    bpmrate = 1.0
    # play midi file
    for msg in mido.MidiFile(filemid):
        # get bpmrate change
        if not q_bpm.empty():
            bpmrate = q_bpm.get()
        # pause or standby
        if msg.type == 'note_on':
            ep.wait()   # wait for set ep
        # get tempo
        if msg.type == 'set_tempo':
            q_bpmc.put(mido.tempo2bpm(msg.tempo))
        # main player
        time.sleep(msg.time*bpmrate) # with tempo control
        if not msg.is_meta:
            # send midi message
            lock_port.acquire()
            outport.send(msg)
            lock_port.release() 
            if msg.type == 'sysex': # for lyric display
                q_lyr.put(msg.data)
#                print(msg)  # for test
    # signal of end
    e.set() 
# display lyric
def display_lyric():
    code2chr = {0:"ア", 1:"イ", 2:"ウ", 3:"エ", 4:"オ", 5:"カ", 6:"キ", 7:"ク", 8:"ケ", 9:"コ",
                10:"ガ", 11:"ギ", 12:"グ", 13:"ゲ", 14:"ゴ", 15:"キャ", 16:"キュ", 17:"キョ", 18:"ギャ", 19:"ギュ",
                20:"ギョ", 21:"サ", 22:"スィ", 23:"ス", 24:"セ", 25:"ソ", 26:"ザ", 27:"ズィ", 28:"ズ", 29:"ゼ",
                30:"ゾ", 31:"シャ", 32:"シ", 33:"シュ", 34:"シェ", 35:"ショ", 36:"ジャ", 37:"ジ", 38:"ジュ", 39:"ジェ",
                40:"ジョ", 41:"タ", 42:"ティ", 43:"トゥ", 44:"テ", 45:"ト", 46:"ダ", 47:"ディ", 48:"ドゥ", 49:"デ",
                50:"ド", 51:"テュ", 52:"デュ", 53:"チャ", 54:"チ", 55:"チュ", 56:"チェ", 57:"チョ", 58:"ツァ", 59:"ツィ",
                60:"ツ", 61:"ツェ", 62:"ツォ", 63:"ナ", 64:"ニ", 65:"ヌ", 66:"ネ", 67:"ノ", 68:"ニャ", 69:"ニュ",
                70:"ニョ", 71:"ハ", 72:"ヒ", 73:"フ", 74:"ヘ", 75:"ホ", 76:"バ", 77:"ビ", 78:"ブ", 79:"ベ",
                80:"ボ", 81:"パ", 82:"ピ", 83:"プ", 84:"ペ", 85:"ポ", 86:"ヒャ", 87:"ヒュ", 88:"ヒョ", 89:"ビャ",
                90:"ビュ", 91:"ビョ", 92:"ピャ", 93:"ピュ", 94:"ピョ", 95:"ファ", 96:"フィ", 97:"フュ", 98:"フェ", 99:"フォ",
                100:"マ", 101:"ミ", 102:"ム", 103:"メ", 104:"モ", 105:"ミャ", 106:"ミュ", 107:"ミョ", 108:"ヤ", 109:"ユ",
                110:"ヨ", 111:"ラ", 112:"リ", 113:"ル", 114:"レ", 115:"ロ", 116:"リャ", 117:"リュ", 118:"リョ", 119:"ワ",
                120:"ウィ", 121:"ウェ", 122:"ヲ", 123:"ン", 124:"ン", 125:"ン", 126:"ン", 127:"ン"}
    sysexlyrc = [67, 121, 9, 17, 10, 0]
    if not q_lyr.empty():
        msgdata = q_lyr.get()
        # check sysex type
        typelength = 6
        compcount = 0
        while compcount < typelength:
            if msgdata[compcount] != sysexlyrc[compcount]:
                break
            compcount += 1
        # check type matched
        if compcount == typelength:
            # generate lyric
            lyricdata = ''
            posdata = typelength
            while posdata < len(msgdata):
                lyricdata += code2chr[msgdata[posdata]]
                posdata += 1
            # display Lylic
            display_2ndline(lyricdata)
            print(lyricdata)    # for debug
# display 1st line
def display_1stline(displine1):
    lcd.setaddress(0, 0)
    lcdline1 = displine1
    charlen = LCDLEN - len(lcdline1)
    if charlen > 0:
        i = 0
        while i < charlen:
            lcdline1 += ' '
            i += 1
    lcd.put_message(lcdline1)
# display 2nd line
def display_2ndline(displine2):
    lcd.setaddress(1, 0)
    lcdline1 = displine2
    charlen = LCDLEN - len(lcdline1)
    if charlen > 0:
        i = 0
        while i < charlen:
            lcdline1 += ' '
            i += 1
    lcd.put_message(lcdline1)
# display 1st line left
def display_1stleft(displine1l):
    lcd.setaddress(0, 0)
    lcdline1 = displine1l
    charlen = (LCDLEN -8) - len(lcdline1) # check vs display area
    if charlen > 0:
        i = 0
        while i < charlen:
            lcdline1 += ' '
            i += 1
    lcd.put_message(lcdline1)
# display bpm (1st line right)
def display_bpm():
    lcdline0 = ''
    charlen = LCDLEN - 8 - len(str(int(bpmint/bpmchange))) - len('bpm')
    if charlen > 0:
        i = 0
        while i < charlen:
            lcdline0 += ' '
            i += 1
    lcdline0 += str(int(bpmint/bpmchange)) + 'bpm'
    lcd.setaddress(0, 7)    # display 1st line right
    lcd.put_message(lcdline0)
# flash bpm with LED
def flash_bpm():
    BPMDIV = 8
    ONCOUNT = 0
    bpmtime = 60.0/(bpmint*BPMDIV)  # flash ON/OFF base interval
    while True:
        # check playstate(0:select, 1:playing)
        if playstate == 0:
            GPIO.output(LED[2],LEDOFF)
            break
        # flash
        GPIO.output(LED[2],LEDON)
        j = 0
        while j < BPMDIV:
            time.sleep(bpmtime)
            if not q_bpmf.empty():
                bpmtime = 60.0/(q_bpmf.get()*BPMDIV)
                break
            if j == ONCOUNT:
                GPIO.output(LED[2],LEDOFF)
            j += 1
## main
# set thread control
e1 = threading.Event()  # for check of end of play_song
ep = threading.Event()  # for pause for play_song

# initialize lcd
lcd = i2clcd()
lcd.clear()
# GPIO initialize
SW = (22, 23, 24, 25, 26, 27)
swnow = []
swlast = []
swchng = []
LED = (5, 6, 17)
ledlast = []
LEDON = 1
LEDOFF = 0
GPIO.setmode(GPIO.BCM)
i = 0
for pinout in LED:
    GPIO.setup(pinout, GPIO.OUT)
    GPIO.output(pinout,LEDOFF)
    ledlast.insert(i, 1)
    i += 1
i = 0
for pinin in SW:
    GPIO.setup(pinin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    swnow.insert(i, 1)
    swlast.insert(i, 1)
    swchng.insert(i, 0)
    i += 1
# print(ledlast, '&', swnow, '&', swlast, '&', swchng) # for debug
# control lever initialize
leftx = MCP3204(channel=0)
lefty = MCP3204(channel=1)
rightx = MCP3204(channel=2)
righty = MCP3204(channel=3)
# set midiout
midiout = 'NSX-39:NSX-39 MIDI 1'
try:
    outport = mido.open_output(midiout)
except OSError:
    display_1stline('Emergency stop!!')
    display_2ndline('No MIDI OUT exists!')
    # close IO
    leftx.close()
    lefty.close()
    rightx.close()
    righty.close()
    GPIO.cleanup()
    print('MIDI OUT does not exist!')   # for debug
    sys.exit(0)
# initialize Values
playstate = 0 # 0:select, 1:playing
# initialize display
display_1stline('Initaizing')
# change dir to this py file
os.chdir(os.path.dirname(os.path.abspath('__file__')))
print('getcwd:      ', os.getcwd()) # print this files directory for debug
# set midi file
filesel = 0
midifile = glob.glob('./midi/*.mid')
print(len(midifile), 'MIDI files exist')    # for debug
# display initial
display_1stline('Select! Up/Down')
display_2ndline('Quit')
# polling for input
try:
    while True:
        # polling interval
        time.sleep(0.05)
        # detect SW operation
        swcount = 0
        i = 0
#        swinput = '' # for debug
        for pinin in SW:
            swnow[i] = GPIO.input(pinin)
            if swnow[i] == swlast[i]:
                swchng[i] = 0
            else:
                swchng[i] = 1
                swcount += 1
            swlast[i] = swnow[i]
#            swinput += str(swnow[i]) # for debug 
            i += 1
#        print(swinput) # for debug
        # before playing section
        if playstate == 0: # 0:select, 1:playing
            # file select by SW
            if swchng[UP] == 1 and swnow[UP] == 0:
                if filesel >= len(midifile):
                    filesel = 0
                else:
                    filesel += 1
#                print(filesel) # for debug
            if swchng[DOWN] == 1 and swnow[DOWN] == 0:
                if filesel <= 0:
                    filesel = len(midifile)
                else:
                    filesel -= 1
#                print(filesel) # for debug
            # display MIDI file
            #  check SW operation & select file
            if swcount > 0:
                if filesel == 0:
                    display_2ndline('Quit')
                else:
                    display_2ndline(os.path.basename(midifile[filesel-1]))
            #  set the song to play / Quit
            if swchng[ENTER] == 1 and swnow[ENTER] == 0:
                if filesel == 0:    # Quit
                    lcd.clear()
                    print('Quit')   # for debug
                    # close IO
                    outport.close()
                    leftx.close()
                    lefty.close()
                    rightx.close()
                    righty.close()
                    GPIO.cleanup()
                    sys.exit(0)
                # set state playing
                playstate = 1  # 0:select, 1:playing
                # initialize
                pause = 1   # 1:pause
                # intialize modulation control
                lyinit = lefty.value
                modchg = 0
                # intialize pitchwheel
                lxinit = leftx.value
                pitchchg = 0
                # intialize expression control
                ryinit = righty.value
                expres = 64
                # intialize bpm change
                bpmint = 120    # MIDI standard Ver.1.0 default
                bpmchange = 1.0
                bpmdif = 0.0
                # print selected song
                print(midifile[filesel-1])  # for debug
                # display status
                display_1stline('Loading')
                # display bpm
                display_bpm()
                # display standby
                display_1stleft('Standby')
                # generate thread object
                ep.clear()    # initial pause
                t1 = threading.Thread(target = play_song, args=(outport, midifile[filesel-1], e1, ep,))   # midifile[filesel] play
                t2 = threading.Thread(target = flash_bpm)   # bpm flash with LED
                # set thread daemon
                t1.setDaemon(True)
                t2.setDaemon(True)
                # start thread object
                t1.start()
                t2.start()
        # on playing  (playstate == 1,  0:select, 1:playing)
        else: 
            # display Lyric
            display_lyric()
            # modulation control
            lynow = lefty.value
            # adjust center sense by CENTERAJ
            if lynow >= lyinit*(1-CENTERAJ) and lynow <= lyinit*(1+CENTERAJ):
                modnow = 0
            elif lynow < lyinit*(1-CENTERAJ):   # down side
                modnow = int(MAXVALUE*(lyinit*(1-CENTERAJ)-lynow)/(lyinit*(1-CENTERAJ)))
            elif lynow > lyinit*(1+CENTERAJ):   # up side
                modnow = int(MAXVALUE*(lynow-lyinit*(1+CENTERAJ))/(1-lyinit*(1+CENTERAJ)))
            # correct input
            if modnow > MAXVALUE:    # for max
                modnow = MAXVALUE
            if modnow != modchg:
                modchg = modnow
                if modchg == 0:
                    GPIO.output(LED[0],LEDOFF)
                else:
                    GPIO.output(LED[0],LEDON)
                msgtx3 = mido.Message('control_change', channel = 0, control = 1, value = modchg)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx3)
                lock_port.release() 
#                print(msgtx3)   # for debug
            # pitchwheel control
            lxnow = leftx.value
            # adjust center sense by CENTERAJ
            if lxnow >= lxinit*(1-CENTERAJ) and lxnow <= lxinit*(1+CENTERAJ):
                pitchnow = 0
            elif lxnow < lxinit*(1-CENTERAJ):   # down side
                pitchnow = int(MINPITCH*(lxinit*(1-CENTERAJ)-lxnow)/(lxinit*(1-CENTERAJ)))
            elif lxnow > lxinit*(1+CENTERAJ):   # up side
                pitchnow = int(MAXPITCH*(lxnow-lxinit*(1+CENTERAJ))/(1-lxinit*(1+CENTERAJ)))
            # input limiter
            if pitchnow < MINPITCH:   # for min
                pitchnow = MINPITCH
            elif pitchnow > MAXPITCH:    # for max
                pitchnow = MAXPITCH
            # revise pitchwheel
            if pitchnow != pitchchg:
                pitchchg = pitchnow
                if pitchchg == 0:
                    GPIO.output(LED[0],LEDOFF)
                else:
                    GPIO.output(LED[0],LEDON)
                msgtx2 = mido.Message('pitchwheel', channel = 0, pitch = pitchchg)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx2)
                lock_port.release() 
#                print(msgtx2)   # for debug
            # expressiion control
            rynow = righty.value
            # adjust center sense by CENTERAJ
            if rynow >= ryinit*(1-CENTERAJ) and rynow <= ryinit*(1+CENTERAJ):
                expnow = CENTEREXP
            elif rynow < ryinit*(1-CENTERAJ):   # down side
                expnow = int(CENTEREXP*(1-(ryinit*(1-CENTERAJ)-rynow)/(ryinit*(1-CENTERAJ))))
            elif rynow > ryinit*(1+CENTERAJ):   # up side
                expnow = int((MAXVALUE-CENTEREXP)*(rynow-ryinit*(1+CENTERAJ))/(1-ryinit*(1+CENTERAJ))+CENTEREXP)
            # correct input
            if expnow > MAXVALUE:    # for max
                expnow = MAXVALUE
            elif expnow < 0:    # for min
                expnow = -0
            if expres != expnow:
                expres = expnow
                if expres == CENTEREXP:
                    GPIO.output(LED[1],LEDOFF)
                else:
                    GPIO.output(LED[1],LEDON)
                msgtx4 = mido.Message('control_change', channel = 0, control = 11, value = expres)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx4)
                lock_port.release() 
#                print(msgtx4)   # for debug
            # bpm change
            if ((swnow[MINUS] == 0 and swchng[MINUS] == 1) or 
                (swnow[PLUS] == 0  and swchng[PLUS] == 1) or
                (swnow[SETZERO] == 0  and swchng[SETZERO] == 1)):
                if swnow[MINUS] == 0 and swchng[MINUS] == 1:
                    bpmdif -= 1.0
                if swnow[PLUS] == 0  and swchng[PLUS] == 1:
                    bpmdif += 1.0
                if swnow[SETZERO] == 0  and swchng[SETZERO] == 1:
                    bpmdif = 0.0
                if bpmint - bpmdif < 3: # lower limiter
                    bpmdif = 0.0
                bpmchange = bpmint/(bpmint+bpmdif)
                q_bpm.put(bpmchange)
                q_bpmf.put(bpmint+bpmdif)
                # display
                display_bpm()                
            # puase
            if swnow[ENTER] == 0  and swchng[ENTER] == 1:
                if pause == 1:
                    pause = 0   # 1:pause
                    ep.set()
                    # disaplay
                    display_1stleft('Playing')
                else:
                    pause = 1   # 1:pause
                    ep.clear()
                    # disaplay
                    display_1stleft('Pause')
        # get bpm 
        if not q_bpmc.empty():
            bpmint = int(q_bpmc.get())
            q_bpmf.put(bpmint+bpmdif)
            # display bpm
            display_bpm()                
        # catch end of song
        if e1.isSet():  # check end of play_song
            playstate = 0 # 0:stop, 1:playing
            # wait for quit thread object
            t1.join()
            t2.join()
            # display title
            display_1stline('Select! Up/Down')
            display_2ndline(os.path.basename(midifile[filesel-1]))
            # clear signal of end of play_song
            e1.clear()
except KeyboardInterrupt:
    # close IO
    outport.close()
    leftx.close()
    lefty.close()
    rightx.close()
    righty.close()
    GPIO.cleanup()
