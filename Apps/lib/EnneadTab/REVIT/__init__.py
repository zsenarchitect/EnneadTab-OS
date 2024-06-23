import os



# Function to dynamically import all submodules
def import_submodules():
    # Get the package directory
    package_dir = os.path.dirname(__file__)
    
    for module in os.listdir(package_dir):

        if module == '__init__.py':
            continue

        if module[-3:] != '.py':
            continue
        try:
            __import__(module[:-3], locals(), globals())
        except Exception as e:
            print (e)
            print ("Cannot import {}".format(module))


            
# Import all submodules
import_submodules()




