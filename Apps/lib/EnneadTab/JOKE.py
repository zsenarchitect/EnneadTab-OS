
import os
import sys
import random



root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)


import FOLDER
import NOTIFICATION
import SPEAK
import ENVIRONMENT
import USER
import FUN
import EXE
import TIME
import SOUND

    
TARGETS = ['fsun', 
           'eshaw']

def random_joke():

    joke_file = "{}\\FUN\\_dad_jokes.txt".format(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO)
    with open(joke_file, "r") as f:
        lines = f.readlines()


    random.shuffle(lines)
    return lines[0].replace("\n", "")

def random_loading_message():
    """get some fun message for loading screen

    Returns:
        str: a random line of funny message
    """

    with open('{}\_loading_screen_message.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    return lines[0].replace("\n", "")


def prank_ph():

    
    icon = '{}\prank\pornhub.png'.format(FOLDER.get_folder_path_from_path(__file__))
   
    NOTIFICATION.toast(sub_text="Please login again at www.pornhub.com",
                        main_text="{} videos failed to download.".format(random.randint(2,6)),
                        app_name="Chrome",
                        icon=icon,
                        force_toast=True)
    
def prank_meme():

    link = "https://www.instagram.com/reel/C0KA4-kxioj/?igsh=MWN6cmg4cW5qeXV5NA%3D%3D"
    import webbrowser
    webbrowser.open(link)


def prank_dvd():

    EXE.open_exe("BOUNCER")
    
    

     
def give_me_a_joke(talk = False, max_len = None):


    joke =  random_joke()
    if not max_len:
        import textwrap as TW
        wrapper = TW.TextWrapper(width = 70)
        temp = ""
        for line in wrapper.wrap(joke):
            temp += line + "\n"
        joke = temp


    if talk:
        SPEAK.speak(joke.replace("\n", " "))
    return joke.replace("\n", " ")


def validating_jokes():
    with open("_dad_jokes.txt", "r") as f:
    #import io
    #with io.open("dad_jokes.txt", encoding = "utf8") as f:
        lines = f.readlines()


    OUT = []
    for line in lines:
        #print "\n#######################"
        #print line
        if r"â€™" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r"â€™", r"\'")
        if r"â??" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r"â??", r"\"")
        if r".â" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r".â", r"\"")
        if line.endswith("?"):
            print ("find a questiong ending:" + "*" * 100)
            print (line)
        OUT.append(line)

    with open("dad_jokes.txt", "w") as f:
        f.writelines(OUT)


if USER_CONSTANTS.USER_NAME in TARGETS:
    chance = 0.02
else:
    chance = 0.0001
if random.random() < chance:
    prank_ph()


if USER_CONSTANTS.USER_NAME in TARGETS:
    chance = 0.02
else:
    chance = 0.0001
if random.random() < chance:
    prank_meme()



if USER_CONSTANTS.USER_NAME in TARGETS:
    chance = 0.05
else:
    chance = 0.0001
if random.random() < chance:
    prank_dvd()


if USER_CONSTANTS.USER_NAME in TARGETS:
    chance = 0.01
else:
    chance = 0.0001
if random.random() < chance:
    FUN.EnneaDuck.quack()


def april_fool():
    return

    y, m, d = TIME.get_date_as_tuple(return_string=False)

    marker_file = FOLDER.get_EA_dump_folder_file("2024_april_fooled3.stupid")
    
    if m == 4 and d in [1, 2] and random.random() < 0.2 :


        if os.path.exists(marker_file):
            return
        dice = random.random()
        if dice < 0.2:
            prank_ph()
        # elif dice < 0.45:
        #     NOTIFICATION.duck_pop(random_joke())
        # elif dice < 0.48:
        #     NOTIFICATION.messenger(random_loading_message())
        elif dice < 0.95:
            max = 10 if USER_CONSTANTS.USER_NAME in TARGETS else 5
            for _ in range(random.randint(3, max)):
                prank_dvd()

        else:
            SOUNDS.play_meme_sound()
        with open(marker_file, 'w') as f:
            f.write("You have been pranked.")


        # FUN.EnneaDuck.quack()

        

april_fool()

if __name__ == "__main__":

    prank_dvd()

