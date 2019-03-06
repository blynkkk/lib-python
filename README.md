# Blynk Python Library
Provides API for [Blynk Server][blynk-server] communication and messaging on IoT/desktop systems with Micropython/Python support. 

[![GitHub version](https://img.shields.io/github/release/blynkkk/lib-python.svg)][lib-release]
[![GitHub download](https://img.shields.io/github/downloads/blynkkk/lib-python/total.svg)][lib-release]
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/lib-python.svg)][lib-stars]
[![GitHub issues](https://img.shields.io/github/issues/blynkkk/lib-python.svg)][lib-issues]
[![Build Status](https://img.shields.io/travis/blynkkk/lib-python.svg)][lib-travis]
[![License](https://img.shields.io/badge/license-MIT-blue.svg)][lib-licence]

If you like **Blynk** - give it a star, or fork it and contribute! 
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/lib-python.svg?style=social&label=Star)][lib-stars] 
[![GitHub forks](https://img.shields.io/github/forks/blynkkk/lib-python.svg?style=social&label=Fork)][lib-network]
__________

### Blynk is **the most popular Internet of Things platform** for connecting hardware to the cloud, designing apps to control them, and managing your deployed products at scale. 

- With Blynk Library you can connect **over 400 hardware models** (including ESP8266, ESP32, NodeMCU, all Arduinos, Raspberry Pi, Particle, Texas Instruments, etc.)to the Blynk Cloud.
Full list of supported hardware can be found [here][blynk-hw].

- With Blynk apps for **iOS** and **Android** apps you can easily build graphic interfaces for all of your projects by simply dragging and dropping widgets on your smartphone. It's a purely WYSIWG experience: no coding on iOS or Android required. 

- Hardware can connect to Blynk Cloud (open-source server) over the Internet using hardware connectivity on board, or with the use of various shields (Ethernet, WiFi, GSM, LTE, etc). Blynk Cloud is available for every user of Blynk **for free**. Direct connection over Bluetooth is also possible. 

![Blynk Banner][blynk-banner]

## Download

**Blynk App: 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/googleplay.svg" width="18" height="18" /> Google Play][blynk-app-android] | 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/apple.svg" width="18" height="18" /> App Store][blynk-app-ios]**

Optionally you can install **Blynk [Local Server][blynk-server]** and run everything locally. However, **Blynk Cloud is free** for anyone who is using Blynk for personal (non-commercial) use.

![Blynk Architecture][blynk-architecture]

## Installation 

#### Installation via python pip
 - Check python availability in your system. 
   ```commandline
   python --version
   ``` 
   To exclude compatibility issue preferable versions are Python 2.7.9 (or greater) or Python 3.4 (or greater)
   If python not present you can download and install it from [here][python-org]. 
      
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
You can run unit tests on Python systems using the command:

    python setup.py test

## Features
Library allows to communicate with public or local [Blynk Server][blynk-server].
 
Supports Python2/Python3/Micropython.

HW support of RaspberryPi/ESP32

##### List of available operations:
 - connect/disconnect events subscribe
 - read/write [virtual pins][blynk-vpins] events subscribe
 - [virtual pin][blynk-vpins] write
 - [virtual pin][blynk-vpins] sync
 - internal app notifications
 - email notifications
 - twitter notifications
 - widget properties modification
 

## Quickstart 
Install Blynk python  library
Download Blynk App ([GooglePlay][blynk-app-android] | [Apple][blynk-app-ios]) and register within it. 
When you create a new project in Blynk app, you will get Auth Token delivered to your inbox. Use this Auth Token within your python scripts to authenticate your device on
[public][blynk-server-public] or [local][blynk-server]

#### Usage example
```py
import blynklib

BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
# base lib init
blynk = blynklib.Blynk(BLYNK_AUTH) 
# advanced options of lib init
# from __future__ import print_function
# blynk = blynklib.Blynk(BLYNK_AUTH, server='blynk-cloud.com', port=80, heartbeat=10, rcv_buffer=1024, log=print)

# register handler for Virtual Pin V22 reading
# for example when a widget in Blynk App asks Virtual Pin data from server within given interval    
@blynk.handle_event('read V22')
def read_virtual_pin_handler(pin):
    
    # user code for this event goes here
    # ...
    # Example: calculate, get sensor values, current time etc
    sensor_data = '<YourCalculatedSensorData>'
    critilcal_data_value = '<YourCriticalSensorValue>'
        
    # update current Virtual Pin value on server 
    blynk.virtual_write(pin, sensor_data)
    # or any other pin if needed
    # blynk.virtual_write(24, sensor_data)
        
    # actions if calculated value become CRITICAL
    if sensor_data >= critilcal_data_value
        # set red color for widget that performs periodical virtual pin read operations
        blynk.set_property(pin, 'color', '#FF0000')
        # send internal notification to Blynk App and notification to defined e-mail 
        blynk.notify('Warning critical value')
        blynk.email(<Your e-mail>, 'Device alarm', 'Critical value!')
        
# main loop that starts program and handles registered events
while True:
    blynk.run()
```
## More Examples

Examine **[more_examples][blynk-py-examples]** to be familiar with basic features usage.

#### Examples List:

##### Core operations:
- 01_write_virtual_pin.py (virtual pin write event handling)
- 02_read_virtual_pin.py  (App read virtual pin events handling)
- 03_connect_disconnect.py (library connect/disconnect events handling)
- 04_email.py(send email support)               
- 05_set_property_notify.py (changing App widget properties and send internal notifications)
- 06_terminal_widget.py (App communication with device through terminal widget)
- 07_tweet_and_logging.py (Tweet messaging and library logging options)

##### Raspberry:
- 01_weather_station_pi3b.py (DHT22; BMP180 sensors usage)

##### ESP32
- 01_touch_button.py (TTP223B sensors usage)



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
