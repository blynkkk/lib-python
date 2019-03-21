# Blynk Python Library
This library provides API to connect IoT hardware that supports Micropython/Python to Blynk Cloud and communiate with Blynk apps (iOS and Android). You can send raw and processed sensor data and remotely control anything that is connected to your hardware (relays, motors, servos) from anywhere in the world.  

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
   
   **NOTE:** To run python in "sandbox" you can try **virtualenv** module. Check [here][virtual-env] on how to do it.
      
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
You can run unit tests on cPython systems using the command:

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

```py
BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
```

#### Usage example
```py
import blynklib

BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
# base lib init
blynk = blynklib.Blynk(BLYNK_AUTH) 
# advanced options of lib init
# from __future__ import print_function
# blynk = blynklib.Blynk(BLYNK_AUTH, server='blynk-cloud.com', port=80, heartbeat=10, rcv_buffer=1024, log=print)

# register handler for Virtual Pin V22 reading.
# for example when a widget in Blynk App asks Virtual Pin data from server within given interval    
@blynk.handle_event('read V22')
def read_virtual_pin_handler(pin):
    
    # your code goes here
    # ...
    # Example: get sensor value, perform calculations, etc
    sensor_data = '<YourCalculatedSensorData>'
    critilcal_data_value = '<YourCriticalSensorValue>'
        
    # send value to Virtual Pin and store it in Blynk Cloud 
    blynk.virtual_write(pin, sensor_data) #example: blynk.virtual_write(24, sensor_data)
        
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

Check **[more_examples][blynk-py-examples]** to get familiar with some of Blynk features.

#### Examples List:

##### Core operations:
- 01_write_virtual_pin.py (how to write to Virtual Pin )
- 02_read_virtual_pin.py  (how to read Virtual Pin )
- 03_connect_disconnect.py (connection management)
- 04_email.py(how to send send email and push notifications) // TODO: combine it into one example               
- 05_set_property_notify.py (how to change some of widget UI properties) // TODO:  move notifications to 04 example 
- 06_terminal_widget.py (communicate between hardware and app through Terminal widget)
- 07_tweet_and_logging.py (how to post to Twitter and log events from your hardware)

##### Raspberry Pi (any):
- 01_weather_station_pi3b.py (Connect DHT22; BMP180 sensors and send data to Blynk app)

##### ESP32
- 01_touch_button.py (Connect TTP223B touch sensor to ESP32 and react to touch)



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
  [python-logo]: 
