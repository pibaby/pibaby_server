from pydub import AudioSegment
import logging
import simpleaudio

def intialize_noise(audio_file, volume_offset):
    global white_noise

    try:
        white_noise = AudioSegment.from_file(f"noise/{audio_file}")
        white_noise = white_noise.fade_in(2000).fade_out(3000)
        print(f"volume_offset: {volume_offset}")
        white_noise = white_noise + volume_offset
    except Exception as e:
        logging.error(f"Error on pydub processing, invaild audio file choice?: {e}")
    try:
        if white_noise_play is not None:
            stop_white_noise()
            play_white_noise()
    except:
        print("white noise is not playing")

def play_white_noise():
    global white_noise
    global white_noise_play
    try:
        white_noise_play = simpleaudio.play_buffer(
            white_noise.raw_data,
            num_channels=white_noise.channels,
            bytes_per_sample=white_noise.sample_width,
            sample_rate=white_noise.frame_rate
        )
    except Exception as e:
        logging.error(f"Error on audio playback: {e}")

def wait_for_done():
    global white_noise_play
    try:
        if white_noise_play is not None:
            white_noise_play.wait_done()
    except:
        print("wait_for_done white noise is not playing")


def stop_white_noise():
    global white_noise_play
    try:
        white_noise_play.stop()
        white_noise_play = None
    except Exception as e:
        logging.error(f"Error on audio stop: {e}")

