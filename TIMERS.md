# Blynk Timers
There are two options of setting polling timers in **blynk**
    
   - create timers for your functions on hardware side
   - create timers on Blynk App side.
   
### Hardware timers
Existing core library solutions may be helpful for hardware timers creation.
   
   For example:
   - micropython provides [machine.Timer][micropython-timer]
   - for cPython [threading.Timer][threading-timer] can be used
   - etc
   
   Unfortunately mentioned above solutions may be not so lightweight and clear as expected.
   For Quickstart we provide separate [timer module][blynktimer] that allows execute functions periodically or run them once.
   
##### Basic usage examples   
```python
from blynktimer import Timer
blynk_timer = Timer()

# run once timer that will fire after 1 sec   
@blynk_timer.register(1, run_once=True)
def your_run_once_function():
    print('Hello, World!')

# periodical timer that will fire each 5 sec
@blynk_timer.register(5)
def your_periodical_function():
    print('Hello, Blynkers!')

while True:
    blynk_timer.run()
        
```   

##### Advanced usage examples   
```python
import time
from blynktimer import Timer

# disable exception raise if all all timers were stopped
blynk_timer = Timer(no_timers_err=False)


# register two timers for single function with different function parameters
@blynk_timer.register(2, 'p1', 'p2', c=1, run_once=True)
@blynk_timer.register(3, 'fp1', 'fp2', run_once=False)
def function1(a, b, c=2):
    time.sleep(c)
    print('Function params: {} {} {}'.format(a, b, c))


# simple function registration for further stop
@blynk_timer.register(4, run_once=False)
def function2():
    print('Function2')


# list available timers
print(blynk_timer.get_timers())

# switch timer state to stopped by timer id
# id = order_num + '_' + function_name
blynk_timer.stop('2_function2')

while True:
    intervals = blynk_timer.run()
    # print real passed time for timer fired events
    # maybe needed for debug
    if any(intervals):
        print(intervals)
```
   
To get more accuracy for timers intervals it is possible to decrease library WAIT_SEC parameter. Default value = 0.05 sec

### Blynk App timers
Some Blynk app widgets have timer setting where yoy can define (1,2,5,10 etc) seconds intervals for reading 
virtual pin values.

Flow:
 - each N seconds Blynk app widget will do Virtual Pin reading operation.
 - Blynk Server for App read request will return current pin value 
 - Additionally Blynk server will fire read virtual pin event and send it to hardware
 - If read pin event was registered on hardware certain handler will be executed      
   
   [micropython-timer]: https://docs.micropython.org/en/latest/library/machine.Timer.html
   [threading-timer]:https://docs.python.org/3/library/threading.html#threading.Timer
   [blynktimer]: https://github.com/blynkkk/lib-python/blob/master/blynktimer.py 