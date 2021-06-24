<outline>
This repository is MIDI player for Pocket Miku with raspberry pi.
Including Python3 codes, shell script for power on start and circuit information.
Main functions are MIDI file play, bpm change and some MIDI controls (pitch, modulation, expression).

<environment>
1. Hardware
 ・Raspberry Pi2 ModelB
 ・GAKKEN nsx-39 (Pocket Miku)
 ・Original HAT (handmade) : refer to /Figure

2. Software
 ・Raspberry Pi setting Interface (GUI through VNC)
   SPI, (VNC) and I2C enable
 ・Python3
 ・pip (sudo pip3 install xxx) and other setting (apt install, etc)
   mido, python-rtmidi, RPi.GPIO, gpiozero(apt install python3-gpiozero)
 　refer to <reference> about LCD display
 ・/home/pi/PocketMiku  : refer to /PocketMiku
 　pocketmiku_playerxx.py　:main
 　AQM_LCD.py :LCD display sub
 　character_table.py :LCD display sub 　
 　pocketmiku_play.service :expample for power on start
 　pocketmiku_play.sh :used on pocketmiku_play.service
 ・/home/pi/PocketMiku/midi  : refer to /PocketMiku/midi
   Set *.mid to play.
 ・/etc/systemd/system/pocketmiku_play.service (when power on start)
   Make symbolic link of pocketmiku_playerxx.py as /PocketMiku/pocketmiku_player and
   create service like /PocketMiku/pocketmiku_play.service ,
   and enable service ($sudo systemctl enable pocketmiku_play).

<useage>
 1. nomal useage
  $python3 pocketmiku_playerxx.py
  (When error happend, some pip or apt install executed more.)
 2. power on start
  create and enable pocketmiku_play.service (see <environment )
 
<reference>
1. LCD display codes (modified to use)
 ・温度センサーBME280の値をLCD(AQM0802A)に表示 
  　http://roguer.info/2016/05/21/7926/
  　: part of lcd display
 ・ yuma-m /raspi_lcd_acm1602ni
 　　https://github.com/yuma-m/raspi_lcd_acm1602ni
 　　: character_table.py and code translater
2. ADC
 ・■SPIインターフェースの12ビット8チャネルA-DコンバータMCP3208
 　　https://www.denshi.club/pc/raspi/5raspberry-pi-zeroiot8a-d5mcp3208.html
3. MIDI
　・DTMハイパー初心者講座
　　　https://dtm-hyper.com/
　・DTM Solutions
　　　https://izmi.com/midi/midi_ctrl_no.html
　・Domino (MIDI音楽編集ソフト)
　  http://takabosoft.com/domino
　・Free MIDI File Site
　・01 ポケミク 歌詞ツール
　  https://sites.google.com/site/himagine201206/home/dtm/nsx39/sysexnsx39
4. HAT
 ・トランジスタ技術　2016/6 Apple Pi
//
//
　
