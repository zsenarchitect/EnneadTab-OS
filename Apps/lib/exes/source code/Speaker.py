import os

import _Exe_Util

TTS_FILE = "EA_Text2Speech.json"


def text_to_speech_with_gTTS(text, lang='en', tld='com'):
    from gtts import gTTS
    from playsound import playsound
    tts = gTTS(text=text, lang=lang, tld=tld)
    filename = _Exe_Util.get_file_in_dump_folder('tts_audio.mp3')
    tts.save(filename)
    playsound(filename)
    os.remove(filename)


def tts():
    data = _Exe_Util.read_json_as_dict_in_dump_folder(TTS_FILE)
    if not data:
        print ("no data")
        return
    # Example usage with different accents
    print (data)
    text = data.get("text")
    lang = data.get("language")
    accent = data.get("accent")

    text_to_speech_with_gTTS(text, lang=lang, tld=accent)


if __name__ == "__main__":
    tts()