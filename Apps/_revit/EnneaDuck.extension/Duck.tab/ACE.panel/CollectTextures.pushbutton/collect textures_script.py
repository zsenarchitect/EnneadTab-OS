from System import Environment
from rpw import db, revit, DB, exceptions
from pyrevit import forms
from shutil import copy
import os

import proDUCKtion # pyright: ignore 
from EnneadTab import ERROR_HANDLE
__title__ = 'Collect\nTextures'
__doc__ = 'Choose a new destination for texture images. Then Collect Textures copies all material texture images to this new location, and updates texture image path.\n'


@ERROR_HANDLE.try_catch_error()
def main():
    materials = get_materials()
    # new_folder = create_folder()
    new_folder = basefolder

    max_value = len(materials)
    with forms.ProgressBar(title="Material...\
            ({value} of {max_value})", cancellable="True") as pb:
        with db.Transaction("Copy and change rendering texture path") as t:
            for count, material in enumerate(materials):
                if pb.cancelled:
                    break
                else:
                    pb.update_progress(count, max_value)

                change_rendering_texture_path(material, new_folder)


def change_rendering_texture_path(material, new_folder):
    """
    see: https://thebuildingcoder.typepad.com/blog/2019/04/set-material-texture-path-in-editscope.html

    TODO:
        - RevitException.ArgumentException:
          Does not accept some values to be assigned as asset_bitmap.Value.
          Can be skipped [if asset_bitmap.IsValidValue(new_bitmap_path):]

    Copies the material generic appearance image to the new folder.
    Assigns the copy to the material.

    material -- Material Class object
    new_folder -- str (absolute path)
    """
    asset_element = get_asset_element(material)
    if asset_element:
        with DB.Visual.AppearanceAssetEditScope(revit.doc) as scope:
            active_asset = scope.Start(asset_element.Id)
            asset_diffuse = active_asset.FindByName(
                DB.Visual.Generic.GenericDiffuse)
            if asset_diffuse:
                asset = asset_diffuse.GetSingleConnectedAsset()
                if asset:
                    asset_bitmap = asset.FindByName(
                        DB.Visual.UnifiedBitmap.UnifiedbitmapBitmap)
                    bitmap_path = get_bitmap_path(asset_bitmap)

                    if not bitmap_path:
                        print("Skipping Revit out of the box material...")
                        # scope.Cancel()
                        return

                    new_bitmap_path = copy_by_path(bitmap_path, new_folder)

                    try:
                        asset_bitmap.Value = new_bitmap_path
                        print("Material texture path for [{}] changed.".format(
                            material.Name))
                        print("New texture path-> {}".format(new_bitmap_path))
                        print(20 * "-")
                        scope.Commit(True)
                    except exceptions.RevitExceptions.ArgumentException as e:
                        print("FAILED to change path for [{}]".format(
                            material.Name))
                        print("\tValue not accepted->({})".format(
                            new_bitmap_path))
                        print("\tException->: {}".format(e.Message))
                        print(20 * "-")
                        scope.Cancel()
                    except Exception as e:
                        # Other exceptions
                        print("FAIL for [{}]".format(material.Name))
                        print("\tException->: {}".format(e.Message))
                        print(20 * "-")
                        scope.Cancel()


def get_materials():
    """ Collect materials from active document """
    material_collector = db.Collector(of_class="Material", is_type=False)
    return material_collector.get_elements()


def create_folder():
    """ Takes user input to create a 'Materials' folder. """
    destination_folder = forms.pick_folder(title="Folder to save Materials TO")
    new_folder = os.path.join(destination_folder, "Materials")
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    return new_folder


def get_asset_element(material):
    """
    Gets the AppearanceAssetElement of the given material.
    If element is color or transparency only, returns None

    material - Material Class object
    """
    asset_id = material.AppearanceAssetId
    if asset_id.InvalidElementId == -1:
        return None
    else:
        return revit.doc.GetElement(asset_id)


def get_bitmap_path(bitmap_property):
    """
    Returns the absolute path of the given AssetPropertyString
    --> Path is relative to default Material Library

    Input raltive path like:
    '1/path/file' or
    '1/path/file | 2/path/file | ...'

    Output:
    'absolute/path/to/file'
    """
    bitmap_paths = bitmap_property.Value.split("|")
    library_paths = revit.app.GetLibraryPaths().Values
    for bitmap_path in bitmap_paths:
        if os.path.isabs(bitmap_path):
            return os.path.abspath(bitmap_path)
        else:
            for lib_path in library_paths:
                bit = os.path.dirname(os.path.relpath(bitmap_path))
                lib = os.path.abspath(lib_path)
                if bit.lower() in lib.lower():
                    return os.sep.join(
                        [lib, os.path.basename(bitmap_path)])


def copy_by_path(file_path, destination_folder):
    """
    Copies a file to a folder and returns the new path

    file_path -- str (absolute path)
    destination_folder -- str (absolute path)
    """
    try:
        copy(file_path, destination_folder)
    except EnvironmentError as e:
        # File exists at destination
        pass
    except Exception as e:
        # Other exceptions
        print(e)
    file_name = os.path.basename(file_path)
    new_path = os.path.join(destination_folder, file_name)
    return new_path



######################################################
if __name__ == "__main__":
   
    basefolder = forms.pick_folder()
    if basefolder:
        main()
