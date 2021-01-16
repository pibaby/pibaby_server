import keyboard
import time
from threading import Timer
import threading
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import sqlite3

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
sleep_start = 0
sleep_end = 0
sleep_timestamp = None
sleep_track_limit = 60 #seconds
last_table = None

def toggle_white_noise():
    global is_sleeping
    global white_noise_play
    global sleep_start
    global sleep_end
    global sleep_timestamp
    global last_table
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    is_sleeping = not is_sleeping
    print(f"toggle white noise play white noise: {is_sleeping}")
    play(sound_boop)
    if is_sleeping:
        sleep_start = time.perf_counter()
        sleep_timestamp = time.asctime( time.gmtime(time.time()) )
        while is_sleeping:
            white_noise_play = simpleaudio.play_buffer(
                white_noise.raw_data,
                num_channels=white_noise.channels,
                bytes_per_sample=white_noise.sample_width,
                sample_rate=white_noise.frame_rate
            )
            white_noise_play.wait_done()
    else:
        sleep_end = time.perf_counter()
        duration = sleep_end - sleep_start
        white_noise_play.stop()
        if duration > sleep_track_limit:
            s.execute(f"""INSERT INTO sleep (timestamp, duration)
                      VALUES ('{sleep_timestamp}', {duration})""")
            db.commit()
            last_table = "sleep"
            rows = s.execute("SELECT * FROM sleep").fetchall()
            print(rows)


def log_wet_diaper():
    global last_table
    print("log wet diaper")
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    play(sound_boop)
    play(sound_boop)
    wet_timestamp = time.asctime( time.gmtime(time.time()) )
    s.execute(f"""INSERT INTO wet_diaper (timestamp)
                VALUES ('{wet_timestamp}')""")
    db.commit()
    last_table = "wet_diaper"
    rows = s.execute("SELECT * FROM wet_diaper").fetchall()
    print(rows)


def log_poopy_diaper():
    global last_table
    print("log poopy diaper")
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    poops_timestamp = time.asctime( time.gmtime(time.time()) )
    play(sound_boop)
    play(sound_boop)
    play(sound_boop)
    s.execute(f"""INSERT INTO poops (timestamp)
                VALUES ('{poops_timestamp}')""")
    db.commit()
    last_table = "poops"
    rows = s.execute("SELECT * FROM poops").fetchall()
    print(rows)


def delete_last_logging():
    global action
    global last_table
    action = False
    print(last_table)
    if last_table is not None:
        play(delete_beep) # TODO make this sound like a confirmation sound
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        print("delete last logging")
        s.execute(f"DELETE FROM {last_table} WHERE id = (SELECT MAX(id) FROM {last_table});")
        db.commit()
        rows = s.execute(f"SELECT * FROM {last_table}").fetchall()
        print(f"{last_table} : {rows}")
        last_table = None


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


def create_tables():
    tables = {
     "sleep":"timestamp TEXT, duration INTEGER",
     "poops":"timestamp TEXT",
     "wet_diaper":"timestamp TEXT"
    }
    db = sqlite3.connect("baby.db")
    s = db.cursor()

    for key, value in tables.items():
        s.execute(f""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{key}' """)
        if s.fetchone()[0]==1 :
            print(f"Table already exists. using table: {key}")
        else :
            print(f"Creating table: {key}")
            s.execute(f"CREATE TABLE {key} (id integer primary key autoincrement, {value})")


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
            play(delete_beep)
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
    create_tables()
    keyboard.hook(print_pressed_keys)
    keyboard.wait()


if __name__ == "__main__":
    main()
