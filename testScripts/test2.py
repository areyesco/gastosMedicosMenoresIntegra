import fitz  # PyMuPDF

# Replace 'your_file.pdf' with the path to your PDF file
pdf_file = "SolDeReembolsoINTEGRASaludEditable_ejemploManual.pdf"

# Open the PDF file
pdf_document = fitz.open(pdf_file)

# Get the first page of the PDF
first_page = pdf_document[0]

# Iterate through the annotations on the page
for annot in first_page.annots():
    # Check if the annotation has a name
    if annot.info:
        # Print the name of the annotation
        print("Annotation Name:", annot.info)

# Close the PDF file
pdf_document.close()
