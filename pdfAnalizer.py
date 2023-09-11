import fitz
from datetime import datetime
import os

# Path to the PDF file
pdf_path = "SolDeReembolsoINTEGRASaludEditable.pdf"
pdf_path = "ARG_SolDeReembolsoINTEGRASalud.pdf"
pdf_path = "20230910_202906_ARG_SolDeReembolsoINTEGRASalud_generated_1.pdf"

filedsInterest = []
for i in range(8, 37):
    filedsInterest.append("Texto" + str(i))

# Open the PDF
doc = fitz.open(pdf_path)

first_page = doc[0]

# Get the fields from the first page (assuming the form fields are on the first page)
fields = doc[0].widgets()

# Print all the field forms
for field in fields:
    print(f"Field Name: {field.field_name}, Field Type: {field.field_type}, Field xref: {field.xref}, Field Value: {field.field_value}")
    if field.field_type == 7:
        field.field_value = "_ediatdo"
        field.update()

print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")

fields = doc[0].widgets()
for field in fields:
    print(f"Field Name: {field.field_name}, Field Type: {field.field_type}, Field Value: {field.field_value}")

print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")


print("|Name|xref|")
print("|---|---|")
xrefInterest = []
fields = doc[0].widgets()
for field in fields:
    if field.field_name in filedsInterest:
        print(f"|{field.field_name}|{field.xref}|")
        xrefInterest.append(field.xref)


for i in xrefInterest:
    field = first_page.load_widget(i)
    if field != None:
        print(f"Field Name: {field.field_name}, Field Type: {field.field_type}, Field xref: {field.xref}, Field Value: {field.field_value}")


field = first_page.load_widget(81)
field.field_value = "666"
field.update()


fecha = datetime.now().strftime("%Y%m%d_%H%M%s")
base_name = os.path.basename(pdf_path).split('.')[0]
output_pdf = f"{fecha}_{base_name}_modified.pdf"

# Guardar los cambios en un nuevo archivo PDF
doc.save(output_pdf)
# Close the document

doc.close()
