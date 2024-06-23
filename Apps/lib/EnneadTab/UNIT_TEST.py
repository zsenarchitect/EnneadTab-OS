try:
    import importlib
except:
    import imp
import os
import traceback
import TEXT
import ENVIRONMENT


def print_boolean_in_color(bool):
    if not ENVIRONMENT.is_terminal_environment():
        return bool
    
    import TEXT
    if bool:
        return TEXT.colored_text("True", TEXT.TextColor.Green)
    else:
        return TEXT.colored_text("False", TEXT.TextColor.Red)  

def print_text_in_highlight_color(text):
    if not ENVIRONMENT.is_terminal_environment():
        return text

    return TEXT.colored_text(text, TEXT.TextColor.Blue)


IGNORE_LIST = ["__pycache__"]



class UnitTest:
    def __init__(self):
        self.failed_module = []
        self.count = 0
        
        
    def try_run_unit_test(self, module):

        print ("\n--{}:\nImport module [{}] Successfully".format(self.count + 1,
                                                                 print_text_in_highlight_color(module.__name__)))
        self.count += 1
        if not hasattr(module, 'unit_test'):
            return
        test_func = getattr(module, 'unit_test')
        if not callable(test_func):
            return
        
        print(print_text_in_highlight_color('Running unit test for module <{}>'.format(module.__name__)))
        try:
            test_func()
            print ("OK!")
            return True
        except AssertionError as e:
            print ("Assertion Error! There is some unexpected results in the test")
            print (traceback.format_exc())
            return False
        
    def process_folder(self, folder):
        if not os.path.isdir(folder):
            return

        
        for module_file in os.listdir(folder):
            if module_file.endswith('.pyc'):
                continue
            module_path = os.path.join(folder, module_file)

            
            if os.path.isdir(module_path):
                self.process_folder(module_path)
                continue
            if not module_file.endswith('.py'):
                continue
            module_name = module_file.split('.')[0]
            if module_name in IGNORE_LIST:
                continue
            try:
                module = imp.load_source(module_name, module_path)
            except:
                try:
                    module = importlib.import_module(module_name)
                except Exception as e:
                    print ("\n\nSomething is worng when importing [{}] becasue:\n\n++++++{}++++++\n\n\n".format(module_name,
                                                                                                                traceback.format_exc()))
                    continue
          
            
            if not self.try_run_unit_test(module):
                self.failed_module.append(module_name)
                

def test_core_module():
    tester = UnitTest()

    tester.process_folder(ENVIRONMENT.CORE_FOLDER)
    if not tester.failed_module:
        print ("below modules are failed.")
        print ("\n".join(tester.failed_module))
        
    
if __name__ == '__main__':
    test_core_module()