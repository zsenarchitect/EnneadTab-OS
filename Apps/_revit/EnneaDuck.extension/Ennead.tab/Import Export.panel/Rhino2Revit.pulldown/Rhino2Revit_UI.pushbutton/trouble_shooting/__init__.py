from pyrevit import  script
import os

from EnneadTab import EXE, FOLDER, ERROR_HANDLE

@ERROR_HANDLE.try_catch_error()
def show_instruction(output):
    #output = script.get_output()
    #output.close_others()

    images_source = os.path.dirname(os.path.realpath(__file__))

    print("Things you might not know: If you have flat face in the element, and if the moving distance is within the limit of bounding face, you can parametrically control converted element just like native Revit element.")
    image = "{}\{}".format(images_source,"instruction_lock control.jpg")
    output.print_image(image)

    print("Things you might not know: You can force a 3D obj into a detail item family, and even perform join/void cut inside this 2D family. Great for making combined mask region.")
    image = "{}\{}".format(images_source,"instruction_3d in 2d.jpg")
    output.print_image(image)


    print("\n\n\n\n\n\n\n\n")
    output.print_md ("##The .3dm format is the preferred method(the same format as Rhino file), it converts the most amount of content close to Revit freeform syntax. But sometimes you will see when Rhino 3dm file is decoded, not all solid can be read, 90% of time it is due to the Rhino geometry not being optimized. \nFor example, non-enclosed polysurface, very tight touch edge, non-manifold geometry or any other invalid geometry, all can potentially make Revit unhappy about the 3dm convertion. For best result, please be familiar with the concept of G-continuity, Topology in Brep, etc.\n\nTry those steps to attempt to fix.")



    print("\n\n1. curvature check: too much warpping is not welcomed in revit.")
    image = "{}\{}".format(images_source,"instruction_curvature.jpg")
    output.print_image(image)

    print("\n\n2. non-manifold check: Should avoid, always.")
    image = "{}\{}".format(images_source,"instruction_non manifold.jpg")
    output.print_image(image)

    print("\n\n3. valid and openness check: invalid geomtry should be fixed before carrying over to revit. A open polysurface/surface does NOT mean a failed revit convert, it really depends on design intent. The convertion can happen to single surface if desired.")
    output.print_md("**But be aware that only closed polysurface/surface can be further boolean joined/cut in revit enviornment.**")
    image = "{}\{}".format(images_source,"instruction_valid and closed.jpg")
    output.print_image(image)

    print("\n\n4. rationalization check: Whenever possible, do not use the study model or competition model directly. Please try to rationalize your design before moving on to revit stage. Make better source geomtry based on your intent. This will benifit your documentation as well.")
    image = "{}\{}".format(images_source,"instruction_simplify ruled geomtry generation.jpg")
    output.print_image(image)

    print("\n\n5. zebra check: It reveals how dense the curvature distribute over surface. Not a direct indicator of why things fails, but it helps you find where things might be wrong.")
    image = "{}\{}".format(images_source,"instruction_zebra.jpg")
    output.print_image(image)

    """
    print("\n\n\n\n\n\n\n\n")
    output.print_md ("##Ok\n\n\n\n\n\n\n##If after all attempt and you still have a few pieces not convertible#\nyou might use the second method. It is less preferred because the whole dwg will be treated as a single object instead of many independent objects. \n\nWe can use **3D CAD** to transfer geometry, so you will need to save rhino as ACIS solid dwg(the same format you used to export Revit to rhino as solid instead of mesh)")
    image = "{}\{}".format(images_source,"instruction1.jpg")
    output.print_image(image)

    output.print_md ("\n\n##It is very important to use a Solid dwg option.")
    image = "{}\{}".format(images_source,"instruction2.jpg")
    output.print_image(image)

    output.print_md ("\n\n##Then use this emergency convert and follow prompt.")
    image = "{}\{}".format(images_source,"instruction_use force import.jpg")
    output.print_image(image)
    """

    output.set_width(1000)
    output.set_height(800)
    output.center()
    temp_file = FOLDER.get_EA_dump_folder_file("Rhino2Revit_instruction.html")
    output.save_contents(temp_file)
    EXE.open_file_in_default_application(temp_file)


# print "Final note: use Revit-->Rhino-->Revit workflow and reconstruct your geometry with much more care, limit the amount of external geometry because even after conversion their parametric ability is in no way native Revit element. This is true for both EnneadTab converter and Rhino. Inside. It will relate to the Revit file performance."


if __name__ == "__main__":
    pass