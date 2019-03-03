# [ESP32 Micropython][esp32]

![esp32][esp32-banner]
## Board preparation

 - download latest micropython [firmware][micropython-download] for your board
 - on your host system install python3 
 - install [esptool][micropython-esptool], [rshell][micropython-rshell], [ampy][micropython-ampy] on your host to communicate with esp32 board
    ```bash
    # Example on Linux 
    sudo pip3 install esptool
    sudo pip3 install rshell
    sudo pip3 install adafruit-ampy
    ```

 - connect board via USB. Run command: 
   ```bash
    dmesg | grep tty
   ```
    that will help to find ttyUSB connection port.This port will be used later for all communication operations
     
 - check board flash status. (In this example and below we assume that port=ttyUSB0)
   ```bash
    esptool.py --port /dev/ttyUSB0 flash_id
   ```
  
 - erase board flash before new firmware uploading
   ```bash
    esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   ```
    
 - burn new firmware
   ```bash
    esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 <your esp32 firmware .bin>
   ```

## Board CLI

 - For board CLI access [rshell][micropython-rshell] can be used:
   ```bash
    rshell --buffer-size=30 -p /dev/ttyUSB0
   ```
   after board prompt appears ">" you will have access to some board commands:
   ```text
   args      cat       connect   echo      exit      filetype  ls        repl      rsync
   boards    cd        cp        edit      filesize  help      mkdir     rm        shell 
   ```
 - **[repl][micropython-repl]** command will start micropython interactive shell.
   Also this shell can be used for board soft reboots(Ctrl+D). Hard reboots can be done by board "rst" button.
   
   
## Board files/directories operations
  
 - **[ampy][micropython-ampy]** utility can be used for storing/deleting files,
   directories creation/removing and scripts run
   ```bash
   export AMPY_PORT=/dev/ttyUSB0
   ampy mkdir /lib
   ampy put blynklib.py /lib/blynklib.py
   ampy put test.py test.py
   ampy run test.py
   ```
   

## Micropython libraries compiltation 

Micropython provides ability to compile source code into .mpy frozen module file
Main advantage of this that .mpy files will consume less RAM compared
to raw Python .py source files 

For .mpy file compilation you need:
 - get [mpy-cross][micropython-mpy-cross] tool
   ```bash
   git clone https://github.com/micropython/micropython.git
   cd micropython/mpy-cross
   make
   ```
 - optionally get heapsize of your board via **[repl][micropython-repl]**.
   ```text
   >>> import gc
   >>> gc.collect()
   >>> gc.mem_free()
   2812256
   ```
 - compile source code and get .mpy file
   ```bash
   ./mpy-cross -X heapsize=2812256 blynklib.py
   ```
 - .mpy files in the same manner can be placed to board libs with **[ampy][micropython-ampy]**
   as usual .py file
   ```bash
   ampy put blynklib.mpy /lib/blynklib.mpy
   ```
   and imported within user scripts
   ```python
   # start of user script
   import blynklib
   ```              
  
 
  [esp32]: http://esp32.net
  [esp32-banner]: https://i.ytimg.com/vi/30f1n9h3aSc/maxresdefault.jpg
  [micropython-download]: http://micropython.org/download#esp32
  [micropython-repl]: https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html
  [micropython-ampy]: https://github.com/pycampers/ampy
  [micropython-rshell]: https://github.com/dhylands/rshell
  [micropython-esptool]: https://github.com/espressif/esptool
  [micropython-mpy-cross]: https://pypi.org/project/mpy-cross/