import os

def pdf2img(pdf_path, output_path = None):
    pass


def img2pdf(image_path, output_path = None):
    """convert image to pdf.

    Args:
        image_path (str): path for the input image
        pdf_path (str): path for the output pdf
    """
    from PIL import Image

    
    if pdf_path is None:
        # replace any image extension with pdf extension
        extension = os.path.splitext(image_path)[1]
        pdf_path = image_path.replace(extension, ".pdf")
    
    # Open the image
    with Image.open(image_path) as img:
        # Converting the image to RGB, to ensure compatibility
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as PDF
        img.save(pdf_path, "PDF", resolution=100.0)
    return pdf_path



def pdfs2pdf(combined_pdf_file_path, list_of_filepaths, reorder = False):
    """merge multiple pdfs to single pdf.

    Args:
        combined_pdf_file_path (str): path for final product
        list_of_filepaths (list): list of l=path for the input pdfs
        reorder (bool, optional): reorder the pdf alphabetically. Defaults to False.
    """
    from PyPDF2 import PdfFileMerger

    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        merger.append(filepath)

    merger.write(combined_pdf_file_path)
    merger.close()


def images2pdf(combined_pdf_file_path, list_of_filepaths, reorder = False):
    """merge multiple images to single pdf.

    Args:
        combined_pdf_file_path (str): path for final product
        list_of_filepaths (list): list of l=path for the input images
        reorder (bool, optional): reorder the pdf alphabetically. Defaults to False.
    """
    from PyPDF2 import PdfFileMerger

    from PIL import Image
    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        with Image.open(filepath) as img:
            merger.append(img)

    merger.write(combined_pdf_file_path)
    merger.close()


