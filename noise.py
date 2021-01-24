from pydub import AudioSegment
import logging
import threading
import simpleaudio
import state
import time
import json
import wsockets

def intialize_noise(audio_file, volume_offset):
    global white_noise

    try:
        state.white_noise = AudioSegment.from_file(f"noise/{audio_file}")
        state.white_noise = state.white_noise.fade_in(2000).fade_out(3000)
        print(f"volume_offset: {volume_offset}")
        state.white_noise = state.white_noise + volume_offset
    except Exception as e:
        logging.error(f"Error on pydub processing, invaild audio file choice?: {e}")
    try:
        if state.white_noise_play is not None:
            stop_white_noise()
            while state.white_noise_play is not None:
                time.sleep(1)
            x = threading.Thread(target=play_white_noise)
            x.start()
    except:
        print("white noise is not playing")

def play_white_noise():
    print("play_white_noise")
    state.is_sleeping = True
    while state.is_sleeping:

        try:
            if state.white_noise_play is not None:
                print("white noise is already playing")
                time.sleep(1)
            else:
                try:
                    print("~~ white noise loop ~~")
                    state.white_noise_play = simpleaudio.play_buffer(
                        state.white_noise.raw_data,
                        num_channels=state.white_noise.channels,
                        bytes_per_sample=state.white_noise.sample_width,
                        sample_rate=state.white_noise.frame_rate
                    )
                    state.white_noise_play.wait_done()
                    state.white_noise_play = None
                except Exception as e:
                    logging.error(f"Error on audio playback: {e}")
        except:
            try:
                print("starting white noise")
                state.white_noise_play = simpleaudio.play_buffer(
                    state.white_noise.raw_data,
                    num_channels=state.white_noise.channels,
                    bytes_per_sample=state.white_noise.sample_width,
                    sample_rate=state.white_noise.frame_rate
                )
                state.white_noise_play.wait_done()
                state.white_noise_play = None
            except Exception as e:
                logging.error(f"Error on audio playback: {e}")

def stop_white_noise():
    state.is_sleeping = False
    try:
        state.white_noise_play.stop()
    except Exception as e:
        logging.error(f"Error on audio stop: {e}")

