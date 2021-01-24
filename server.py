import keyboard
import time
import datetime
from threading import Timer
import threading
from pydub import AudioSegment
from pydub.playback import play
import logging
import sqlite3
import wsockets as ws
from config import conf, read_config
import noise
logging.basicConfig(level=logging.INFO)

sound_boop = AudioSegment.from_file('resources/boop.wav')
delete_beep = AudioSegment.from_file('resources/delete.wav')

# State Variables
stime = 0
etime = 0
is_timer = False
action = False
is_sleeping = False
button_presses = 0
white_noise_play = None
sleep_start = 0
sleep_end = 0
sleep_start_timestamp = None
last_table = None

def toggle_white_noise():
    global is_sleeping
    global white_noise_play
    global sleep_start
    global sleep_end
    global sleep_start_timestamp
    global last_table
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    is_sleeping = not is_sleeping
    logging.info(f"toggle white noise play white noise: {is_sleeping}")
    play(sound_boop)
    if is_sleeping:
        sleep_start = time.perf_counter()
        sleep_start_timestamp = datetime.datetime.now().isoformat()
        while is_sleeping:
            noise.play_white_noise()
            noise.wait_for_done()
    else:
        sleep_end = time.perf_counter()
        duration = sleep_end - sleep_start
        sleep_end_timestamp = datetime.datetime.now().isoformat()
        noise.stop_white_noise()
        logging.info(f"""{duration} > {conf["sleep_track_limit"] * 60}: {duration > conf["sleep_track_limit"] * 60 }""")
        if duration > conf["sleep_track_limit"] * 60:
            s.execute(f"""INSERT INTO sleep (start_timestamp,end_timestamp)
                      VALUES ('{sleep_start_timestamp}','{sleep_end_timestamp}')""")
            db.commit()
            last_table = "sleep"
            rows = s.execute("SELECT * FROM sleep").fetchall()
            logging.info(rows)


def log_wet_diaper():
    global last_table
    logging.info("log wet diaper")
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    play(sound_boop)
    play(sound_boop)
    wet_timestamp =datetime.datetime.now().isoformat()
    s.execute(f"""INSERT INTO wet_diaper (timestamp)
                VALUES ('{wet_timestamp}')""")
    db.commit()
    last_table = "wet_diaper"
    rows = s.execute("SELECT * FROM wet_diaper").fetchall()
    logging.info(rows)


def log_poopy_diaper():
    global last_table
    logging.info("log poopy diaper")
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    poops_timestamp = datetime.datetime.now().isoformat()
    play(sound_boop)
    play(sound_boop)
    play(sound_boop)
    s.execute(f"""INSERT INTO poops (timestamp)
                VALUES ('{poops_timestamp}')""")
    db.commit()
    last_table = "poops"
    rows = s.execute("SELECT * FROM poops").fetchall()
    logging.info(rows)


def delete_last_logging():
    global action
    global last_table
    action = False
    logging.info(last_table)
    if last_table is not None:
        play(delete_beep) # TODO make this sound like a confirmation sound
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        logging.info("delete last logging")
        s.execute(f"DELETE FROM {last_table} WHERE id = (SELECT MAX(id) FROM {last_table});")
        db.commit()
        rows = s.execute(f"SELECT * FROM {last_table}").fetchall()
        logging.info(f"{last_table} : {rows}")
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
        logging.warn(f"did not expect button_presses: {button_presses}")
    button_presses = 0


def create_tables():
    tables = {
     "sleep":"start_timestamp TEXT, end_timestamp TEXT, title TEXT, color TEXT",
     "poops":"timestamp TEXT, title TEXT, color TEXT",
     "wet_diaper":"timestamp TEXT, title TEXT, color TEXT"
    }
    db = sqlite3.connect("baby.db")
    s = db.cursor()

    for key, value in tables.items():
        s.execute(f""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{key}' """)
        if s.fetchone()[0]==1 :
            logging.info(f"Table already exists. using table: {key}")
        else :
            logging.info(f"Creating table: {key}")
            s.execute(f"CREATE TABLE {key} (id integer primary key autoincrement, {value})")


def print_pressed_keys(e):
    global stime
    global etime
    global action
    global is_timer
    global button_presses

    if e.event_type == "down":
        if stime == 0:
            stime = time.perf_counter()
        if time.perf_counter() - stime  >  conf["long_press"] and not action:
            action = True
            # play long press sound
            logging.info("Long press sound")
            play(delete_beep)
    else:
        etime = time.perf_counter()
        seconds_pressed = etime - stime
        if seconds_pressed > conf["long_press"] and button_presses == 0:
            delete_last_logging()
        else:
            if button_presses < 3:
                button_presses+=1
            if not is_timer:
                is_timer = True
                r = Timer(conf["delay"], button_sequence)
                r.start()
        stime = 0


def main():
    noise.intialize_noise(conf['selected_noise'], conf['volume_offset'])
    create_tables()
    read_config()
    # keyboard.hook(print_pressed_keys)
    keyboard.hook_key("8", print_pressed_keys)
    ws.run()


if __name__ == "__main__":
    main()
