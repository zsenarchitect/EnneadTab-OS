__doc__ = "Common revit family syntax you can use in family formula"
__title__ = "Family Fomula\nCheat Sheet"
__context__ = 'zero-doc'

from pyrevit import script

from EnneadTab import ERROR_HANDLE

@ERROR_HANDLE.try_catch_error()
def give_me_cheat_sheet():
    data_table = []
    def data(name, description, note):
        data_table.append( [name, description, note])

    def final_print_table():
        columns = ["fomula", "description", "notes"]
        output.print_table(table_data=data_table,title="Useful fomula in family editor",columns = columns)



    data("not(x)",\
        "return the opposite of x",\
        "only for Yes/No parameters")

    data("and(x1,x2,x3...)",\
        "return True if every input is true, otherwise return False",\
        "only for Yes/No parameters")

    data("or(x1,x2,x3...)",\
        "return True if any input is true, otherwise return False",\
        "only for Yes/No parameters")

    data("if(condition,A,B)",\
        "return result A if condition is true, otherwise return result B.",\
        "result can be Yes/No parameter, length parameter, family type parameter, number parameter, and even another nested if() statement.")

    data("abs(x)",\
        "return absolute value of x",\
        "abs(-10) --> 10")

    data("sqrt(x)",\
        "return square root value of x",\
        "abs(9) --> 3")

    data("x^y",\
        "return x raised to the power of y",\
        "4^2 --> 16")

    data("round(x)",\
        "return nearest whole number of x",\
        "round(3.1) --> 3")

    data("roundup(x)",\
        "return nearest whole number larger than x",\
        "roundup(3.1) --> 4")

    data("rounddown(x)",\
        "return nearest whole number smaller than x",\
        "rounddown(3.1) --> 3")

    data("pi",\
        "return math pi",\
        "~3.1415926535897932...")

    data("sin(A)",\
        "return a/c",\
        "See diagram below")

    data("cos(A)",\
        "return b/c",\
        "See diagram below")

    data("tan(A)",\
        "return a/b",\
        "See diagram below")

    data("asin(a/c)",\
        "return A",\
        "See diagram below")

    data("acos(b/c)",\
        "return A",\
        "See diagram below")

    data("atan(a/b)",\
        "return A",\
        "See diagram below")


    output = script.get_output()
    output.set_title("Cheat Sheet")
    output.set_width(1500)
    output.set_height(900)
    output.center()
    output.close_others()
    #output.open_url("http://dict.cn/")
    final_print_table()

    """
    print(script.get_script_path())
    print(script.get_bundle_files())
    print(script.get_bundle_file('triangle.png'))
    """
    #get_bundle file location
    output.print_image(script.get_bundle_file("triangle.png"))

    print("Advanced Examples:")
    print("show_mullion_H._intermediate = if(or(is_louver, H - spandrel_H < 3000), no, yes)")
    print("when you have louver or the glass height below spandrel is smaller than 3000mm, in either case the intermediate mullion will be hidden.")

if __name__ == "__main__":
    give_me_cheat_sheet()
  