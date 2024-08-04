import os
import random
import tkinter as tk

class AnimatedCharacter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.impath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img_assets")

        self.idle = [tk.PhotoImage(file=os.path.join(self.impath, 'idle.gif'), format='gif -index %i' % i) for i in range(6)]
        self.idle_to_sleep = [tk.PhotoImage(file=os.path.join(self.impath, 'idle_to_sleep.gif'), format='gif -index %i' % i) for i in range(57)]
        self.sleep = [tk.PhotoImage(file=os.path.join(self.impath, 'sleep.gif'), format='gif -index %i' % i) for i in range(21)]
        self.sleep_to_idle = [tk.PhotoImage(file=os.path.join(self.impath, 'sleep_to_idle.gif'), format='gif -index %i' % i) for i in range(12)]
        self.walk_positive = [tk.PhotoImage(file=os.path.join(self.impath, 'walking_positive.gif'), format='gif -index %i' % i) for i in range(9)]
        self.walk_negative = [tk.PhotoImage(file=os.path.join(self.impath, 'walking_negative.gif'), format='gif -index %i' % i) for i in range(9)]

        self.label = tk.Label(self, bd=0, bg='black')
        self.label.pack()

        self.overrideredirect(True)
        self.wm_attributes('-topmost', True)

        self.bind('<Button-1>', self.save_last_click_pos)
        self.bind('<B1-Motion>', self.dragging)

        self.cycle = 0
        self.check = 1
        self.event_number = random.randrange(1, 3, 1)
        self.x = 1400

        self.update_animation()
        print ("initiation done")

    def save_last_click_pos(self, event):
        self.last_click_x = event.x
        self.last_click_y = event.y

    def dragging(self, event):
        x, y = event.x - self.last_click_x + self.winfo_x(), event.y - self.last_click_y + self.winfo_y()
        self.geometry("+%s+%s" % (x, y))

    def update_animation(self):
        
        if self.check == 0:
            frame = self.idle[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.idle, self.event_number, 1, 9)

        elif self.check == 1:
            frame = self.idle_to_sleep[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.idle_to_sleep, self.event_number, 10, 10)

        elif self.check == 2:
            frame = self.sleep[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.sleep, self.event_number, 10, 15)

        elif self.check == 3:
            frame = self.sleep_to_idle[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.sleep_to_idle, self.event_number, 1, 1)

        elif self.check == 4:
            frame = self.walk_positive[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.walk_positive, self.event_number, 1, 9)
            self.x -= 3

        elif self.check == 5:
            frame = self.walk_negative[self.cycle]
            self.cycle, self.event_number = self.gif_work(self.cycle, self.walk_negative, self.event_number, 1, 9)
            self.x -= -3

        self.geometry('100x100+' + str(self.x) + '+1050')
        self.label.configure(image=frame)
        self.after(1, self.event, self.cycle, self.check, self.event_number, self.x)

    def event(self, cycle, check, event_number, x):
        idle_num = [1, 2, 3, 4]
        sleep_num = [10, 11, 12, 13, 15]
        walk_left = [6, 7]
        walk_right = [8, 9]

        if event_number in idle_num:
            check = 0
        elif event_number == 5:
            check = 1
        elif event_number in walk_left:
            check = 4
        elif event_number in walk_right:
            check = 5
        elif event_number in sleep_num:
            check = 2
        elif event_number == 14:
            check = 3

        self.after(100, self.update_animation)

    def gif_work(self, cycle, frames, event_number, first_num, last_num):
        if cycle < len(frames) - 1:
            cycle += 1
        else:
            cycle = 0
            event_number = random.randrange(first_num, last_num + 1, 1)
        return cycle, event_number


if __name__ == "__main__":
    print ("New")
    animated_character = AnimatedCharacter()
    animated_character.mainloop()
