try:
    import tkinter as tk
    from tkinter import font
except:
    pass
import os

from creation import make_button

DEFAULT_NAME = "Type Here..."
class UI:

    def __init__(self, tab_folder, window_size=800, background_color="#333333"):
        self.main_folder = tab_folder
        tab_options = [f for f in os.listdir(self.main_folder) if f.endswith(".tab") or f.endswith(".menu")] 
 
        
        self.root = tk.Tk()
        self.root.title("Button Creator")

        # Calculate the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the x and y coordinates for centering vertically
        x = (screen_width - window_size) // 2
        y = (screen_height - window_size) // 2

        # Set the window size and position
        self.root.geometry("{}x{}+{}+{}".format(window_size, window_size, x, y))

        # Set the background color
        self.root.configure(bg=background_color)

        # Create a label for the text above the selection with bold font
        bold_font = font.Font(weight="bold")  # Create a bold font
        text_label = tk.Label(self.root, 
                              text="Select a tab to place this new button:", 
                              bg=background_color, 
                              fg="white",
                              font=bold_font)  # Set the label to use the bold font
        text_label.pack(pady=10)  # Add vertical space between this label and the next

        # Create a variable to store the selected option
        self.selected_tab = tk.StringVar()
        
        # Set the default selected option to the first option in the list
        self.selected_tab.set(tab_options[0])

        # Create radio buttons for each option
        for option in tab_options:
            radio_button = tk.Radiobutton(self.root, 
                                          text=option, 
                                          variable=self.selected_tab, 
                                          value=option, 
                                          command=self.tab_option_selected,
                                          bg=background_color,
                                          selectcolor="orange",
                                          fg="white",
                                          indicatoron=False,
                                          width=15)
            radio_button.pack()

        # Create a label to display the selected option
        self.label = tk.Label(self.root, text="", bg=background_color, fg="white")
        self.label.pack(pady=2)  # Add vertical space between this label and the next

        # add divider
        divider = tk.Frame(self.root, height=1, bg="white")
        divider.pack(fill="x", padx=10, pady=5)
        
        self.is_left_click = tk.BooleanVar()
        self.is_left_click.set(True)
        tk.Radiobutton(self.root, text="Left", variable=self.is_left_click, value=True, bg=background_color,fg="white",selectcolor="orange",indicatoron=False).pack(pady=3)
        tk.Radiobutton(self.root, text="Right", variable=self.is_left_click, value=False, bg=background_color,fg="white",selectcolor="orange",indicatoron=False).pack(pady=3)
        
        # add divider
        divider = tk.Frame(self.root, height=1, bg="white")
        divider.pack(fill="x", padx=10, pady=5)
        
        # Create a textbox for user input with default text "abcdef" and bold font
        text_label = tk.Label(self.root, 
                              text="What is the new button name?", 
                              bg=background_color, 
                              fg="white",
                              font=bold_font)  # Set the label to use the bold font
        text_label.pack(pady=2)  # Add vertical space between this label and the next
        
        self.user_input = tk.Entry(self.root, 
                                bg="gray", 
                                fg="white",
                                font=bold_font,
                                justify='center')  # Center-align text
        self.user_input.insert(0, DEFAULT_NAME)  # Set default text
        self.user_input.pack(pady=10)

        
        # Create a button to run the function with larger size and bolder text
        self.run_button = tk.Button(self.root, 
                                    text="Run", 
                                    command=self.run_function, 
                                    font=("Helvetica", 24)  
                                    )     
        self.run_button.pack(pady=10)


        self.root.mainloop()

    def tab_option_selected(self):
        selected_option = self.selected_tab.get()
        self.label.config(text='You selected: {}'.format(selected_option))

    def run_function(self):
        selected_option = self.selected_tab.get()
        user_text = self.user_input.get()
        if user_text == DEFAULT_NAME:
            return
        print('Selected Tab Folder: {}'.format(selected_option))
        print('User Text Input: {}'.format(user_text))
        print ("Click action = {}".format("Left" if self.is_left_click.get() else "Right"))
        self.root.destroy()  # Close the window when the function finishes
        make_button( "{}\\{}".format(self.main_folder, selected_option), user_text, is_left_click=self.is_left_click.get())

