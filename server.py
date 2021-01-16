import keyboard
import time
from threading import Timer
import threading
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import sqlite3
db_connection = sqlite3.connect("baby.db")
s = db_connection.cursor()

sound_boop = AudioSegment.from_file('resources/boop.wav')
delete_beep = AudioSegment.from_file('resources/delete.wav')
white_noise = AudioSegment.from_file('resources/nature.wav')
white_noise = white_noise.fade_in(2000).fade_out(3000)

stime = 0
etime = 0
long_press = 1.2 # long press in seconds
delay = 1.0 # timer length before counting buttons
is_timer = False
action = False
is_sleeping = False
button_presses = 0
white_noise_play = None

def toggle_white_noise():
    global is_sleeping
    global white_noise_play
    is_sleeping = not is_sleeping
    print(f"toggle white noise play white noise: {is_sleeping}")
    play(sound_boop)
    if is_sleeping:
        while is_sleeping:
            white_noise_play = simpleaudio.play_buffer(
                white_noise.raw_data,
                num_channels=white_noise.channels,
                bytes_per_sample=white_noise.sample_width,
                sample_rate=white_noise.frame_rate
            )
            white_noise_play.wait_done()
    else:
        white_noise_play.stop()
        # s.execute(f"INSERT INTO sleep VALUES ('Sammy', 'shark')")

    # rows = s.execute("SELECT timestamp, duration FROM sleep").fetchall()
    # print(rows)


def log_wet_diaper():
    print("log wet diaper")
    play(sound_boop)
    play(sound_boop)

def log_poopy_diaper():
    print("log poopy diaper")
    play(sound_boop)
    play(sound_boop)
    play(sound_boop)

def delete_last_logging():
    global action
    action = False
    print("delete last logging")
    play(delete_beep)

def button_sequence():
    global button_presses
    global is_timer
    global action
    action = False
    is_timer = False
    if button_presses == 1:
        x = threading.Thread(target=toggle_white_noise)
        x.start()
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

    s.execute("CREATE TABLE sleep (timestamp TEXT, duration INTEGER)")



if __name__ == "__main__":
    main()
