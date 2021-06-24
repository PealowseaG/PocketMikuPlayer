# python3 (coding: utf-8)
# main: Display temperature(dummy) & time
# refer  http://roguer.info/2016/05/21/7926/
#   https://github.com/yuma-m/raspi_lcd_acm1602ni
import smbus
import time
from character_table import CHAR_TABLE
from datetime import datetime

class i2clcd:
    i2c = smbus.SMBus(1)
    addr = 0x3e
    contrast = 42   # 0～63

    def __init__(self):
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        self.i2c.write_byte_data(self.addr, 0, 0x39)    # function set(IS=1)
        self.i2c.write_byte_data(self.addr, 0, 0x14)    # internal osc
        self.i2c.write_byte_data(self.addr, 0,
                    (0x70 | (self.contrast & 0x0f)))    # contrast
        self.i2c.write_byte_data(self.addr, 0,
                    (0x54 | ((self.contrast >> 4) & 0x03)))      # contrast/icon/power
        self.i2c.write_byte_data(self.addr, 0, 0x6B)    # follower control
        # self.i2c.write_byte_data(self.addr, 0, 0x6c)    # follower control
        time.sleep(0.2)

    def clear(self):
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        self.i2c.write_byte_data(self.addr, 0, 0x70)    # Constract
        self.i2c.write_byte_data(self.addr, 0, 0x0C)    # Display On
        self.i2c.write_byte_data(self.addr, 0, 0x01)    # Clear Display
        self.i2c.write_byte_data(self.addr, 0, 0x06)    # Entry Mode Set
        time.sleep(0.2)

    def puts(self, msg):
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        [self.i2c.write_byte_data(self.addr, 0x40, ord(c)) for c in msg]

    def setaddress(self, line, col):
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        self.i2c.write_byte_data(self.addr, 0, 0x80 | (0x40 if line > 0 else 0) | col)

    # set original character
    def setcg(self, no, cg):
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        self.i2c.write_byte_data(self.addr, 0, 0x40 | (no << 3))
        [self.i2c.write_byte_data(self.addr, 0x40, c) for c in cg]

    # Display original character
    def putcg(self, line, col, no):
        self.setaddress(line, col)
        self.i2c.write_byte_data(self.addr, 0x40, no)

    def convert_message(self, message):
        char_code_list = []
        for char in message:
            if char not in CHAR_TABLE:
                char_code_list += CHAR_TABLE['?']   
            else:   
                char_code_list += CHAR_TABLE[char]
#        if len(char_code_list) > 8:
#            raise ValueError('Exceeds maximum length of characters for each line: 16')
        return char_code_list

    def put_message(self, message):
        char_code_list = self.convert_message(message)
        self.i2c.write_byte_data(self.addr, 0, 0x38)    # function set(IS=0)
        for code in char_code_list:
            self.i2c.write_byte_data(self.addr, 0x40, code)

if __name__ == '__main__':
    try:
        lcd = i2clcd()

        # set original char : ℃
        cgchar0 = (0b00000,
                   0b00001,
                   0b01100,
                   0b10010,
                   0b10000,
                   0b10010,
                   0b01100)
        lcd.setcg(0, cgchar0)

        lcd.clear()

        while True:
            lcd.setaddress(0, 0)
#            lcd.puts('ガギグゲゴ')
            lcd.put_message('Apl パイ')
            lcd.putcg(0, 7, 0)
            # 現在時間
            lcd.setaddress(1, 0)
            lcd.put_message(datetime.now().strftime("%H:%M:%S"))
#            lcd.puts(datetime.now().strftime("%H:%M:%S"))
            time.sleep(1)

    except KeyboardInterrupt:
        pass
