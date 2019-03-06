# Blynk Python Library
Blynk Python/Micropython Library

TODO: BADGES
If you like **Blynk** - give it a star, or fork it and contribute! 
[![GitHub stars](https://img.shields.io/github/stars/blynkkk/blynk-library.svg?style=social&label=Star)](https://github.com/blynkkk/blynk-library/stargazers) 
[![GitHub forks](https://img.shields.io/github/forks/blynkkk/blynk-library.svg?style=social&label=Fork)](https://github.com/blynkkk/blynk-library/network)
__________

## What is Blynk?
### Blynk is **the most popular Internet of Things platform** for connecting hardware to the cloud, designing apps to control them, and managing your deployed products at scale. 

- With Blynk Library you can connect **over 400 hardware models** (including ESP8266, ESP32, NodeMCU, all Arduinos, Raspberry Pi, Particle, Texas Instruments, etc.)to the Blynk Cloud.
Full list of supported hardware can be found [here](https://github.com/blynkkk/blynkkk.github.io/blob/master/SupportedHardware.md).

- With Blynk apps for **iOS** and **Android** apps you can easily build graphic interfaces for all of your projects by simply dragging and dropping widgets on your smartphone. It's a purely WYSIWG experience: no coding on iOS or Android required. 

- Hardware can connect to Blynk Cloud (open-source server) over the Internet using hardware connectivity on board, or with the use of various shields (Ethernet, WiFi, GSM, LTE, etc). Blynk Cloud is available for every user of Blynk **for free**. Local connection between over Bluetooth is also possible. 

![Blynk Banner][blynk-banner]

## Download

**Blynk App: 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/googleplay.svg" width="18" height="18" /> Google Play][blynk-app-android] | 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/apple.svg" width="18" height="18" /> App Store][blynk-app-ios]**

Optionally you can install **Blynk [Local Server](https://github.com/blynkkk/blynk-server)** and run everything locally. However, **Blynk Cloud is free** for anyone who is using Blynk for personal (non-commercial) use.

![Blynk Architecture][blynk-architecture]

## Installation 

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

## Features
Library allows to communicate with public or custom [Blynk Server][blynk-server].
 
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
 

## [Quickstart][blynk-docs]
Install Blynk python  library
Download Blynk App ([GooglePlay][blynk-app-android] | [Apple][blynk-app-ios]) and register within it. 
During registration personal auth token will be provided. Use this token within your python scripts to pass
[public][blynk-server-public] or [custom][blynk-server] Blynk server authentification.

#### Usage example
```py
import blynklib

BLYNK_AUTH = '<YourAuthToken>'
blynk = blynklib.Blynk(BLYNK_AUTH)

# register handler for virtual pin V11 reading
# for example when some Blynk App widget asks virtual pin data from server periodically    
@blynk.handle_event('read V11')
def read_virtual_pin_handler(pin):
    
    # user code for this event goes here
    # ...
    # Example: calculate, get sensor values, current time etc
    
    # update current virtual pin value on server 
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
