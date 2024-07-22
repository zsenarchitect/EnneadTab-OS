
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import threading
import time
import random
import ENVIRONMENT
import TEXT

def get_audio_path_by_name(file_name):
    if not file_name.endswith(".wav"):
        file_name = file_name + ".wav"
    if os.path.exists(file_name):
        return file_name
    if os.path.exists("{}\\{}".format(ENVIRONMENT.AUDIO_FOLDER, file_name)):
        return "{}\\{}".format(ENVIRONMENT.AUDIO_FOLDER, file_name)
    print ("A ha! {}\\{} is not valid or accessibile. Better luck next time.".format(ENVIRONMENT.AUDIO_FOLDER, file_name))
    return False

def get_one_audio_path_by_prefix(prefix):
    files = [os.path.join(ENVIRONMENT.AUDIO_FOLDER, f) for f in os.listdir(ENVIRONMENT.AUDIO_FOLDER) if f.startswith(prefix)]
    file = random.choice(files)
    return file

    
def play_sound(file = "sound_effect_popup_msg3"):
    file = get_audio_path_by_name(file)
    if not file:
        return

    try:
        from System.Media import SoundPlayer # pyright: ignore
        sp = SoundPlayer()
        sp.SoundLocation = file
        sp.Play()
        return True
    except Exception as e:
        # print ("Cannot use system media becasue: " + str(e))
        pass

    try:
        import playsound # pyright : ignore
        playsound.playsound(file)
        return True
    except Exception as e:
        # print ("Cannot use native playsound  becasue: " + str(e))
        pass
    try:
        # Assuming you're using os.system to play sounds
        os.system('powershell -c (New-Object Media.SoundPlayer "{}").PlaySync();'.format(file))
        return True
    except Exception as e:
        # print(f"An error occurred: {e}")
        pass
        
    try:
        import sys
        sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
        import playsound # pyright : ignore
        playsound.playsound(file)
        return True
    except Exception as e:
        # print ("cannot use playsound module becasue: " + str(e))
        pass

    return False


def test_play_all_sounds():
    for file in os.listdir(ENVIRONMENT.AUDIO_FOLDER):
        print (file)
        
        if not play_sound(file):
            print (TEXT.colored_text("{} cannot be played in system".format(file)))
            


def play_meme_sound():
    file = get_one_audio_path_by_prefix("meme")
    play_sound(file)

def unit_test():
    print ("Playing stupid sounds effect")

    file = get_one_audio_path_by_prefix("meme")
    player = Player()
    player.start(file)
    for _ in range(10):
        print (_)
    player.stop()
    
class Player:
    """
    the music file start to play, and a FlagListener will start running, when 
    detecting a stop flag snet by any program, it stops.

    Can be usewd to play 'elevator music' continously but not 
    infiniately during long process
    such as doc syncing dyc opening

    I think this Listerner will use threading to keep it running 
    without blocking main program

    player = Player(file)
    player.start()
    # do other stuff
    player.stop()

    
    """

    def play(self):
        while not self.stop_flag.is_set():
            print("Playing elevator music...")
            play_sound(self.file)

            
    def start(self, file):
        self.file = file


        # Create a flag to control the music playback
        self.stop_flag = threading.Event()

        # Create a thread to play music
        self.music_thread = threading.Thread(target=self.play)

        # Start the music thread
        self.music_thread.start()

    def stop(self):

        # Set the stop flag to terminate the music thread
        self.stop_flag.set()

        # Wait for the music thread to finish
        self.music_thread.join()

        print("Music stopped.")
        pass


def sys_alert():
    #play window alert sound
    import winsound
    duration = 100  # milliseconds
    freqs = [440,
            500,
            600,
            900]# Hz
    for i,f in enumerate(freqs):
        if i == len(freqs)-1:
            duration = 400
        winsound.Beep(f, duration)
#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    # unit_test() 
    file = "sound_effect_spring"
    # play_sound(file)
    # play_sound()
    test_play_all_sounds()
    # sys_alert()



    
    