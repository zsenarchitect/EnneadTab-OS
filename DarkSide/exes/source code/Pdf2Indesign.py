import PyPDF2
import subprocess
import os
import winsound
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to extract the number of pages in a PDF
def get_pdf_page_count(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    return len(pdf_reader.pages)

# ExtendScript to create InDesign document and place PDF pages
extendscript = """
try {{
    var myDocument = app.documents.add();
    myDocument.documentPreferences.pageWidth = "17in";
    myDocument.documentPreferences.pageHeight = "11in";
    myDocument.documentPreferences.facingPages = false;
    var pdfPath = "{pdf_path}";
    var pageCount = {page_count};

    for (var i = 0; i < pageCount; i++) {{
        try {{
            if (i > 0) {{
                myDocument.spreads.add();
            }}
            app.scriptPreferences.measurementUnit = MeasurementUnits.INCHES_DECIMAL;
            var mySpread = myDocument.spreads.item(i);
            app.pdfPlacePreferences.pageNumber = i + 1;
            var myPDFPage = mySpread.place(File(pdfPath), [0, 0])[0];
            myPDFPage.geometricBounds = [0, 0, myDocument.documentPreferences.pageHeight, myDocument.documentPreferences.pageWidth];
            myPDFPage.fit(FitOptions.FRAME_TO_CONTENT);
            myPDFPage.fit(FitOptions.FILL_PROPORTIONALLY);
            
        }} catch (e) {{
            alert("Error placing page " + (i + 1) + ": " + e.message);
        }}
    }}

    try {{
        var myFile = new File("{indd_path}");
        myDocument.save(myFile);
    }} catch (e) {{
        alert("Error saving document: " + e.message);
    }} finally {{
        myDocument.close();
    }}
}} catch (e) {{
    alert("Error creating document: " + e.message);
}}
"""

# Function to create ExtendScript from template
def create_extendscript(pdf_path, page_count, indd_path):
    return extendscript.format(pdf_path=pdf_path.replace("\\", "\\\\").replace("/", "\\\\"), page_count=page_count, indd_path=indd_path.replace("\\", "\\\\"))

# Function to get the desktop path
def get_desktop_path():
    return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

# Function to run ExtendScript from Python on Windows using VBScript
def run_extendscript(script, close_indesign, version):
    desktop_path = get_desktop_path()
    script_path = os.path.join(desktop_path, "script.jsx")
    with open(script_path, "w") as f:
        f.write(script)
    
    vbs_content = """
Set app = CreateObject("InDesign.Application.{version}")
app.DoScript "{script_path}", 1246973031
{close_indesign}
""".format(version=version, script_path=script_path, close_indesign=close_indesign)

    vbs_path = os.path.join(desktop_path, "run_script.vbs")
    with open(vbs_path, "w") as f:
        f.write(vbs_content)
    
    subprocess.call(["cscript", vbs_path])

# Function to process a single PDF file
def process_pdf(pdf_path, version, close_indesign=False):
    page_count = get_pdf_page_count(pdf_path)
    indd_path = os.path.splitext(pdf_path)[0] + ".indd"
    script = create_extendscript(pdf_path, page_count, indd_path)
    # print (script)
    run_extendscript(script, close_indesign, version)

# Main function to process all PDF files in a directory
def process_all_pdfs_in_directory(directory, version):
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    for i, filename in enumerate(pdf_files):
        print (filename)
        pdf_path = os.path.join(directory, filename)
        close_indesign = "app.quit();" if i == len(pdf_files) - 1 else ""
        process_pdf(pdf_path, version, close_indesign)
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

# GUI for folder selection
def select_folder(version_entry):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        version = version_entry.get()
        process_all_pdfs_in_directory(folder_selected, version)
        messagebox.showinfo("Success", "All PDFs have been processed successfully!")

def main():
    # Create the main window
    root = tk.Tk()
    root.title("PDF to InDesign Processor")

    # Add a label
    lbl_instruction = tk.Label(root, text="Select folder that contains the PDFs to convert to InDesign")
    lbl_instruction.pack(pady=10)

    # Add a label and entry for InDesign version
    lbl_version = tk.Label(root, text="Your InDesign version")
    lbl_version.pack()
    version_entry = tk.Entry(root, justify='center')
    version_entry.insert(0, "2024")
    version_entry.pack(pady=5)

    # Add a button to select the folder
    btn_select_folder = tk.Button(root, text="Select Folder", command=lambda: select_folder(version_entry))
    btn_select_folder.pack(pady=20)

    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    main()
