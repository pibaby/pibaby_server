import keyboard
import time
from threading import Timer

stime = 0
etime = 0
long_press = 1.2 # long press in seconds
delay = 1.0 # timer length before counting buttons
is_timer = False
action = False
button_presses = 0

def toggle_white_noise():
    print("toggle white noise")

def log_wet_diaper():
    print("log wet diaper")

def log_poopy_diaper():
    print("log poopy diaper")

def delete_last_logging():
    global action
    action = False
    print("delete last logging")

def button_sequence():
    global button_presses
    global is_timer
    global action
    action = False
    is_timer = False
    if button_presses == 1:
        toggle_white_noise()
    elif button_presses == 2:
        log_wet_diaper()
    elif button_presses == 3:
        log_poopy_diaper()
    else:
        print(f"did not expect button_presses: {button_presses}")
    button_presses = 0

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
        if time.perf_counter() - stime  >  long_press and not action:
            action = True
            # play long press sound
            print("Long press sound")
    else:
        etime = time.perf_counter()
        seconds_pressed = etime - stime
        if seconds_pressed > long_press and button_presses == 0:
            delete_last_logging()
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
