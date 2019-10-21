# Blynk Python Library
This library provides API to connect IoT hardware that supports Micropython/Python to Blynk Cloud and communiate with Blynk apps (iOS and Android). You can send raw and processed sensor data and remotely control anything that is connected to your hardware (relays, motors, servos) from anywhere in the world.  

[![GitHub version](https://img.shields.io/github/release/blynkkk/lib-python.svg)][lib-release]
[![GitHub download](https://img.shields.io/github/downloads/blynkkk/lib-python/total.svg)][lib-release]
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/lib-python.svg)][lib-stars]
[![GitHub issues](https://img.shields.io/github/issues/blynkkk/lib-python.svg)][lib-issues]
[![Build Status](https://img.shields.io/travis/blynkkk/lib-python.svg)][lib-travis]
[![License](https://img.shields.io/badge/license-MIT-blue.svg)][lib-licence]

If you like **Blynk** - give it a star, or fork it and contribute! 
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/lib-python.svg?style=social&label=Star)][lib-stars] 
[![GitHub forks](https://img.shields.io/github/forks/blynkkk/lib-python.svg?style=social&label=Fork)][lib-network]


![Blynk Banner][blynk-banner]
### Blynk is **the most popular Internet of Things platform** for connecting hardware to the cloud, designing apps to control them, and managing your deployed devices at scale. 

- With Blynk Library you can connect **over 400 hardware models** (including ESP8266, ESP32, NodeMCU, all Arduinos, Raspberry Pi, Particle, Texas Instruments, etc.)to the Blynk Cloud.
Full list of supported hardware can be found [here][blynk-hw].

- With Blynk apps for **iOS** and **Android** apps you can easily build graphic interfaces for all of your projects by simply dragging and dropping widgets on your smartphone. It's a purely WYSIWG experience: no coding on iOS or Android required. 

- Hardware can connect to Blynk Cloud (open-source server) over the Internet using hardware connectivity on board, or with the use of various shields (Ethernet, WiFi, GSM, LTE, etc). Blynk Cloud is available for every user of Blynk **for free**. 




## Installation of Blynk Python Library 

#### Installation via python pip
 - Check python availability in your system. 
   ```commandline
   python --version
   ``` 
   To exclude compatibility issue preferable versions are Python 2.7.9 (or greater) or Python 3.4 (or greater)
   If python not present you can download and install it from [here][python-org]. 
   
   **NOTE:** To run python in "sandbox" you can try **virtualenv** module. Check [this document][virtual-env] how to do it.
      
 - If you’re using preferable versions of python mentioned above, then **pip** comes installed with Python by default. 
   Check pip availability:
   ```commandline
   pip --version
   ```    
 - Install blynk library
   ```commandline
   sudo pip install blynklib
   ``` 

#### Manual installation
Library can be installed locally from git sources: 
   
```commandline 
git clone https://github.com/blynkkk/lib-python.git
cd lib-python
pip install --user -e .

# sudo pip install -e .  # if installation needed not for current but for all users
``` 

#### Testing
You can run unit tests for cPython version of library (blynklib_cp.py) systems using the command:

    python setup.py test

**NOTE:** Unit tests for Micropython ENV are not available yet.

#### Micropython installation
Some hardware platforms can use **[Micropython][micropython-org]** package.
This is helpful for preliminary testing and debugging of your code outside of real hardware. Supported platforms 
and related installation docs can be found [here][micropython-pkg].


## Features
This library supports Python2, Python3, and Micropython.

- Communication with public or local [Blynk Server][blynk-server].
- Exchange any data between your hardware and app
- Tested to work with: Raspberry Pi (any), ESP32, ESP8266

##### List of available operations:
 - Subscribe to connect/disconnect events 
 - Subscribe to read/write events of [virtual pins][blynk-vpins]
 - [Virtual Pin][blynk-vpins] write
 - [Virtual Pin][blynk-vpins] sync
 - Send mobile app push notifications
 - Send email notifications
 - Send twitter notifications
 - Change widget GUI parameters in Blynk app based on hardware input
 

## Quickstart 
1. Install Blynk python library as described above
2. Install Blynk App: 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/googleplay.svg" width="18" height="18" /> Google Play][blynk-app-android] | 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/apple.svg" width="18" height="18" /> App Store][blynk-app-ios]

- Create new account in Blynk app using your email address
- Create a new Project in Blynk app 
- You will get Auth Token delivered to your email account. 
- Put this Auth Token within your python script to authenticate your device on [public][blynk-server-public] or [local][blynk-server]

```python
BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
```

#### Usage example
```python
import blynklib

BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
# base lib init
blynk = blynklib.Blynk(BLYNK_AUTH)
 
# advanced options of lib init
# from __future__ import print_function
# blynk = blynklib.Blynk(BLYNK_AUTH, server='blynk-cloud.com', port=80, ssl_cert=None, heartbeat=10, rcv_buffer=1024, log=print)

# Lib init with SSL socket connection
# blynk = blynklib.Blynk(BLYNK_AUTH, port=443, ssl_cert='<path to local blynk server certificate>')
# current blynk-cloud.com certificate stored in project as 
# https://github.com/blynkkk/lib-python/blob/master/certificate/blynk-cloud.com.crt

# register handler for Virtual Pin V22 reading by Blynk App.
# when a widget in Blynk App asks Virtual Pin data from server within given configurable interval (1,2,5,10 sec etc) 
# server automatically sends notification about read virtual pin event to hardware
# this notification captured by current handler 
@blynk.handle_event('read V22')
def read_virtual_pin_handler(pin):
    
    # your code goes here
    # ...
    # Example: get sensor value, perform calculations, etc
    sensor_data = '<YourSensorData>'
    critilcal_data_value = '<YourThresholdSensorValue>'
        
    # send value to Virtual Pin and store it in Blynk Cloud 
    blynk.virtual_write(pin, sensor_data)
    
    # you can define if needed any other pin
    # example: blynk.virtual_write(24, sensor_data)
        
    # you can perform actions if value reaches a threshold (e.g. some critical value)
    if sensor_data >= critilcal_data_value
        
        blynk.set_property(pin, 'color', '#FF0000') # set red color for the widget UI element 
        blynk.notify('Warning critical value') # send push notification to Blynk App 
        blynk.email(<youremail@email.com>, 'Email Subject', 'Email Body') # send email to specified address
        
# main loop that starts program and handles registered events
while True:
    blynk.run()
```
## Other Examples

Examples can be found **[here][blynk-py-examples]** Check them all to get familiar with main Blynk API features.

##### Core operations:
- [01_write_virtual_pin.py](https://github.com/blynkkk/lib-python/blob/master/examples/01_write_virtual_pin.py): How to read incoming data from Blynk app to Virtual Pin and use it in your code
- [02_read_virtual_pin.py](https://github.com/blynkkk/lib-python/blob/master/examples/02_read_virtual_pin.py): How to update value on Virtual Pin
- [03_connect_disconnect.py](https://github.com/blynkkk/lib-python/blob/master/examples/03_connect_disconnect.py): Managing connection with Blynk Cloud
- [04_email.py](https://github.com/blynkkk/lib-python/blob/master/examples/04_email.py): How to send send email and push notifications from your hardware                
- [05_set_property_notify.py](https://github.com/blynkkk/lib-python/blob/master/examples/05_set_property_notify.py): How to change some of widget UI properties like colors, labels, etc  
- [06_terminal_widget.py](https://github.com/blynkkk/lib-python/blob/master/examples/06_terminal_widget.py): Communication between hardware and app through Terminal widget)
- [07_tweet_and_logging.py](https://github.com/blynkkk/lib-python/blob/master/examples/07_tweet_and_logging.py): How to post to Twitter and log events from your hardware
- [08_blynk_timer.py](https://github.com/blynkkk/lib-python/blob/master/examples/08_blynk_timer.py): How send data periodically from hardware by using **[Blynk Timer][blynktimer-doc]**
- [09_sync_virtual_pin.py](https://github.com/blynkkk/lib-python/blob/master/examples/09_sync_virtual_pin.py): How to sync virtual pin states and properties
- [10_rtc_sync.py](https://github.com/blynkkk/lib-python/blob/master/examples/10_rtc_sync.py): How to perform RTC sync with blynk server 
- [11_ssl_socket.py](https://github.com/blynkkk/lib-python/blob/master/examples/10_ssl_socket.py): SSL server connection. Feature available only fo cPython. 

##### Raspberry Pi (any):
Read [Raspberry Pi guide](https://github.com/blynkkk/lib-python/tree/master/examples/raspberry) first.

- [01_weather_station_pi3b.py](https://github.com/blynkkk/lib-python/blob/master/examples/raspberry/01_weather_station_pi3b.py) Connect DHT22; BMP180 sensors and send data to Blynk app

##### ESP32
Read [ESP32 guide](https://github.com/blynkkk/lib-python/tree/master/examples/esp32) first.
- [01_touch_button.py](https://github.com/blynkkk/lib-python/blob/master/examples/esp32/01_touch_button.py) Connect TTP223B touch sensor to ESP32 and react to touch
- [02_terminal_cli.py](https://github.com/blynkkk/lib-python/blob/master/examples/esp32/02_terminal_cli.py) Communication between ESP32 hardware and app through Terminal widget
- [03_temperature_humidity_dht22.py](https://github.com/blynkkk/lib-python/blob/master/examples/esp32/03_temperature_humidity_dht22.py) Connect DHT22 sensor to ESP32 and send data to Blynk app

##### ESP8266
Read [ESP8266 guide](https://github.com/blynkkk/lib-python/tree/master/examples/esp8266) first.
- [01_potentiometer.py](https://github.com/blynkkk/lib-python/blob/master/examples/esp8266/01_potentiometer.py) Cconnect potentiometer to ESP8266 and send resistance value to the app 



### Memory size limitations
For hardware with limited memory size (ex. ESP8266) you can use ***frozen modules*** or ***frozen bytecode*** approaches
to load **blynklib** or any other library to hardware.
  
Read [this document][esp8266-readme] to get more information.

## Documentation and other helpful links

[Full Blynk Documentation](http://docs.blynk.cc/#blynk-firmware) - a complete guide on Blynk features

[Community (Forum)](http://community.blynk.cc) - join a 500,000 Blynk community to ask questions and share ideas

[Help Center](http://help.blynk.cc) - helpful articles on various Blynk aspects

[Code Examples Browser](http://examples.blynk.cc) - browse examples to explore Blynk possibilities

[Official Website](https://blynk.io) 

**Social Media:**

[Facebook](https://www.fb.com/blynkapp) [Twitter](https://twitter.com/blynk_app) [Youtube](https://www.youtube.com/blynk)

[Instagram](https://www.instagram.com/blynk.iot/) [LinkedIn](https://www.linkedin.com/company/b-l-y-n-k/)


## Blynk libraries for other platforms
* [C++](https://github.com/blynkkk/blynk-library)
* [Node.js, Espruino, Browsers](https://github.com/vshymanskyy/blynk-library-js)
* [Python](https://github.com/vshymanskyy/blynk-library-python) (by Volodymyr Shymanskyy)
* [Particle](https://github.com/vshymanskyy/blynk-library-spark)
* [Lua, OpenWrt, NodeMCU](https://github.com/vshymanskyy/blynk-library-lua)
* [OpenWrt packages](https://github.com/vshymanskyy/blynk-library-openwrt)
* [MBED](https://developer.mbed.org/users/vshymanskyy/code/Blynk/)
* [Node-RED](https://www.npmjs.com/package/node-red-contrib-blynk-ws)
* [LabVIEW](https://github.com/juncaofish/NI-LabVIEWInterfaceforBlynk)
* [C#](https://github.com/sverrefroy/BlynkLibrary)

## Contributing
You are very welcome to contribute: stability bugfixes, new hardware support, or any other improvements. Please.


### License
This project is released under The MIT License (MIT)


  [lib-release]: https://github.com/blynkkk/lib-python/releases/latest
  [lib-licence]: https://github.com/blynkkk/lib-python/blob/master/LICENSE
  [lib-travis]: https://travis-ci.org/blynkkk/lib-python
  [lib-issues]: https://github.com/blynkkk/lib-python/issues
  [lib-stars]: https://github.com/blynkkk/lib-python/stargazers
  [lib-network]: https://github.com/blynkkk/lib-python/network
  [blynk-io]: https://github.com/blynkkk/blynkkk.github.io
  [blynk-hw]: https://github.com/blynkkk/blynkkk.github.io/blob/master/SupportedHardware.md
  [blynk-architecture]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/architecture.png
  [blynk-banner]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/GithubBanner.jpg
  [blynk-server]: https://github.com/blynkkk/blynk-server
  [blynk-server-public]: http://blynk-cloud.com
  [blynk-docs]: https://docs.blynk.cc/
  [blynk-py-examples]: https://github.com/blynkkk/lib-python/blob/master/examples
  [blynk-app-android]: https://play.google.com/store/apps/details?id=cc.blynk
  [blynk-app-ios]: https://itunes.apple.com/us/app/blynk-control-arduino-raspberry/id808760481?ls=1&mt=8
  [blynk-vpins]: http://help.blynk.cc/getting-started-library-auth-token-code-examples/blynk-basics/what-is-virtual-pins
  [python-org]: https://www.python.org/downloads/
  [micropython-org]: https://micropython.org/ 
  [micropython-pkg]: https://github.com/micropython/micropython/wiki/Getting-Started
  [virtual-env]: https://virtualenv.pypa.io/en/latest/installation/
  [esp8266-readme]: https://github.com/blynkkk/lib-python/blob/master/examples/esp8266/README.md
  [blynktimer-doc]: https://github.com/blynkkk/lib-python/blob/master/TIMERS.md
