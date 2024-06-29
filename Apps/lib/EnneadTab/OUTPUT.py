"""to-do: make a standalone method to print long and interactive output, becasuwe the default way Rhino print output in cammand history sucks!

this class need to do following:
+singelton format, call many times, return one. Deafault to have one instance per caller, but also option to share common output.
+buttons in line that bind a func(zoom to element(s), select elemet(s), checkbox selection, its title should be customizeblae)
+ a search bar at the top of the web


2023-12-16:
this might be hard to make the button iteract back to the main software
"""


import os
import io
import webbrowser

import DATA_FILE
import FOLDER 
import ENVIRONMENT
import ENVIRONMENT
import NOTIFICATION
import TIME 
import EXE 

# STYLE_MAP = {"main_body":"p",
#              "title":"h1",
#              "sub_title":"h2",
#              "foot_note":"foot_note"}

FUNCS = """
<script>
function sample_func(btn) {
  alert(btn.innerText);
  prompt("Type anything:");
  confirm("Do you want to continue?");
}

</script>
"""

class Style:
    MainBody = "p"
    Title = "h1"
    SubTitle = "h2"
    Footnote = "foot_note"
    

class Output:
    """_summary_

    Returns:
        _type_: _description_
    """

    _instance = None
    _out = [] # the container for everything that is outputing
    _report_path = FOLDER.get_EA_dump_folder_file("OUTPUT.html")
    _graphic_settings = {
            'background_color': 'rgb(50, 50, 50)',
            'font_family': 'Helvetica, Arial, sans-serif',
            'text_color': 'white'
        }

    # when in Reivit, do not print to pollute the nice pyrevit console
    _is_print_out = not ENVIRONMENT.is_Revit_environment()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def write(self, content, style = None, as_str=False):
        if not style:
            style = Style.MainBody
        if as_str:
            content = str(content)
        Output._out.append((style, content))
        if Output._is_print_out:
            print (content)

    def reset_output(self):
        Output._out = []
        
    def plot(self):
        self._generate_html_report()
        self._print_html_report()
        

    def _generate_html_report(self):
        with io.open(Output._report_path, 'w', encoding='utf-8') as report_file:
            report_file.write("<html><head><title>EnneadTab Output</title></head><body>")
            report_file.write("<style>")
            report_file.write("body {{ background-color: {}; font-family: {}; color: {}; margin-left:300px;margin-right:300px;}}"
                              .format(Output._graphic_settings['background_color'], 
                                      Output._graphic_settings['font_family'], 
                                      Output._graphic_settings['text_color']))
            report_file.write("h1 {{ font-size: 30px; font-weight: bold; }}")
            report_file.write("h2 {{ font-size: 20px; color: red; }}")
            report_file.write("ul {{ list-style-type: none; margin: 20; padding: 10; }}")
            report_file.write("li {{ margin-left: 40px; }}") 
            report_file.write(".foot_note {{ font-size: 8px; color: red; }}") 
            report_file.write("</style>")

            report_file.write(FUNCS)

            
            report_file.write("<h1 style='text-align: center;'>{}</h1>".format("EnneadTab Console"))
            report_file.write("<div style='text-align: center;'>")
            report_file.write("<img src='{}\\logo_ennead-e.png' height='80'>".format(ENVIRONMENT.IMAGE_FOLDER))
            report_file.write("</div>")
            report_file.write("<p style='text-align: center;' class='foot_note'>{}</p>".format(TIME.get_formatted_current_time()))
            report_file.write("<hr>") 

            for header_style, content in Output._out:
        
                
                if isinstance(content, list):
                    report_file.write("<ul>")
                    for i, item in enumerate(content):
                        report_file.write("<li>{0} : {1}</li>".format(i+1,
                                                                    Output.format_content(item)))                      
                    report_file.write("</ul>")
                else:
                    report_file.write("<{0}>{1}</{0}>".format(header_style, Output.format_content(content)))
                    
                
            report_file.write("</body></html>")

    @staticmethod
    def format_content(input):
        if "bt_" in str(input):
            return "<button onclick='return sample_func(this)'>{}</button>".format(input.split("bt_")[1])
        
        if os.path.exists(str(input)):
            if "_large" in str(input):
                return "<img src='{}' height = '800'>".format(input)
            return "<img src='{}' height = '300'>".format(input)
        return str(input).replace("\n", "<br>")

    # try to use a dummy top match pyrevit output method
    def print_md(self, content):
        print (content)

    # try to use a dummy top match pyrevit output method
    def print_html(self, content):
        print (content)

    def _print_html_report(self):
        webbrowser.open("file://{}".format(Output._report_path))


    def insert_division(self):
        self.write("<hr>")






####################################################
def get_output():
    return Output()


def unit_test():
    output = get_output()
    output.write("Sample text in 'Title' style",Style.Title)
    output.write("Sample text in 'SubTitle' style",Style.SubTitle)
    output.write("Sample text in default style")
    output.write("sample text in foot note style(this is not working yet)", Style.Footnote)

    output.insert_division()
    output.write("\n\n")
    output.insert_division()
    
    output.write("Trying to print list as item list")
    test_list = ["A", "B", "C", 99, 440, 123]
    output.write(test_list)
    output.write("Trying to print list as str")
    output.write(test_list, as_str=True)
    
    output.insert_division()

    
    output.write("Trying to print image")
    output.write("{}\\meme_you sync first.jpg".format(ENVIRONMENT.IMAGE_FOLDER))


    output.insert_division()


    output.write("Trying to print a button")
    output.write("bt_sample button")


    output.insert_division()
    new_output = get_output()
    new_output.write("This is a new output object but should write to same old output window")
    new_output.plot()



def display_pyrevit_output_on_browser():
    if not ENVIRONMENT.is_Revit_environment():
        NOTIFICATION.messenger("currently only support Revit Env")
        return
    from pyrevit import script
    dest_file = FOLDER.get_EA_dump_folder_file("EnneadTab Output.html")
    output = script.get_output()
    output.save_contents(dest_file)
    output.close()
    os.startfile(dest_file)
      
#######################################################
if __name__ == "__main__":
    unit_test()