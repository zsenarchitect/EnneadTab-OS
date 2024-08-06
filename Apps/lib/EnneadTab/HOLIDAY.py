# https://python-holidays.readthedocs.io/en/latest/index.html

"""used to make customized greeting for all the employee in the office """



import datetime



try:
    from pyrevit import script
except:
    pass

import os
import sys
import random


import FOLDER
import EXE
import SOUND
import ENVIRONMENT
import NOTIFICATION

def festival_greeting():
    greeting_chinese_new_year()
    greeting_mid_moon()
    greeting_xmas()
    greeting_pi()
    greeting_april_fools()
    greeting_may_force()
    

def is_valid_date(date_tuple_start,
                  date_tuple_end):
    d0 = datetime.datetime(date_tuple_start[0], 
                           date_tuple_start[1],
                           date_tuple_start[2])
    today = datetime.datetime.now()
    d1 = datetime.datetime(date_tuple_end[0], 
                           date_tuple_end[1],
                           date_tuple_end[2])

    return (d0 <= today <= d1)

def greeting_april_fools():

    if not is_valid_date((2024,3,31),(2024,4,1)):
        return

    import JOKE
    for _ in range(random.randint(1, 5)):
        JOKE.prank_dvd()

    NOTIFICATION.messenger(JOKE.random_loading_message())


def greeting_may_force():

    if not is_valid_date((2024,5,1),(2024,5,6)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    
    image = "may_force.jpg"

    image_file = "{}\\{}".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT,
                                 image)
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    return 
    file = 'sound effect_xmas_hohoho.wav'
    SOUND.play_sound(file)
    
def greeting_pi():

    if not is_valid_date((2024,3,13),(2024,3,15)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    
    image = "pi_day.jpeg"

    image_file = "{}\\{}".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT,
                                 image)
    output = script.get_output()
    output.print_image(image_file)
    output.print_md("#Happy Pi Day: 3.14")
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    return 
    file = 'sound effect_xmas_hohoho.wav'
    SOUND.play_sound(file)
  
def greeting_xmas():

    if not is_valid_date((2023,12,20),(2024,1,3)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    
    image = "xmax_tree_drawing.png"

    image_file = "{}\\{}".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT,
                                 image)
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")


    file = 'sound_effect_xmas_hohoho.wav'
    SOUND.play_sound(file)
    
     
def greeting_chinese_new_year():

    
    if not is_valid_date((2024,1,26),(2024,2,15)):
        return
    image = "YEAR OF BUNNY.png"
    files = os.listdir(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)
    random.shuffle(files)
    for file in files:
        if file.endswith(".png") and "YEAR OF DRAGON" in file:
            image = file
            break


    image_file = "{}\{}".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT,
                                image)
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    file = 'sound effect_chinese_new_year.wav'
    SOUND.play_sound(file)

    
def greeting_mid_moon():

    d0 = datetime.datetime(2023, 9,28)
    today = datetime.datetime.now()
    d1 = datetime.datetime(2023,10,10)

    if not(d0 < today < d1):
        return

    image = "mid moon.jpg"
    image_file = __file__.split("ENNEAD.extension")[0] + "ENNEAD.extension\\bin\{}".format(image)
    
    
    image = "moon-cake-drawing.png"
    moon_cake_image_file = __file__.split("ENNEAD.extension")[0] + "ENNEAD.extension\\bin\{}".format(image)
    
    #print image_file
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(1200)
    output.set_height(900)
    output.self_destruct(100)
    output.center()
    output.set_title("Greeting from EnneadTab")
    output.print_md("# Happy Mid-Autumn Festival, everybody!")
    output.print_md("## Also known as the Moon-Festival, it is a family reunion holiday shared in many east asian culture.")
    output.print_md("## An important part is the moon-cake. You may find the technical drawing below.")
    output.print_image(moon_cake_image_file)

    file = 'sound effect_chinese_new_year.wav'
    SOUND.play_sound(file)
    
    
    
    if random.random() > 0.2:
        return
    dest_file = FOLDER.get_EA_dump_folder_file("Moon Festival.html")
    output.save_contents(dest_file)
    output.close()
    os.startfile(dest_file)



if __name__ == '__main__':
    festival_greeting()