# Blynk Python Library
Blynk Python/Micropython Library

## What is Blynk?
Blynk provides **iOS** and **Android** apps to control any hardware **over the Internet** or **directly using Bluetooth**.
You can easily build graphic interfaces for all your projects by simply dragging and dropping widgets, **right on your smartphone**.
Blynk is **the most popular IoT platform** used by design studios, makers, educators, and equipment vendors all over the world.

`![Blynk Banner][blynk-banner]

## Download

**Blynk App: 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/googleplay.svg" width="18" height="18" /> Google Play][blynk-app-android] | 
[<img src="https://cdn.rawgit.com/simple-icons/simple-icons/develop/icons/apple.svg" width="18" height="18" /> App Store][blynk-app-ios]**

Optionally: **[Blynk Server][blynk-server]**. Public Blynk Cloud is free for anyone who is using Blynk for personal (non-commercial) purposes.

![Blynk Architecture][blynk-architecture]

## [Installation][blynk-io] 

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
Library allows to communicate with public or custom [Blynk Server][blynk-server]

##### List of available operations:
 - connect/disconnect events subscribe
 - read/write virtual pins events subscribe
 - virtual pin write
 - virtual pin sync
 - internal app notifications
 - email notifications
 - set widget property
 

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

@blynk.handle_event("connect")
def connect_handler():
    print('Connect to Blynk server successful!')

while True:
    blynk.run()
```

Examine more Blynk python library **[examples][blynk-py-examples]** to be familiar with basic features usage.


### License
This project is released under The MIT License (MIT)



  [blynk-io]: https://github.com/blynkkk/blynkkk.github.io
  [blynk-architecture]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/architecture.png
  [blynk-banner]: https://github.com/blynkkk/blynkkk.github.io/blob/master/images/GithubBanner.jpg
  [blynk-server]: https://github.com/blynkkk/blynk-server
  [blynk-server-public]: blynk-cloud.com
  [blynk-docs]: https://docs.blynk.cc/
  [blynk-py-examples]: https://github.com/blynkkk/lib-python/blob/master/examples
  [blynk-app-android]: https://play.google.com/store/apps/details?id=cc.blynk
  [blynk-app-ios]: https://itunes.apple.com/us/app/blynk-control-arduino-raspberry/id808760481?ls=1&mt=8
  