import os
import fitz  # PyMuPDF
from tkinter import Tk, filedialog
from PIL import Image
from pathlib import Path

def extract_and_save_reverse_images(pdf_path, zoom_factor=2):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Get the PDF name without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Get the desktop path
    desktop_path = Path.home() / "Desktop"
    
    # Create output directory on desktop
    output_dir = desktop_path / f"ReverseExtractionJpg of {pdf_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the number of pages in the PDF
    num_pages = pdf_document.page_count
    
    # Process each page in reverse order
    for page_num in reversed(range(num_pages)):
        # Select the page
        page = pdf_document.load_page(page_num)
        
        # Apply zoom factor
        matrix = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to PIL image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the image as JPG
        output_path = output_dir / f"page_{num_pages - page_num}.jpg"
        img.save(output_path, "JPEG")
    
    print(f"Extraction complete! Images saved in: {output_dir}")

def pick_pdf_and_extract_images():
    # Initialize tkinter GUI
    root = Tk()
    root.withdraw()  # Hide the root window
    
    # Open file dialog to select PDF
    pdf_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )
    
    if pdf_path:
        extract_and_save_reverse_images(pdf_path)
        
# Run the GUI
if __name__ == "__main__":
    pick_pdf_and_extract_images()
