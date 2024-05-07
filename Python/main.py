import Lcd1_14driver
from machine import UART,I2C,Pin,PWM
import time
import sys
from time import sleep
import _thread

from PicoDHT22 import PicoDHT22

import PicoCCS811

LCD = Lcd1_14driver.Lcd1_14()

#------joystck pin declaration----- 
joyRight = Pin(20,Pin.IN,Pin.PULL_UP)
joyDown  = Pin(18,Pin.IN,Pin.PULL_UP)
joySel   = Pin(3,Pin.IN,Pin.PULL_UP)
joyLeft  = Pin(16,Pin.IN,Pin.PULL_UP)
joyUp    = Pin(2,Pin.IN,Pin.PULL_UP)

#------button pin declaration----- 
btnA     = Pin(15,Pin.IN,Pin.PULL_UP)
btnB     = Pin(17,Pin.IN,Pin.PULL_UP)

BL = 13   # lcd back light pin declaration

#------global declaration----- 
interrupt_rgt_flag=0
interrupt_dwn_flag=0
interrupt_sel_flag=0
interrupt_lft_flag=0
interrupt_up_flag=0
interrupt_a_flag=0
interrupt_b_flag=0

interrupt_total_flag=4

interrupt_ud_flag=0
interrupt_lr_flag=0

def callback_rgt(pin):
    global interrupt_rgt_flag
    interrupt_rgt_flag=1

def callback_dwn(pin):
    global interrupt_dwn_flag
    interrupt_dwn_flag=1
    
def callback_sel(pin):
    global interrupt_sel_flag
    interrupt_sel_flag=1
    
def callback_lft(pin):
    global interrupt_lft_flag
    interrupt_lft_flag=1
    
def callback_up(pin):
    global interrupt_up_flag
    interrupt_up_flag=1
    
def callback_btn_a(pin):
    global interrupt_a_flag
    interrupt_a_flag=1
    
def callback_btn_b(pin):
    global interrupt_b_flag
    interrupt_b_flag=1

def pico_lcd_114():
    global interrupt_rgt_flag
    global interrupt_dwn_flag
    global interrupt_sel_flag
    global interrupt_lft_flag
    global interrupt_up_flag
    global interrupt_a_flag
    global interrupt_b_flag
    
    global interrupt_ud_flag
    global interrupt_lr_flag
    
    pwm = PWM(Pin(BL))
    pwm.freq(100)
    pwm.duty_u16(32768)    #max value is 65535
    LCD.fill(LCD.white)
    
    LCD.lcd_show()
    LCD.write_text("Pico Lcd",x=30,y=20,size=2,color=LCD.black)
    LCD.write_text("Pico WIFI",x=30,y=60,size=2,color=LCD.black)
    LCD.write_text("Made By Yeo ",x=30,y=100,size=2,color=LCD.black)
                    
    LCD.hline(10,10,220,LCD.blue)
    LCD.hline(10,125,220,LCD.blue)
    LCD.vline(10,10,115,LCD.blue)
    LCD.vline(230,10,115,LCD.blue)
            
    LCD.lcd_show()
        
    joyRight.irq(trigger=Pin.IRQ_FALLING, handler=callback_rgt)
    joyDown.irq(trigger=Pin.IRQ_FALLING, handler=callback_dwn)
    joySel.irq(trigger=Pin.IRQ_FALLING, handler=callback_sel)
    joyLeft.irq(trigger=Pin.IRQ_FALLING, handler=callback_lft)
    joyUp.irq(trigger=Pin.IRQ_FALLING, handler=callback_up)
    btnA.irq(trigger=Pin.IRQ_FALLING, handler=callback_btn_a)
    btnB.irq(trigger=Pin.IRQ_FALLING, handler=callback_btn_b)

    while True:
            
        if interrupt_rgt_flag is 1:
            interrupt_rgt_flag = 0
                      
        if interrupt_dwn_flag is 1:
            if interrupt_ud_flag > ( interrupt_total_flag - 1 ) :
                interrupt_ud_flag = 0
            else :
                interrupt_ud_flag = interrupt_ud_flag + 1
            
            print("Joystick Down {}", interrupt_ud_flag)
            
            interrupt_dwn_flag = 0

        if interrupt_sel_flag is 1:
            print("Joystick Select")
            interrupt_sel_flag = 0
                
        if interrupt_lft_flag is 1:
            print("Joystick Left")
            interrupt_lft_flag = 0
           
        if interrupt_up_flag is 1:
            if interrupt_ud_flag == 0 :
                interrupt_ud_flag = 4
            else :
                interrupt_ud_flag = interrupt_ud_flag - 1
                
            print("Joystick UP {}", interrupt_ud_flag)
                
            interrupt_up_flag = 0
                
        if interrupt_a_flag is 1:
            print("Button A")
            interrupt_a_flag = 0
                
        if interrupt_b_flag is 1:
            print("Button B")
            interrupt_b_flag = 0
                
    LCD.lcd_show()
    time.sleep(0.5)
    LCD.fill(0xFFFF)
    
def pico_dh22_ccs811():
    """
    Co2 ppm
    400~600 Excellent
    700~800 Good
    900~1000 Fair
    1100~1500 Fair (Ventilation Recommended)
    1600~2100 BAD (Ventilation REQUIRED)

    TVOC ppb
    0~220 Good
    221~660 Moderate (Ventilation Recommended)
    661~1430 High (Ventilation REQUIRED)
    """
    
    dht22 = PicoDHT22(Pin(4,Pin.IN,Pin.PULL_UP))
    
    i2c = I2C(1, sda=Pin(6), scl=Pin(7))
    c = PicoCCS811.CCS811(i2c)
    c.setup()
    
    while True:
        T, H = dht22.read()
        
        if T is None:
            LCD.write_text("sensor error",x=0,y=60,size=3,color=LCD.white)
        else:
            if interrupt_ud_flag is 0:
                LCD.fill(LCD.white)
                LCD.write_text("Pico Lcd",x=30,y=20,size=2,color=LCD.black)
                LCD.write_text("Pico WIFI",x=30,y=60,size=2,color=LCD.black)
                LCD.write_text("Made By Yeo ",x=30,y=100,size=2,color=LCD.black)
                    
                LCD.hline(10,10,220,LCD.blue)
                LCD.hline(10,125,220,LCD.blue)
                LCD.vline(10,10,115,LCD.blue)
                LCD.vline(230,10,115,LCD.blue)
                
            if interrupt_ud_flag is 1:
                LCD.fill(LCD.white)
                LCD.write_text("-Temperature-",x=0,y=30,size=2,color=LCD.black)
                LCD.write_text("T={:3.1f}C".format(T),x=0,y=85,size=3,color=LCD.black)
                
            if interrupt_ud_flag is 2:
                LCD.fill(LCD.white)
                LCD.write_text("-Humidity-",x=0,y=30,size=2,color=LCD.black)
                LCD.write_text("H={:3.1f}%".format(H),x=0,y=85,size=3,color=LCD.black)
                
            if interrupt_ud_flag is 3:
                LCD.fill(LCD.white)
                LCD.write_text("Carbon Dioxide",x=0,y=30,size=2,color=LCD.black)
                if c.data_available():
                    r = c.read_algorithm_results()
                    if int("{}".format(r[0])) < 601 :
                        LCD.write_text("CO2={}".format(r[0]),x=0,y=85,size=3,color=LCD.blue)
                    elif int("{}".format(r[0])) > 600 and int("{}".format(r[0])) < 901 :
                        LCD.write_text("CO2={}".format(r[0]),x=0,y=85,size=3,color=LCD.green)
                    elif int("{}".format(r[0])) > 900 and int("{}".format(r[0])) < 1601 :
                        LCD.write_text("CO2={}".format(r[0]),x=0,y=85,size=3,color=LCD.pink)
                    elif int("{}".format(r[0])) > 1600 :
                        LCD.write_text("CO2={}".format(r[0]),x=0,y=85,size=3,color=LCD.red)
                    else :
                        LCD.write_text("CO2={}".format(r[0]),x=0,y=85,size=3,color=LCD.blue)
                else :
                    LCD.write_text("Wait for ...",x=0,y=85,size=2,color=LCD.red)
                    
            if interrupt_ud_flag is 4:
                LCD.fill(LCD.white)
                LCD.write_text("Total",x=0,y=10,size=2,color=LCD.black)
                LCD.write_text("Volatile",x=0,y=30,size=2,color=LCD.black)
                LCD.write_text("Organic",x=0,y=50,size=2,color=LCD.black)
                LCD.write_text("Compounds",x=0,y=70,size=2,color=LCD.black)
                if c.data_available():
                    r = c.read_algorithm_results()
                    if int("{}".format(r[1])) < 221 :
                        LCD.write_text("tVOC={}".format(r[1]),x=0,y=105,size=3,color=LCD.blue)
                    elif int("{}".format(r[1])) > 220 and int("{}".format(r[1])) < 661 :
                        LCD.write_text("tVOC={}".format(r[1]),x=0,y=105,size=3,color=LCD.pink)
                    elif int("{}".format(r[1])) > 660 :
                        LCD.write_text("tVOC={}".format(r[1]),x=0,y=105,size=3,color=LCD.red)
                    else :
                        LCD.write_text("tVOC={}".format(r[1]),x=0,y=105,size=3,color=LCD.blue)
                else :
                    LCD.write_text("Wait for ...",x=0,y=105,size=2,color=LCD.red)
            
        LCD.lcd_show()
        time.sleep(1)
        
if __name__=='__main__':
    
    try:
        start_thread = _thread.start_new_thread(pico_dh22_ccs811, ())
        pico_lcd_114()
    
    except KeyboardInterrupt:
        pass
