import os
import random
import ENVIRONMENT

try:
    import System.Drawing as SD # pyright: ignore
except Exception as e:
    pass


def get_image_path_by_name(file_name):
    path = "{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)
    if os.path.exists(path):
        return path
    print ("A ha! {} is not valid or accessibile. Better luck next time.".format(path))



def get_one_image_path_by_prefix(prefix):
    files = [os.path.join(ENVIRONMENT.IMAGE_FOLDER, f) for f in os.listdir(ENVIRONMENT.IMAGE_FOLDER) if f.startswith(prefix)]
    file = random.choice(files)
    return file


def average_RGB(R, G, B):
    """avergae RGB value to simulate a quick greyscale value

    Args:
        R (int): _description_
        G (int): _description_
        B (int): _description_

    Returns:
        int: math average of the RGB int value
    """
    return (R+G+B)/3

def convert_image_to_greyscale(original_image_path, new_image_path = None):
    """convert image to greyscale

    Args:
        original_image_path (str): _description_
        new_image_path (str): _description_
    """
    if new_image_path is None:
        new_image_path = original_image_path
    image = SD.Image.FromFile(original_image_path)
    for x in range(image.Width):
        for y in range(image.Height):
            pixel_color = image.GetPixel(x, y)
            R = pixel_color.R
            G = pixel_color.G
            B = pixel_color.B
            A = pixel_color.A
            new_color = SD.Color.FromArgb(A,
                                          average_RGB(R, G, B), 
                                          average_RGB(R, G, B), 
                                          average_RGB(R, G, B))
            image.SetPixel(x, y, new_color)
    image.Save(new_image_path)
    return image