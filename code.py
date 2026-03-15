import BlynkLib
import RPi.GPIO as GPIO
import time
import adafruit_dht
import board
from w1thermsensor import W1ThermSensor
from RPLCD.i2c import CharLCD

BLYNK_AUTH = "xxxx"
blynk = BlynkLib.Blynk(BLYNK_AUTH, server='blynk.cloud', port=80)

GPIO.setmode(GPIO.BCM)

#Setup Pin
waterPump = 6
coolingFan = 5

GPIO.setup(waterPump, GPIO.OUT)
GPIO.setup(coolingFan, GPIO.OUT)

GPIO.output(waterPump, GPIO.LOW)
GPIO.output(coolingFan, GPIO.LOW)

dhtDevice = adafruit_dht.DHT11(board.D16)
sensor_air = W1ThermSensor()

#LCD Setup
lcd = CharLCD('PCF8574', 0x27)
lcd.clear()

#Overall Checking
lcd.write_string("Loading...")
time.sleep(1)

lcd.clear()
lcd.write_string("Checking")
lcd.crlf()
lcd.write_string("Water Pump...")
GPIO.output(waterPump, GPIO.HIGH)
time.sleep(1)
GPIO.output(waterPump, GPIO.LOW)

lcd.clear()
lcd.write_string("Checking")
lcd.crlf()
lcd.write_string("Cooling Fan...")
GPIO.output(coolingFan, GPIO.HIGH)
time.sleep(1)
GPIO.output(coolingFan, GPIO.LOW)

lcd.clear()
lcd.write_string("System Ready")
time.sleep(1)

#Parameter
batasSuhu = 35
waterPump_status = 0
coolingFan_status = 0


@blynk.VIRTUAL_WRITE(0)
def waterPump_control(value):
    global waterPump_status

    waterPump_status = int(value[0])

    print("Blynk V0:", waterPump_status)

    if waterPump_status == 1:
        GPIO.output(waterPump, GPIO.HIGH)
        print("Water Pump ON")
    else:
        GPIO.output(waterPump, GPIO.LOW)
        print("Water Pump OFF")


@blynk.VIRTUAL_WRITE(1)
def coolingFan_control(value):
    global coolingFan_status

    coolingFan_status = int(value[0])

    print("Blynk V1:", coolingFan_status)

    if coolingFan_status == 1:
        GPIO.output(coolingFan, GPIO.HIGH)
        print("Fan ON")
    else:
        GPIO.output(coolingFan, GPIO.LOW)
        print("Fan OFF")


def readSensor():

    #DS18B20
    try:
        suhuAir = round(sensor_air.get_temperature(), 1)
    except:
        suhuAir = 0.0

    #DHT
    suhuUdara = None
    for i in range(3):
        try:
            suhuUdara = dhtDevice.temperature
            if suhuUdara is not None:
                suhuUdara = round(suhuUdara, 1)
                break
        except:
            time.sleep(0.5)

    if suhuUdara is None:
        suhuUdara = 0.0

    return suhuAir, suhuUdara


#Looping Program Utama
try:

    while True:

        blynk.run()

        suhuAir, suhuUdara = readSensor()

        if suhuUdara >= batasSuhu:
            GPIO.output(coolingFan, GPIO.LOW)
            coolingFan_status = 1
        else:
            GPIO.output(coolingFan, GPIO.HIGH)
            coolingFan_status = 0

        blynk.virtual_write(2, suhuAir)
        blynk.virtual_write(3, suhuUdara)
        blynk.virtual_write(4, waterPump_status)
        blynk.virtual_write(5, coolingFan_status)

        lcd.clear()
        lcd.write_string("Air: {:.1f}C".format(suhuAir))
        lcd.crlf()
        lcd.write_string("Udara: {:.1f}C".format(suhuUdara))

        print("Suhu Air   : {:.1f} C".format(suhuAir))
        print("Suhu Udara : {:.1f} C".format(suhuUdara))

        for i in range(5):
            blynk.run()
            time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping...")

    GPIO.output(waterPump, GPIO.LOW)
    GPIO.output(coolingFan, GPIO.LOW)

    lcd.clear()
    lcd.write_string("Program Stop")

    GPIO.cleanup()