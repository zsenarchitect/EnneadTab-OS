import os
import fitz  # PyMuPDF
from tkinter import Tk, filedialog, Button, Checkbutton, IntVar, Label
from tkinter import messagebox
from PIL import Image
from pathlib import Path
import _Exe_Util


def extract_and_save_images(pdf_path, reverse_order, zoom_factor=2):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Get the PDF name without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Get the desktop path
    desktop_path = Path.home() / "Desktop"
    
    # Create output directory on desktop
    output_dir = desktop_path / f"ExtractionJpg of {pdf_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the number of pages in the PDF
    num_pages = pdf_document.page_count
    
    # Determine the order of processing pages
    page_range = reversed(range(num_pages)) if reverse_order else range(num_pages)
    
    # Process each page in the specified order
    for page_num in page_range:
        # Select the page
        page = pdf_document.load_page(page_num)
        
        # Apply zoom factor
        matrix = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to PIL image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the image as JPG
        page_index = num_pages - page_num if reverse_order else page_num + 1
        output_path = output_dir / f"page_{page_index}.jpg"
        img.save(output_path, "JPEG")
    
    print(f"Extraction complete! Images saved in: {output_dir}")
    return output_dir

@_Exe_Util.try_catch_error
def pick_pdf_and_extract_images():
    # Initialize tkinter GUI
    root = Tk()
    root.title("PDF Image Extractor")
    root.geometry("600x400")  # Set default width to 600 pixels
    
    reverse_var = IntVar(value=1)  # Default to reverse order
    root.output_dir = None  # Initialize the output directory

    def select_pdf():
        pdf_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if pdf_path:
            pdf_label.config(text=os.path.basename(pdf_path))
            root.pdf_path = pdf_path

    def process_pdf():
        if hasattr(root, 'pdf_path') and root.pdf_path:
            reverse_order = reverse_var.get() == 1
            output_dir = extract_and_save_images(root.pdf_path, reverse_order)
            root.output_dir = output_dir
            messagebox.showinfo("Processing Complete", f"Extraction complete! Images saved in: {output_dir}")

    def open_output_folder():
        if root.output_dir:
            os.startfile(root.output_dir)

    pdf_label = Label(root, text="No PDF selected")
    pdf_label.pack(pady=10)

    select_button = Button(root, text="Select PDF", command=select_pdf)
    select_button.pack(pady=5)
    
    reverse_checkbox = Checkbutton(root, text="Reverse Order", variable=reverse_var)
    reverse_checkbox.pack(pady=5)
    
    process_button = Button(root, text="Process", command=process_pdf)
    process_button.pack(pady=5)
    
    open_folder_button = Button(root, text="Open Output Folder", command=open_output_folder)
    open_folder_button.pack(pady=5)
    
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    pick_pdf_and_extract_images()
