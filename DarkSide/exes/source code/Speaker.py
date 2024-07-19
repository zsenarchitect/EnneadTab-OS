import os
import time
import _Exe_Util
import contextlib
import io

TTS_FILE = "EA_Text2Speech.sexyDuck"

def text_to_speech_with_gTTS(text, lang='en', tld='com'):
    from gtts import gTTS
    import pygame

    try:
        tts = gTTS(text=text, lang=lang, tld=tld)
        filename = _Exe_Util.get_file_in_dump_folder('tts_audio_{}.mp3'.format(time.time()))
        tts.save(filename)
        
        # Suppress Pygame initialization message
        with contextlib.redirect_stdout(io.StringIO()):
            pygame.mixer.init()

        # Load and play the sound file
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait until the sound has finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Unload the mixer to release the file
        pygame.mixer.music.unload()

        # Add a small delay to ensure pygame releases the file
        time.sleep(1)

        # Remove the file after playing
        os.remove(filename)
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup_tts_mp3()

def cleanup_tts_mp3():
    dump_folder = _Exe_Util.get_dump_folder()
    current_time = time.time()
    two_minutes_ago = current_time - 2 * 60  # 2 minutes in seconds

    for file in os.listdir(dump_folder):
        if not file.startswith("tts_audio"):
            continue

        file_path = os.path.join(dump_folder, file)
        if not os.path.isfile(file_path):
            continue

        file_mod_time = os.path.getmtime(file_path)
        if file_mod_time >= two_minutes_ago:
            continue

        try:
            os.remove(file_path)
            print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

@_Exe_Util.try_catch_error
def tts():
    data = _Exe_Util.read_json_as_dict_in_dump_folder(TTS_FILE)
    if not data:
        print("No data")
        return
    print(data)
    text = data.get("text")
    lang = data.get("language")
    accent = data.get("accent")

    text_to_speech_with_gTTS(text, lang=lang, tld=accent)

if __name__ == "__main__":
    tts()


    print("\n\nEnd")
