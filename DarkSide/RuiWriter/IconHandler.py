from PIL import Image
import base64
from constants import SPECIAL_LIST_KEY
import os
import io
import textwrap
from GuidHandler import GuidHandler


# from BaseHandler import BaseHandler
# maybe do not share icon , because button left right macro should use separate bitmap Id for be safe. 
# BUT, bitmap index might cure this in rui 

# this is intentionally not inherating from base class
class IconHandler:
    bitmap_sizes = {16:"small_bitmap", 
                    24:"normal_bitmap",
                    32:"large_bitmap"}
    # print (sorted(bitmap_sizes)[0])
    default_icon = "{}\default_icon.png".format(os.path.dirname(__file__))

    def __init__(self, image_path, caller = None):
        """_summary_

        Args:
            image_path (_type_): _description_
            caller (_type_, optional): allow additional info so icon index table will not overlap. Defaults to None. This is also the reason in guid json some key file name a re funny long
        """
        if image_path is None:
            image_path = IconHandler. default_icon

        self.path = image_path
        self.image = Image.open(image_path).convert('RGBA')
        if caller:
            self.guid = GuidHandler(image_path + caller).guid
        else:
            self.guid = GuidHandler(image_path).guid


    def __repr__(self):
        return f"IconHandler: GUID = {self.guid}"

    
    def get_bitmap_text(self, size):
        resized_image = self.image.resize((size, size), Image.LANCZOS)
        # print (resized_image)
        image_byte_array = resized_image.tobytes()
        # print (image_byte_array)
        base64_image_text = base64.b64encode(image_byte_array).decode()
        # print (base64_image_text)
            
        return base64_image_text

    @property
    def bitmap_small_text(self):
        return self.get_bitmap_text(sorted(IconHandler.bitmap_sizes)[0])

    @property
    def bitmap_medium_text(self):
        return self.get_bitmap_text(sorted(IconHandler.bitmap_sizes)[1])

    @property
    def bitmap_large_text(self):
        return self.get_bitmap_text(sorted(IconHandler.bitmap_sizes)[2])




    @staticmethod
    def chain_bitmap_text(icon_list):
        # this will order up index for icon guid, and generate chained text based on this index
        # it need to run three times, once per icon size

        # return dict of smal, med, large.

        index_icon_list = [{"bitmap_item":{"guid":icon.guid,
                                           "index":str(i)}} for i, icon in enumerate(icon_list)]


        out = {}
        for size in sorted(IconHandler.bitmap_sizes):
            size_name = IconHandler.bitmap_sizes[size]

            # bitmap_text = ""
            # for icon in icon_list:
            #     bitmap_text += icon.get_bitmap_text(size)

            bitmap_text = combined_image_text(icon_list, size)
            
            # max 76 chac
            bitmap_text = textwrap.fill(bitmap_text, width=76)

            #test_bitmap(bitmap_text, size)

                
            out[size_name] = {"item_width":str(size),
                              "item_height": str(size),
                                 SPECIAL_LIST_KEY:index_icon_list,
                                 "bitmap": bitmap_text
                                 }

        return out

        
def combined_image_text(icon_list, size):
    # Create a BytesIO object to store the combined image data
    combined_image_io = io.BytesIO()

    # Calculate the width and height of the combined image
    
    combined_width = size
    combined_height = size * len(icon_list)

    # Create a new image with the combined dimensions
    combined_image = Image.new('RGBA', (combined_width, combined_height))

    # Paste the all images side by side in the combined image
    for i, image_handler in enumerate(icon_list):
        resized_image = image_handler.image.resize((size, size), Image.LANCZOS)
        combined_image.paste(resized_image, (0, i * size))

    # Save the combined image as a PNG
    combined_image.save(combined_image_io, format='PNG')

    # Get the bytes of the combined image
    combined_image_data = combined_image_io.getvalue()

    # Encode the combined image as base64
    combined_base64 = base64.b64encode(combined_image_data).decode()


    return combined_base64

    
def test_bitmap(bitmap_text, size):
    print ("\n\n", size, " version:\n", bitmap_text)
    return
    decoded_bitmap = base64.b64decode(bitmap_text)    
    print (decoded_bitmap)        
    # save the decoded bitmap to a file
    local_bmp = "{}\decoded_bitmap_{}.bmp".format(OS_ROOT_FOLDER,
                                                    size)
    with open(local_bmp, "wb") as f:
        f.write(decoded_bitmap)
        
        

if __name__ == "__main__":
    sample_icon = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Toolbar\Block.tab\make_block_unique.button\icon.png"
    sample_icon = IconHandler(sample_icon)
    # sample_icon.get_bitmap_text(16)
    IconHandler.chain_bitmap_text([sample_icon])