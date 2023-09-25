import fitz  # PyMuPDF
from datetime import datetime
import os
from app_config import AppConfig
import re
from xml_extractor import extract_xml_data
import argparse

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

def generate_documents(insurance_pdf_format_file_path, output_directory_path, invoices, amounts):
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
        output_pdf = f"{output_directory_path}/{prefix_date_sring}_{base_name}_generated_{document_number}.pdf"
        
        # Guardar los cambios en un nuevo archivo PDF
        doc.save(output_pdf)
        document_number += 1
        doc.close()
    
    return document_number

def extract_data_from_invoices(invoices_dir_path):
    # Call the function to extract data from the XML files
    invoices = []
    amounts = []
    extracted_data = extract_xml_data(invoices_dir_path, app_config.xml_extractor_print_summary) 
    for invoice_data in extracted_data:
        invoices.append(invoice_data['invoice_number'])
        amounts.append(invoice_data['amount'])
    return invoices, amounts

def main():
    parser = argparse.ArgumentParser(description='Generate Insurance refund format based on XML invoices in a directory.')
    parser.add_argument('-d', '--directory', required=True, help='The directory containing XML invoices files.')
    parser.add_argument('-i', '--insurance_file', required=False, help='Insurance file path.', default=app_config.insurance_pdf_format_file_path)
    parser.add_argument('-o', '--output_directory', required=False, help='Output directory path.')
    
    args = parser.parse_args()

    # Verify if the provided directory exists
    if not os.path.exists(args.directory):
        print(f"The provided directory {args.directory} does not exist.")
        return
    
    # Verify if the provided directory exists
    if not os.path.exists(args.insurance_file):
        print(f"The Insurance file path {args.insurance_file} does not exist.")
        return
    
    # Verify if the provided directory exists
    if args.output_directory and not os.path.exists(args.output_directory):
        print(f"The output directory {args.output_directory} does not exist.")
        return

    # By default the output_directory is the same Invoice files path
    if args.directory and args.output_directory == None:
        args.output_directory = args.directory

    # Extract data from invoices
    invoices, amounts = extract_data_from_invoices(args.directory)
    
    # Llamar a la función para modificar el PDF
    generate_documents(args.insurance_file, args.output_directory, invoices, amounts)
    #modificar_pdf(input_pdf, facturas, importes)

if __name__ == "__main__":
    main()



