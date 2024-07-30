import shutil
import os
import time

def copy_revit_ini_files():
    # L:\4b_Applied Computing\01_Revit\Initialization\2025\Revit.ini
    # \\tsclient\L\4b_Applied Computing\01_Revit\Initialization\2025\Revit.ini
    # C:\ProgramData\Autodesk\RVT 2025\UserDataCache\Revit.ini
    stable_source_base = "L:\\4b_Applied Computing\\01_Revit\\Initialization"
    image_builder_base = "\\\\tsclient\\L\\4b_Applied Computing\\01_Revit\\Initialization"
    target_base = "C:\\ProgramData\\Autodesk\\RVT "
    filename = "Revit.ini"

    for year in range(2000, 2099):
        for source_base in [stable_source_base, image_builder_base]:
            source_path = os.path.join(source_base, f"{year}", filename)
            target_path = os.path.join(target_base + str(year), "UserDataCache", filename)
            if not os.path.exists(source_path):
                continue
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Copy the file
            shutil.copyfile(source_path, target_path)
            print(f"Copied {source_path} to {target_path}")

    print ("\n\nRestart Revit to see updates.")
    print ("You can close this window")
    time.sleep(30)

if __name__ == "__main__":
    copy_revit_ini_files()
