import fitz  # PyMuPDF
from datetime import datetime
import os
from app_config import AppConfig
import re

# Load configuration
app_config = AppConfig()

def convert_string_to_number(input_string):
    # Remove non-numeric characters (commas, dollar sign, spaces, etc.)
    cleaned_string = re.sub(r'[^\d.]', '', input_string)

    # Convert the cleaned string to a floating-point number (float)
    try:
        number = float(cleaned_string)
        if app_config.bDebug:
            print(f"input_string: {input_string}, cleaned_string: {cleaned_string}, number: {number}")
        return number
    except ValueError:
        # If conversion fails, handle the exception as needed
        return None

def update_widget( page, wid_xref, value ):
    global bDebug
    wid_aux = page.load_widget(wid_xref)
    if wid_aux != None:
        if value == None:
            value = ""
        wid_aux.field_value = str(value)
        wid_aux.update()
        if app_config.bDebug:
            print(f"Widget updated, name: {wid_aux.field_name}, xref: {wid_aux.xref}, value: {wid_aux.field_value}")

def update_document(page, invoices, amounts):
    """
    Update document with invoices and amounts

    Args:
        invoices (list): List of invoice values.
        amounts (list): List of amount values.

    Returns:
        
    """
    total_invoices_amount = 0
    for invoice, amount, invoice_xref, amount_xref in zip(invoices, amounts, app_config.invoice_widgets, app_config.amount_widgets):
        # Get and remove the first invoice widget.
        #invoice_xref = invoice_widgets.pop(0)

        # Get and remove the first amount widget.
        #amount_xref = amount_widgets.pop(0)

        # Update invoice widget
        #mod_invoice = {"xref": invoice_xref, "value": invoice}
        update_widget(page, invoice_xref, invoice)

        # Update amount widget
        #mod_amount = {"xref": amount_xref, "value": amount}
        amount_number = convert_string_to_number(amount)
        if amount_number is None:
            raise ValueError(f"The amount must be a number: invoice: {invoice}, amount: {amount}, amount number: {amount_number}")
        
        if amount_number >= app_config.max_amount:
            raise ValueError(f"The amount is bigger than the max_amount: invoice: {invoice}, amount: {amount}, amount number: {amount_number}")
        update_widget(page, amount_xref, "{:,.2f}".format(amount_number))

        # Calcular la suma de los importes
        total_invoices_amount += amount_number
    
    update_widget(page, app_config.total_amount_xref_widget, "{:,.2f}".format(total_invoices_amount))
    
    if app_config.bDebug:
        print("Document page updated")

def get_page_from_pdf(doc):
    return doc[app_config.doc_page]

def generate_documents(insurance_pdf_format_file_path, invoices, amounts):
    """
    Generate documents by pairing invoices and amounts with widget xrefs.

    Args:
        invoices (list): List of invoice values.
        amounts (list): List of amount values.
        invoice_widgets (list): List of invoice widgets (xref values).
        amount_widgets (list): List of amount widgets (xref values).

    Returns:
        list: List of documents (lists of modifications) for each set of invoices and amounts.
    """
    document_number = 1
    while invoices and amounts:
        # Abrir el archivo PDF
        doc = fitz.open(insurance_pdf_format_file_path)
        
        # Obtener la primera página del PDF
        page = get_page_from_pdf(doc)

        # Determine the number of widgets available for this iteration
        num_widgets = min(len(app_config.invoice_widgets), len(app_config.amount_widgets))

        # Split the invoices and amounts accordingly
        invoices_subset = invoices[:num_widgets]
        amounts_subset = amounts[:num_widgets]

        # Remove the processed items from the original lists
        invoices = invoices[num_widgets:]
        amounts = amounts[num_widgets:]

        # Generate modifications for the subset of invoices and amounts
        invoice_modifications = update_document(page, invoices_subset, amounts_subset)

        # Nombre del archivo de salida
        prefix_date_sring = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(insurance_pdf_format_file_path).split('.')[0]
        output_pdf = f"./generatedFiles/{prefix_date_sring}_{base_name}_generated_{document_number}.pdf"
        
        # Guardar los cambios en un nuevo archivo PDF
        doc.save(output_pdf)
        document_number += 1
        doc.close()
    
    return document_number

def extract_data_from_invoices(invoices_dir_path):
    invoices = ["17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148"]
    amounts = ["$1598.80", "$298.91", "$1183.50", "$ 869.79"]
    invoices = ["17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148","17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148","17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148"]
    amounts = ["$1598.80", "$298.91", "$1183.50", "$ 869.79","$1598.80", "$298.91", "$1183.50", "$ 869.79","$1598.80", "$298.91", "$1183.50", "$ 869.79", "$1183.50", "$ 869.79"]
    return invoices, amounts

def main():
    # Extract data from invoices
    invoices_dir_path = "./invoices"
    invoices, amounts = extract_data_from_invoices(invoices_dir_path)
    
    # Nombre del archivo de entrada
    insurance_pdf_format_file_path = app_config.insurance_pdf_format_file_path
    
    # Llamar a la función para modificar el PDF
    generate_documents(insurance_pdf_format_file_path, invoices, amounts)
    #modificar_pdf(input_pdf, facturas, importes)

if __name__ == "__main__":
    main()



