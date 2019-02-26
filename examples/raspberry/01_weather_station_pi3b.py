# -*- coding: utf-8 -*-
"""
[WEATHER STATION EXAMPLE (DHT22; BMP180 sensors) PI3b+] =============================================================

PI3b+ pins schema:
    https://www.theengineeringprojects.com/wp-content/uploads/2018/07/introduction-to-raspberry-pi-3-b-plus-2.png

DHT22 sensor:
    - connect VCC sensor line to "+5v" board pin
    - connect GND sensor line to "ground" board pin
    - connect DATA sensor line to board GPIO17
    - pip install Adafruit-DHT

    DHT22 datasheet that may be helpful:
    https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf


BMP180 sensor:
    - connect VIN sensor line to "+3.3v" board pin
    - connect GND sensor line to "ground" board pin
    - connect SCL sensor line to board GPIO3 (SCL)
    - connect SDA sensor line to board GPIO2 (SDA)

    - ensure that i2c-tools package installed in your system 'aptitude show i2c-tools'
    - if not installed run 'sudo apt-get install i2c-tools'
    - ensure that i2c interface was enabled in your system
        'sudo raspi-config'  -> Interfacing Options ->  I2C enable -> Confirm -> then board reboot
    - run 'sudo i2cdetect -y 1' that will detect i2c devices.
        If sensor was connected correctly within output table you will see "77"
    - to install BPM python lib you will need get BMP180 archived project and install lib from local files:
          git clone https://github.com/adafruit/Adafruit_Python_BMP
          cd Adafruit_Python_BMP
          sudo python setup.py install

    BMP180 datasheet that may be helpful:
    https://arduino.ua/docs/BMP085_DataSheet_Rev.1.0_01July2008.pdf


Environment prepare:
In your Blynk App project:
    - add "Notification" widget

    - add "Gauge" widget,
    - bind it to Virtual Pin V7
    - set name "Temperature"
    - set label /pin.##/°C
    - set update time=10 sec and assign 0-100 values range to it

    - add "Gauge" widget,
    - bind it to Virtual Pin V8
    - set name "Humidity"
    - set label /pin.##/ %
    - set update time=10 sec and assign 0-100 values range to it

    - add "Gauge" widget,
    - bind it to Virtual Pin V9
    - set name "Pressure"
    - set label /pin/ Hg
    - set update time=10 sec and assign 0-800 values range to it

    - add "Gauge" widget,
    - bind it to Virtual Pin V10
    - set name "Altitude"
    - set label /pin.##/ m
    - set update time=10 sec and assign 0-1000 values range to it

    - Run the App (green triangle in the upper right corner).
    - define your auth token for current example
    - optionally change default critical temperature value to your own
    - run current example

This started program will periodically call and execute event handler "read_virtual_pin_handler".
that will try to get data from sensors and write them to related virtual pins.
Within App widget values will be updated each 10 sec.
If during cycle there was error in get data operation  - widget colors will be changed to grey (aka disabled state)
and restored on next successful read sensor data operation. Additionally if temperature will be less than
critical value (default = 20°C) handler will send warning notification to on App.

Schema for temperature parameter:
=====================================================================================================================
            +-----------+                        +--------------+                    +--------------+
            |           |                        |              |                    |              |
            | blynk lib |                        | blynk server |                    |  blynk app   |
            |           |                        |  virtual pin |                    |              |
            |           |                        |              |                    |              |
            +-----------+                        +--------------+                    +--------------+
                  |                                     |                                    |
                  |                                     |                                    |
                  |                                     |  widget read frequency = 10 sec    |
                  |                                     +<-----------------------------------+
                  |                                     |                                    |
                  |                                     |                                    |
                  |                                     |  send virtual pin value to widget  |
                  |                                     |                                    |
   event handler  |    read event to hw from server     +----------------------------------->+
  (user function) |                                     |                                    |
       +-----------<------------------------------------+                                    |
       |          |                                     |                                    |
       |          |   write temperature value to pin    |                                    |
       +--------->------------------------------------->+         next widget read event     |
                  | optionally:                         |                                    |
                  |      - set widget property          +<-----------------------------------+
                  |      - send notification            |                                    |
                  |                                     |                                    |
                  +                                     +                                    +
=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""

import blynklib
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085


class Counter:
    cycle = 0


BLYNK_AUTH = 'YourAuthToken'
blynk = blynklib.Blynk(BLYNK_AUTH, heartbeat=15, max_msg_buffer=512)

T_CRI_VALUE = 20.0  # 20.0°C
T_CRI_MSG = 'Low TEMP!!!'
T_CRI_COLOR = '#c0392b'

T_COLOR = '#f5b041'
H_COLOR = '#85c1e9'
P_COLOR = '#a2d9ce'
A_COLOR = '#58d68d'
ERR_COLOR = '#444444'

T_VPIN = 7
H_VPIN = 8
P_VPIN = 9
A_VPIN = 10
GPIO_DHT22_PIN = 17


@blynk.handle_event('read V{}'.format(T_VPIN))
def read_handler(vpin):
    # DHT22
    dht22_sensor = Adafruit_DHT.DHT22  # possible sensor modifications .DHT11 .DHT22 .AM2302. Also DHT21 === DHT22
    humidity, temperature = Adafruit_DHT.read_retry(dht22_sensor, GPIO_DHT22_PIN, retries=5, delay_seconds=1)
    Counter.cycle += 1
    # check that values are not False (mean not None)
    if all([humidity, temperature]):
        print('temperature={} humidity={}'.format(temperature, humidity))
        if temperature <= T_CRI_VALUE:
            blynk.set_property(T_VPIN, 'color', T_CRI_COLOR)
            # send notifications not each time but once a minute (6*10 sec)
            if Counter.cycle % 6 == 0:
                blynk.notify(T_CRI_MSG)
                Counter.cycle = 0
        else:
            blynk.set_property(T_VPIN, 'color', T_COLOR)
        blynk.set_property(H_VPIN, 'color', H_COLOR)
        blynk.virtual_write(T_VPIN, temperature)
        blynk.virtual_write(H_VPIN, humidity)
    else:
        print('[ERROR] reading DHT22 sensor data')
        blynk.set_property(T_VPIN, 'color', ERR_COLOR)  # show aka 'disabled' that mean we errors on data read
        blynk.set_property(H_VPIN, 'color', ERR_COLOR)

    # BMP180
    bmp180_sensor = BMP085.BMP085(busnum=1)
    pressure = bmp180_sensor.read_pressure()
    altitude = bmp180_sensor.read_altitude()
    # check that values are not False (mean not None)
    if all([pressure, altitude]):
        print('pressure={} altitude={}'.format(pressure, altitude))
        blynk.set_property(P_VPIN, 'color', P_COLOR)
        blynk.set_property(A_VPIN, 'color', A_COLOR)
        blynk.virtual_write(P_VPIN, pressure / 133.322)  # mmHg  1mmHg = 133.322 Pa
        blynk.virtual_write(A_VPIN, altitude)
    else:
        print('[ERROR] reading BMP180 sensor data')
        blynk.set_property(P_VPIN, 'color', ERR_COLOR)  # show aka 'disabled' that mean we errors on data read
        blynk.set_property(A_VPIN, 'color', ERR_COLOR)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
