import eyed3


def is_correct(path_to_audio_file):
    try:
        audio = eyed3.load(path_to_audio_file)
        return True
    except Exception:
        return False


def get_duration(path):
    try:
        audio = eyed3.load(path)
        return audio.info.time_secs
    except:
        pass
