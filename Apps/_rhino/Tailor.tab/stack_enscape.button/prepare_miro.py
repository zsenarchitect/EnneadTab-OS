
import os
import shutil
from PIL import Image

ROOT_FOLDER = r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings"
MIRO_FOLDER = "{}\\miro_temp".format(ROOT_FOLDER)
STUDY_NAMES = [
    "angled_frame", #precast bg, copper foreground
    "angled_frame_alt", #copper on bg and fg
    "angled_frame_alt_alt", #terraceoota on bg and fg
    "sawtooth",
    "hori",
    "solar_panel", 
        ]

def main():

    for f in os.listdir(MIRO_FOLDER):
        os.remove(os.path.join(MIRO_FOLDER,f))

    for study in STUDY_NAMES:
        print ("working on " + study)
        folder = "{}\\{}".format(ROOT_FOLDER, study)

        stitch_files = []
        for f in os.listdir(folder):
            if f.endswith("jpg"):
                shutil.copyfile(os.path.join(folder, f),
                                os.path.join(MIRO_FOLDER, f))
                
                stitch_files.append(os.path.join(folder, f))

        stitch_images_horizontally(sorted(stitch_files), study)
    print ("!!!!!!!!!!!!!!Miro Ready")

def stitch_images_horizontally(image_paths, study_name , gap=50):
    images = [Image.open(img_path).convert('RGBA') for img_path in image_paths]
    resized_images = [resize_image_to_height(img) for img in images]
    
    total_width = sum(img.width for img in resized_images) + gap * (len(resized_images) - 1)
    max_height = max(img.height for img in resized_images)

    # Create a new blank image with transparency
    new_image = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

    x_offset = 0
    for img in resized_images:
        new_image.paste(img, (x_offset, 0), img)  # Use img as mask for transparency
        x_offset += img.width + gap
    new_image.save("{}\\_stiched_{}.png".format(MIRO_FOLDER, study_name))

def resize_image(image, max_dimension=1500):
    # Calculate the scaling factor
    scaling_factor = min(max_dimension / float(image.size[0]), max_dimension / float(image.size[1]))
    if scaling_factor < 1:  # Only resize if the image is larger than the max dimension
        new_size = (int(image.size[0] * scaling_factor), int(image.size[1] * scaling_factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def resize_image_to_height(image, target_height=1500):
    # Calculate the scaling factor to achieve the target height
    scaling_factor = target_height / float(image.size[1])
    new_width = int(image.size[0] * scaling_factor)
    
    # Resize the image to the new dimensions
    return image.resize((new_width, target_height), Image.Resampling.LANCZOS)

if __name__ == "__main__":
    main()