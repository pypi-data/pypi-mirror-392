# Python-Logger
Logger for python that can write into stdout, create a log file at the end.

## Usage

### Colors

There are multiple colors available, you can use them using Colors.<COLOR>


### Types of log

- log, normal logs
- warn
- error
- debug, can be disabled with parameter self.debug (`debug=False` in constructor)

- success
- failed


### Layout functions

- `section`, create a separation to arrange your logs

```
................................. SECTION .................................
```

- `cadre`, create a rectangle with text inside

```
################################################################################
#                                                                              #
#                                                                              #
#                                    CADRE                                     #
#                                                                              #
#                                                                              #
################################################################################
```


### Macros

- `init`, Create a cadre and start timer
- `end`, stop timer, create a last log with total duration and save into file


### Waiters

There are some waiters to track your process progress:

- `waiting_time`: print the running time of a process

```
My message 4h 2min 42sec
```

- `waiting_animation`: print an animated wheel next to a custom message for a duration

```
[/] My message
```

- `progress_bar`: display a loading bar with a given advencement (ex: 0.42 stands for 42%)

```
[11%] [■■■■■.............................................]
```


### Example

Here is a code exampleto show posibilities

```
from logger_pauwels import Logger, Colors
import time

l = Logger(debug=False)
l.init(msg="Logger Pauwels demonstration")
l.log("Testing log system")
l.section("Progress bar", char=".", color=Colors.YELLOW)

steps = 200
duration = 5    # In seconds
for i in range(steps):
    l.progress_bar(i/steps, color=Colors.YELLOW)
    time.sleep(duration / steps)

l.cadre("Waiting time", color=Colors.BLUE)

for i in range(steps):
    l.waiting_time(i/duration)
    time.sleep(duration / steps)

l.cadre("Thanks for using me :D", color=Colors.RED)

l.end()
```
