import ENVIRONMENT

import sys
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)

from termcolor import colored # pyright: ignore
from COLOR import TextColor
    

def colored_text(text, color = TextColor.Cyan, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """

    
    if "colored" not in globals():
        # in some terminal run, it cannot read the dependecy folder so cannot load the colored moudle
        return text
    return colored(text, color, on_color, attrs)



def unit_test():
    print (colored_text("Test dfault color text"))
    print (colored_text("test green", TextColor.Green))#, attrs=[TextColor.Blue, 'blink']))




if __name__ == "__main__":
    unit_test()