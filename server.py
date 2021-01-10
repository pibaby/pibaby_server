import keyboard
import time
from threading import Timer

stime = 0
etime = 0
long_press = 2.0
delay = 1.0
action = False
timer = 0
is_timer = False
long_press
button_presses = 0

def button_sequence():
    global button_presses
    global is_timer
    print(f"Press Sequence Action {button_presses} " + "="*40)
    button_presses = 0
    is_timer = False

def print_pressed_keys(e):
    global stime
    global etime
    global action
    global is_timer
    global button_presses
    global delay

    if e.event_type == "down":
        if stime == 0:
            stime = time.perf_counter()
            print(f"stime: {stime}")
        # print(f"{time.perf_counter() - stime}")
        if time.perf_counter() - stime  >  long_press and not action:
            print("Long Press Sound")
            action = True
    else:
        etime = time.perf_counter()
        seconds_pressed = etime - stime
        print(f"etime: {etime}")
        print(f"Your time: {etime - stime} seconds")
        if seconds_pressed > long_press and button_presses == 0:
            print("Long Press Action " + "="*40)
        else:
            if button_presses < 3:
                button_presses+=1
            if not is_timer:
                is_timer = True
                r = Timer(delay, button_sequence)
                r.start()

        stime = 0


def main():
    # If using keyboard instead of gpio
    keyboard.hook(print_pressed_keys)
    keyboard.wait()


if __name__ == "__main__":
    main()
