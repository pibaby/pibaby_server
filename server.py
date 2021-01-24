import keyboard
import time
import datetime
import asyncio
from threading import Timer
import threading
from pydub import AudioSegment
from pydub.playback import play
import logging
import sqlite3
import wsockets as ws
import state
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
button_presses = 0

def update_web():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        loop.create_task(ws.init())
    else:
        asyncio.run(ws.init())

def toggle_white_noise():
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    play(sound_boop)
    if not state.is_sleeping:
        state.sleep_start = time.perf_counter()
        state.sleep_start_timestamp = datetime.datetime.now().isoformat()
        x = threading.Thread(target=noise.play_white_noise)
        x.start()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # if cleanup: 'RuntimeError: There is no current event loop..'
            loop = None
        if loop and loop.is_running():
            loop.create_task(ws.toggle_is_playing(True))
        else:
            asyncio.run(ws.toggle_is_playing(True))

    else:
        state.sleep_end = time.perf_counter()
        duration = state.sleep_end - state.sleep_start
        sleep_end_timestamp = datetime.datetime.now().isoformat()
        noise.stop_white_noise()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # if cleanup: 'RuntimeError: There is no current event loop..'
            loop = None
        if loop and loop.is_running():
            loop.create_task(ws.toggle_is_playing(False))
        else:
            asyncio.run(ws.toggle_is_playing(False))

        logging.info(f"""{duration} > {conf["sleep_track_limit"] * 60}: {duration > conf["sleep_track_limit"] * 60 }""")
        if duration > conf["sleep_track_limit"] * 60:
            s.execute(f"""INSERT INTO sleep (start_timestamp,end_timestamp)
                      VALUES ('{state.sleep_start_timestamp}','{sleep_end_timestamp}')""")
            db.commit()
            state.last_table = "sleep"
            rows = s.execute("SELECT * FROM sleep").fetchall()
            logging.debug(rows)
        update_web()


def log_wet_diaper():
    logging.info("log wet diaper")
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    play(sound_boop)
    play(sound_boop)
    wet_timestamp =datetime.datetime.now().isoformat()
    s.execute(f"""INSERT INTO wet_diaper (timestamp)
                VALUES ('{wet_timestamp}')""")
    db.commit()
    state.last_table = "wet_diaper"
    rows = s.execute("SELECT * FROM wet_diaper").fetchall()
    logging.debug(rows)
    update_web()


def log_poopy_diaper():
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
    state.last_table = "poops"
    rows = s.execute("SELECT * FROM poops").fetchall()
    logging.debug(rows)
    update_web()


def delete_last_logging():
    global action
    action = False
    logging.info(state.last_table)
    if state.last_table is not None:
        play(delete_beep) # TODO make this sound like a confirmation sound
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        logging.info("delete last logging")
        s.execute(f"DELETE FROM {state.last_table} WHERE id = (SELECT MAX(id) FROM {state.last_table});")
        db.commit()
        rows = s.execute(f"SELECT * FROM {state.last_table}").fetchall()
        logging.debug(f"{state.last_table} : {rows}")
        state.last_table = None
        update_web()


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
