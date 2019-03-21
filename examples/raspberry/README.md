# [Raspberry Pi][raspberry]
A small and affordable computer that you can use to learn programming

![Blynk Banner][raspberry-banner]

## Board preparation

 - Micro Sd card will be needed with capacity >= 8 Gb (for installation without GUI 4Gb card can be used)  
 - Download latest **[raspbian os][raspbian]** (debian based os for raspberry devices)
 - Examine these instructions **[windows setup][install-windows]**, **[linux setup][install-linux]**,
   **[headless-setup][install-headless]**, **[remote vnc][install-vnc]**, **[wifi][install-wifi]**.
 
 - For GPIO interface communication **[wiring Pi][wiring-pi]** should be installed
   This will allow you to communicate with GPIO pins directly via board CLI.
    
   For example:
   ```bash
   # prints pin diagram appropriate to your Pi
   gpio readall    
   ```
 - install ***rpi.gpio*** module to communicate with GPIO pins from Python scripts
   ```bash
   sudo apt-get update
   sudo apt-get -y install python-rpi.gpio
   
   # sudo apt-get -y install python3-rpi.gpio  # for Python3
   ```      
## Security

Protect your device and to avoid situations when it can be used without your permission.

Read this [guide][raspberry-security] to understand how to impove rasberry Pi security.
 



  [raspberry]: https://www.raspberrypi.org/
  [raspberry-banner]: https://www.raspberrypi.org/app/uploads/2018/03/770A5842-1612x1080.jpg
  [raspbian]: https://www.raspberrypi.org/downloads/raspbian/
  [install-windows]: https://howtoraspberrypi.com/create-raspbian-sd-card-raspberry-pi-windows/
  [install-headless]: https://howtoraspberrypi.com/how-to-raspberry-pi-headless-setup/
  [install-linux]: https://howtoraspberrypi.com/create-sd-card-raspberry-pi-command-line-linux/
  [install-vnc]:https://howtoraspberrypi.com/raspberry-pi-vnc/
  [install-wifi]: https://howtoraspberrypi.com/connect-wifi-raspberry-pi-3-others/
  [wiring-pi]: http://wiringpi.com/download-and-install/
  [raspberry-security]: https://www.raspberrypi.org/documentation/configuration/security.md