# Updated invoice details based on the provided table
invoice_details_updated = [
    ("17225", "$1,598.80"),
    ("17224", "$298.91"),
    ("E59EF017-0A0A-46F3-800E-7B945D614CB9", "$1,183.50"),
    ("17148", "$869.79")
]

# Define the field names for factura and importe based on the provided table
factura_fields = [
    "Texto9", "Texto11", "Texto13", "Texto15", 
    "Texto17", "Texto18", "Texto19", "Texto20", 
    "Texto25", "Texto27", "Texto29", "Texto31"
]

importe_fields = [
    "Texto10", "Texto12", "Texto14", "Texto16", 
    "Texto21", "Texto22", "Texto23", "Texto24", 
    "Texto26", "Texto28", "Texto30", "Texto32"
]

# Open the provided editable PDF again
doc = fitz.open("ARG_SolDeReembolsoINTEGRASalud.pdf")

# Load the first page
page = doc[0]

# Retrieve all widgets (form fields) from the page
widgets = page.widgets()

# Create a dictionary mapping widget names to widget objects
widget_dict = {widget.field_name: widget for widget in widgets}

# Fill in the updated invoice details to the appropriate fields using the widget dictionary
for i, (factura, importe) in enumerate(invoice_details_updated):
    if i < len(factura_fields):
        field_factura = widget_dict.get(factura_fields[i])
        field_importe = widget_dict.get(importe_fields[i])
        if field_factura:
            field_factura.text = factura
        if field_importe:
            field_importe.text = importe

# Fill in the updated total amount to the "Texto33" field
field_total = widget_dict.get("Texto33")
if field_total:
    field_total.text = f"${total_amount_updated:,.2f}"

# Save the modified PDF
final_modified_pdf_path_corrected_third_time = "/mnt/data/SolDeReembolsoINTEGRASaludEditable_final_modified_corrected_third_time.pdf"
doc.save(final_modified_pdf_path_corrected_third_time)
doc.close()

final_modified_pdf_path_corrected_third_time
