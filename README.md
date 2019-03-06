TODO: we need to add IoT to the repository name or somewhere so that we are found through search. Needs investigation.
https://github.com/search?q=iot  - how to get to this list? 

# Blynk Python Library
Blynk Python/Micropython Library

TODO: Generic description of what this library does and which (known) hardware is supported

TODO: BADGES
[![GitHub version](https://img.shields.io/github/release/blynkkk/blynk-library.svg)](https://github.com/blynkkk/blynk-library/releases/latest)
[![GitHub download](https://img.shields.io/github/downloads/blynkkk/blynk-library/total.svg)](https://github.com/blynkkk/blynk-library/releases/latest)
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/blynk-library.svg)](https://github.com/blynkkk/blynk-library/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/blynkkk/blynk-library.svg)](https://github.com/blynkkk/blynk-library/issues)
[![Build Status](https://img.shields.io/travis/blynkkk/blynk-library.svg)](https://travis-ci.org/blynkkk/blynk-library)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/blynkkk/blynk-library/blob/master/LICENSE)

If you like **Blynk** - give it a star, or fork it and contribute! 
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/blynk-library.svg?style=social&label=Star)](https://github.com/blynkkk/blynk-library/stargazers) 
[![GitHub forks](https://img.shields.io/github/forks/blynkkk/blynk-library.svg?style=social&label=Fork)](https://github.com/blynkkk/blynk-library/network)
__________

### Blynk is **the most popular Internet of Things platform** for connecting hardware to the cloud, designing apps to control them, and managing your deployed products at scale. 

- With Blynk Library you can connect **over 400 hardware models** (including ESP8266, ESP32, NodeMCU, all Arduinos, Raspberry Pi, Particle, Texas Instruments, etc.)to the Blynk Cloud.
Full list of supported hardware can be found [here](https://github.com/blynkkk/blynkkk.github.io/blob/master/SupportedHardware.md).

- With Blynk apps for **iOS** and **Android** apps you can easily build graphic interfaces for all of your projects by simply dragging and dropping widgets on your smartphone. It's a purely WYSIWG experience: no coding on iOS or Android required. 

- Hardware can connect to Blynk Cloud (open-source server) over the Internet using hardware connectivity on board, or with the use of various shields (Ethernet, WiFi, GSM, LTE, etc). Blynk Cloud is available for every user of Blynk **for free**. Direct connection over Bluetooth is also possible. 

![Blynk Banner][blynk-banner]

## Download

**Blynk App: 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/googleplay.svg" width="18" height="18" /> Google Play][blynk-app-android] | 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/apple.svg" width="18" height="18" /> App Store][blynk-app-ios]**

Optionally you can install **Blynk [Local Server](https://github.com/blynkkk/blynk-server)** and run everything locally. However, **Blynk Cloud is free** for anyone who is using Blynk for personal (non-commercial) use.

![Blynk Architecture][blynk-architecture]

## Installation 

TODO: needs description or link for installing Python itself. On Windows, Linux, and macOS. If there is a certain version required, explain how to check the version and how to upgrade.

#### Installation via Python pip
    sudo pip install blynklib   


#### Manual installation 
    git clone https://github.com/blynkkk/lib-python.git
    cd lib-python
    pip install --user -e .

    # sudo pip install -e .  # if installation needed not for current but for all users 

#### Testing
You can run unit tests using the command:

    python setup.py test

TODO: what should be the positive result for user? How they can confirm that everything works? 

TODO: troubleshooting: what can go wrong?

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
 

## [Quickstart][blynk-docs]  - why is it linked to docs? 
Install Blynk python  library
Download Blynk App ([GooglePlay][blynk-app-android] | [Apple][blynk-app-ios]) and register within it. 
When you create a new project in Blynk app, you will get Auth Token delivered to your inbox. Use this Auth Token within your python scripts to authenticate your device on
[public][blynk-server-public] or [local][blynk-server]

#### Usage example
```py
import blynklib

BLYNK_AUTH = '<YourAuthToken>' #insert your Auth Token here
blynk = blynklib.Blynk(BLYNK_AUTH) #TODO: Explain what this line does

# register handler for Virtual Pin V11 reading
# for example when a widget in Blynk App asks Virtual Pin data from server within given interval    
@blynk.handle_event('read V11')
def read_virtual_pin_handler(pin):
    
    # user code for this event goes here
    # ...
    # Example: calculate, get sensor values, current time etc
    
    # Can we have a real example similar to arduino int sensorData = analogRead (A0), and then use
    # `sensorData` further in the example? 
    
    # update current Virtual Pin value on server 
    blynk.virtual_write(pin, <USER_CALCULATED_VALUE>)
    # or any other pin if needed
    # blynk.virtual_write(24, '<ANY_OTHER_USER_CALCULATED_VALUE>')
        
    # actions if calculated value become CRITICAL
    if <USER_CALCULATED_VALUE>  >= <USER_DEFINED_CRITICAL_VALUE>
        # set red color for widget that performs periodical virtual pin read operations
        blynk.set_property(pin, 'color', '#FF0000')
        # send internal notification to Blynk App and notification to defined e-mail 
        blynk.notify('Warning critical value')
        blynk.email(<Your e-mail>, 'Device alarm', 'Critical value!')
        
# main loop that starts program and handles registered events
while True:
    blynk.run()
```


Examine more **[examples][blynk-py-examples]** to be familiar with basic features usage.

TODO: can we list all the examples just here + very short description, E.g:
1. How to send email with data from hardware (@antohaUA: please check with Dima regarding limits (number of emails, number of characters). Also people ask about cyrillic and other languages handling.
2.
3.
...

TODO: troubleshooting: what can go wrong?

### License
This project is released under The MIT License (MIT)



  [blynk-io]: https://github.com/blynkkk/blynkkk.github.io
  [blynk-architecture]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/architecture.png
  [blynk-banner]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/GithubBanner.jpg
  [blynk-server]: https://github.com/blynkkk/blynk-server
  [blynk-server-public]: http://blynk-cloud.com
  [blynk-docs]: https://docs.blynk.cc/
  [blynk-py-examples]: https://github.com/blynkkk/lib-python/blob/master/examples
  [blynk-app-android]: https://play.google.com/store/apps/details?id=cc.blynk
  [blynk-app-ios]: https://itunes.apple.com/us/app/blynk-control-arduino-raspberry/id808760481?ls=1&mt=8
  [blynk-vpins]: http://help.blynk.cc/getting-started-library-auth-token-code-examples/blynk-basics/what-is-virtual-pins
