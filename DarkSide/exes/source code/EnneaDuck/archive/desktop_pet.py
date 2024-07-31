#from __future__ import print_function

import sys
sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules")
import pyautogui  # need pyautogui to show the label for dependecy reason, but for pyrevit might just import from site package
import random
import tkinter as tk

"""
should walk toward mouse location, but stop within 100 pixel distance.
"""

x = 500
cycle = 0
check = 1
idle_num =[1,2,3,4]
sleep_num = [10,11,12,13,15]
walk_left = [6,7]
walk_right = [8,9]
event_number = random.randrange(1,3,1)
import os
impath = "{}\img_assets\\".format(os.path.dirname(os.path.realpath(__file__)))




#transfer random no. to event
def event(cycle,check,event_number,x):
    global window
    global label

    common_wait = 50
    if event_number in idle_num:
        check = 0
        print('idle')
        print (cycle)
        window.after(common_wait,update,cycle,check,event_number,x) #no. 1,2,3,4 = idle
    elif event_number == 5:
        check = 1
        print('from idle to sleep')
        window.after(common_wait,update,cycle,check,event_number,x) #no. 5 = idle to sleep
    elif event_number in walk_left:
        check = 4
        print('walking towards left')
        window.after(common_wait,update,cycle,check,event_number,x)#no. 6,7 = walk towards left
    elif event_number in walk_right:
        check = 5
        print('walking towards right')
        window.after(common_wait,update,cycle,check,event_number,x)#no 8,9 = walk towards right
    elif event_number in sleep_num:
        check  = 2
        print('sleep')
        print (cycle)
        window.after(common_wait,update,cycle,check,event_number,x)#no. 10,11,12,13,15 = sleep
    elif event_number == 14:
        check = 3
        print('from sleep to idle')
        window.after(common_wait,update,cycle,check,event_number,x)#no. 15 = sleep to idle



#making gif work
def gif_work(cycle,frames,event_number,first_num,last_num):
    if cycle < len(frames) -1:
        cycle+=1
    else:
        cycle = 0
        event_number = random.randrange(first_num,last_num+1,1)
    return cycle,event_number


def update(cycle,check,event_number,x):
    global window
    global label
    global idle_num
    global sleep_num
    global walk_left
    global walk_right

    global idle
    global idle_to_sleep
    global sleep
    global sleep_to_idle
    global walk_positive
    global walk_negative
    #idle
    if check ==0:
        frame = idle[cycle]
        cycle ,event_number = gif_work(cycle,idle,event_number,1,9)

    #idle to sleep
    elif check ==1:
        frame = idle_to_sleep[cycle]
        cycle ,event_number = gif_work(cycle,idle_to_sleep,event_number,10,10)
    #sleep
    elif check == 2:
        frame = sleep[cycle]
        cycle ,event_number = gif_work(cycle,sleep,event_number,10,15)
    #sleep to idle
    elif check ==3:
        frame = sleep_to_idle[cycle]
        cycle ,event_number = gif_work(cycle,sleep_to_idle,event_number,1,1)
    #walk toward left
    elif check == 4:
        frame = walk_positive[cycle]
        cycle , event_number = gif_work(cycle,walk_positive,event_number,1,9)
        x -= 3
    #walk towards right
    elif check == 5:
        frame = walk_negative[cycle]
        cycle , event_number = gif_work(cycle,walk_negative,event_number,1,9)
        x -= -3


    window.geometry('100x100+'+str(x)+'+1050')
    label.configure(image=frame)
    window.after(1,event,cycle,check,event_number,x)
    #print (cycle)
    #print (frame)



##########################
lastClickX = 0
lastClickY = 0


def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + window.winfo_x(), event.y - lastClickY + window.winfo_y()
    window.geometry("+%s+%s" % (x , y))
    # after refactor this to a class, can update all x, y with memeory position.
##########################

def main():
    global window
    global label
    global idle
    global idle_to_sleep
    global sleep
    global sleep_to_idle
    global walk_positive
    global walk_negative



    window = tk.Tk()
    window.geometry("100x100+300+300")
    #call buddy's action gif
    idle = [tk.PhotoImage(file=impath+'idle.gif',format = 'gif -index %i' %(i)) for i in range(6)]#idle gif
    idle_to_sleep = [tk.PhotoImage(file=impath+'idle_to_sleep.gif',format = 'gif -index %i' %(i)) for i in range(57)]#idle to sleep gif
    sleep = [tk.PhotoImage(file=impath+'sleep.gif',format = 'gif -index %i' %(i)) for i in range(21)]#sleep gif
    sleep_to_idle = [tk.PhotoImage(file=impath+'sleep_to_idle.gif',format = 'gif -index %i' %(i)) for i in range(12)]#sleep to idle gif
    walk_positive = [tk.PhotoImage(file=impath+'walking_positive.gif',format = 'gif -index %i' %(i)) for i in range(9)]#walk to left gif
    walk_negative = [tk.PhotoImage(file=impath+'walking_negative.gif',format = 'gif -index %i' %(i)) for i in range(9)]#walk to right gif
    #window configuration
    window.config(highlightbackground='green')

    label = tk.Label(window,bd=0,bg='green')
    talk_bubble = tk.Label(window,text = "123")

    label.pack()
    window.overrideredirect(True)
    window.wm_attributes('-transparentcolor','green')
    window.wm_attributes('-topmost',True)


    ###############
    window.bind('<Button-1>', SaveLastClickPos)
    window.bind('<B1-Motion>', Dragging)
    ##################

    """https://www.geeksforgeeks.org/right-click-menu-using-tkinter/
    see above helper doc for making a right click menu pop."""

    def hey(s):
        talk_bubble.configure(text = s)
        window.after(2000)


    m = tk.Menu(window, tearoff = 0)
    m.add_command(label ="Hello.", command = lambda:hey("hi"))
    m.add_separator()
    m.add_command(label ="Kill Me.", command = lambda:window.destroy())
    #for kill me, add a atomic bomb explosion gif.

    """see https://stackoverflow.com/questions/110923/how-do-i-close-a-tkinter-window about quiting"""


    def do_popup(event):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    label.bind("<Button-3>", do_popup)

    #loop the program
    window.after(1,update,cycle,check,event_number,x)
    window.mainloop()


if __name__ == "__main__":
    main()
"""
We need gif of duck animation for the EnneaDuck desktop pet.

Need to have at least several gif for different status:

idle
walking left
walking right
runing left
running right
honking with opening wings
sleeping
pooping
etc

then hats, boots, jackets...
    """
