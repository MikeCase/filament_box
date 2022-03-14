from rpi_lcd import LCD
import Adafruit_DHT
from gpiozero import Motor
import subprocess
import gspread
import time
from datetime import datetime
import csv

gc = gspread.service_account(filename="/home/pi/filament_box/creds.json")
sht = gc.open_by_key('1QyWozG81ChQUNG2YsGM8lmWdO4-LnrgOs9o0ZrzOteA').sheet1

LCDADDRESS = 0x3f
PIN = 23

sensor = Adafruit_DHT.DHT11
lcd = LCD(address=LCDADDRESS)
fan_one = Motor(forward=13, backward=12)
fan_two = Motor(forward=7, backward=5)
def get_ip():
    # Get the IP address of the RPi
    ip_address = subprocess.run(['hostname', '-I'], capture_output=True)
    return ip_address.stdout.decode()

def save_values(hum, temp):
    # Save data to google sheets.  
    now = str(datetime.now())
    try:
        sht.append_row([hum, temp, now])
    except APIError:
        time.sleep(30)
        sht.append_row([hum, temp, now]) 

def read_values():
    humidity, temp = Adafruit_DHT.read_retry(sensor, PIN)
    return humidity, temp

if __name__ == "__main__":
    while True:
        humidity, temp = read_values()
        if humidity is not None and temp is not None:
            # Convert temperature to freedom units.
            temp_in_f = temp * (9/5) + 32
            
            # Display the temperature and relative humidity on the lcd
            lcd.text(f'Temp: {temp_in_f} F', 1)
            lcd.text(f'RH: {humidity}%', 2)

            # Display the IP of the unit on the lcd.
            lcd.text(f'IP: {get_ip()}', 3)
            save_values(humidity, temp_in_f)
            if humidity > 49.0:
                fan_one.forward()
                fan_two.forward()
            else:
                fan_one.stop()
                fan_two.stop()
        else:
            lcd.text(f'OH NO!, Trying again', 4)

        time.sleep(600)
