import fitz
from datetime import datetime
import os

# Path to the PDF file
pdf_path = "ARG_SolDeReembolsoINTEGRASalud.pdf"

# Open the PDF
doc = fitz.open(pdf_path)

first_page = doc[0]

field = first_page.load_widget(21)
field.field_value = "41"
field.update()


fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = os.path.basename(pdf_path).split('.')[0]
output_pdf = f"{fecha}_{base_name}_modified.pdf"

# Guardar los cambios en un nuevo archivo PDF
doc.save(output_pdf)
# Close the document

doc.close()
