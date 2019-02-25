"""
pip intsall Adafruit-DHT

https://masterkit.ru/blog/articles/raspberry-pi-3-model-b-podklyuchaem-datchik-atmosfernogo-davleniya-bmp180
aptitude show i2c-tools
sudo apt-get install i2c-tools

https://github.com/adafruit/Adafruit_Python_BMP
git clone
sudo python setup.py install

sudo raspi-config
Interfacing Options
I2C enable
sudo i2cdetect -y 1   ->> 77

"""

import blynklib
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085

BLYNK_AUTH = '9448d9f3d18d4910b1d6d026f853a5da'
blynk = blynklib.Blynk(BLYNK_AUTH)


@blynk.handle_event('read V7')
def read_handler(pin):
    # possible sensor modifications .DHT11 .DHT22 .AM2302
    # data pin connected to GPIO17.
    dht22_sensor = Adafruit_DHT.DHT22
    pin = 17
    humidity, temperature = Adafruit_DHT.read_retry(dht22_sensor, pin, retries=5, delay_seconds=1)

    # check that values are not False (mean not None)
    if all([humidity, temperature]):
        print('temperature={} humidity={}'.format(temperature, humidity))
        blynk.set_property(7, 'color', '#f5b041')
        blynk.set_property(8, 'color', '#85c1e9')
        blynk.virtual_write(7, temperature)  # without formatting on App side it can be '{:0.2f}'.format(temperature)
        blynk.virtual_write(8, humidity)
    else:
        print('[ERROR] reading DHT22 sensor data')
        blynk.set_property(7, 'color', '#444444')  # show as disabled that mean we have not captured data in time
        blynk.set_property(8, 'color', '#444444')

    # BMP180
    bmp180_sensor = BMP085.BMP085(busnum=1)
    pressure = bmp180_sensor.read_pressure()
    altitude = bmp180_sensor.read_altitude()
    if all([pressure, altitude]):
        print('pressure={} altitude={}'.format(pressure, altitude))
        blynk.set_property(9, 'color', '#a2d9ce')
        blynk.set_property(10, 'color', '#58d68d')
        blynk.virtual_write(9, pressure / 133.322)  # mm of mercury column  1mm Mc = 133.322 Pa
        blynk.virtual_write(10, altitude)
    else:
        print('[ERROR] reading BMP180 sensor data')
        blynk.set_property(9, 'color', '#444444')  # show as disabled that mean we have not captured data in time
        blynk.set_property(10, 'color', '#444444')


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
