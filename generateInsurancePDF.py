import fitz  # PyMuPDF
from datetime import datetime
import os
from app_config import AppConfig
import re
from xml_extractor import extract_xml_data
import argparse
import zipfile

app_config = AppConfig()


def convert_string_to_number(input_string):
    """
    Strip non-numeric characters from *input_string* and return it as a float.

    Handles strings that come directly from XML attributes, which may include
    currency symbols, commas, or spaces (e.g. '$1,500.00').

    Args:
        input_string (str): Raw amount string from the invoice XML.

    Returns:
        float | None: Parsed number, or None if the string cannot be converted.
    """
    cleaned_string = re.sub(r'[^\d.]', '', input_string)
    try:
        number = float(cleaned_string)
        if app_config.bDebug:
            print(f"input_string: {input_string}, cleaned_string: {cleaned_string}, number: {number}")
        return number
    except ValueError:
        return None


def update_widget(page, wid_xref, value):
    """
    Write *value* into the PDF form field identified by *wid_xref*.

    Silently skips the operation when the xref does not resolve to a widget on
    the given page.  None values are coerced to an empty string so the field is
    cleared rather than left with stale content.

    Args:
        page (fitz.Page): The PDF page that contains the form field.
        wid_xref (int): Internal xref number of the target widget.
        value (str | None): Text to write into the field.
    """
    wid_aux = page.load_widget(wid_xref)
    if wid_aux is not None:
        wid_aux.field_value = str(value) if value is not None else ""
        wid_aux.update()
        if app_config.bDebug:
            print(f"Widget updated, name: {wid_aux.field_name}, xref: {wid_aux.xref}, value: {wid_aux.field_value}")


def update_document(page, invoices, amounts, adjustment=0):
    """
    Fill the invoice rows and total field on *page* with the supplied data.

    Iterates over (invoice, amount) pairs and writes each value into the
    corresponding form field using the xref lists from AppConfig.  After all
    rows are filled, the grand total is computed as the sum of all amounts plus
    the optional *adjustment* and written to the total field.

    Args:
        page (fitz.Page): PDF page containing the INTEGRA reimbursement form.
        invoices (list[str]): Invoice UUID strings, one per row.
        amounts (list[str]): Raw amount strings matching each invoice.
        adjustment (float): Value added to the computed total before writing it
            to the PDF.  Use a negative number to subtract.

    Raises:
        ValueError: If an amount cannot be parsed as a number, or if it
            exceeds AppConfig.max_amount.
    """
    total_invoices_amount = 0
    for invoice, amount, invoice_xref, amount_xref in zip(
        invoices, amounts, app_config.invoice_widgets, app_config.amount_widgets
    ):
        update_widget(page, invoice_xref, invoice)

        amount_number = convert_string_to_number(amount)
        if amount_number is None:
            raise ValueError(
                f"The amount must be a number: invoice: {invoice}, amount: {amount}, amount number: {amount_number}"
            )
        if amount_number >= app_config.max_amount:
            raise ValueError(
                f"The amount is bigger than the max_amount: invoice: {invoice}, amount: {amount}, amount number: {amount_number}"
            )
        update_widget(page, amount_xref, "{:,.2f}".format(amount_number))
        total_invoices_amount += amount_number

    total_with_adjustment = total_invoices_amount + adjustment
    update_widget(page, app_config.total_amount_xref_widget, "{:,.2f}".format(total_with_adjustment))

    if app_config.bDebug:
        if adjustment != 0:
            print(f"Total invoices: {total_invoices_amount:.2f}, adjustment: {adjustment:.2f}, final total: {total_with_adjustment:.2f}")
        print("Document page updated")


def get_page_from_pdf(doc):
    """Return the form page from *doc* as defined in AppConfig.doc_page."""
    return doc[app_config.doc_page]


def get_file_name_with_timestamp(
    output_directory_path,
    base_file_name,
    sufix,
    extension,
    bool_add_prefix_timestamp,
    prefix_timestamp_format=app_config.prefix_timestamp_format_default,
):
    """
    Build a file path with an optional timestamp prefix and suffix.

    Args:
        output_directory_path (str): Directory where the file will be saved.
        base_file_name (str): Core name of the file (without extension).
        sufix (str | None): String appended after the base name (None to omit).
        extension (str): File extension without leading dot.
        bool_add_prefix_timestamp (bool): Prepend a timestamp when True.
        prefix_timestamp_format (str): strftime format for the timestamp prefix.

    Returns:
        str: Full absolute file path.
    """
    prefix_date_string = ""
    if bool_add_prefix_timestamp:
        prefix_date_string = datetime.now().strftime(prefix_timestamp_format)
    if sufix:
        sufix = "_" + sufix
    output_file_path = os.path.join(
        output_directory_path, f"{prefix_date_string}_{base_file_name}{sufix}.{extension}"
    )
    return output_file_path


def generate_documents(insurance_pdf_format_file_path, output_directory_path, invoices, amounts, adjustment=0):
    """
    Produce one or more filled PDF reimbursement forms from *invoices* and *amounts*.

    The PDF template supports a fixed number of rows (determined by the length
    of AppConfig.invoice_widgets).  When more invoices are provided than fit on
    a single form, the function iterates and generates additional numbered PDFs
    until all invoices are processed.

    Args:
        insurance_pdf_format_file_path (str): Path to the editable PDF template.
        output_directory_path (str): Directory where generated PDFs are saved.
        invoices (list[str]): All invoice UUIDs to include.
        amounts (list[str]): Corresponding amounts for each invoice.
        adjustment (float): Offset applied to the total on every generated page.

    Returns:
        list[str]: Paths to all generated PDF files.
    """
    insurance_generated_files = []
    document_number = 1

    while invoices and amounts:
        doc = fitz.open(insurance_pdf_format_file_path)
        page = get_page_from_pdf(doc)

        num_widgets = min(len(app_config.invoice_widgets), len(app_config.amount_widgets))
        invoices_subset = invoices[:num_widgets]
        amounts_subset = amounts[:num_widgets]
        invoices = invoices[num_widgets:]
        amounts = amounts[num_widgets:]

        update_document(page, invoices_subset, amounts_subset, adjustment)

        output_file_path = get_file_name_with_timestamp(
            output_directory_path,
            os.path.basename(insurance_pdf_format_file_path).split('.')[0],
            f"generated_{document_number}",
            "pdf",
            True,
        )
        doc.save(output_file_path)
        document_number += 1
        insurance_generated_files.append(output_file_path)
        doc.close()

    return insurance_generated_files


def extract_data_from_invoices(invoices_dir_path):
    """
    Scan *invoices_dir_path* for XML files and return two parallel lists.

    Thin wrapper around xml_extractor.extract_xml_data that unpacks the result
    into separate invoice-number and amount lists for use by generate_documents.

    Args:
        invoices_dir_path (str): Directory containing CFDI XML invoice files.

    Returns:
        tuple[list[str], list[str]]: (invoices, amounts) parallel lists.
    """
    invoices = []
    amounts = []
    extracted_data = extract_xml_data(invoices_dir_path, app_config.xml_extractor_print_summary)
    for invoice_data in extracted_data:
        invoices.append(invoice_data['invoice_number'])
        amounts.append(invoice_data['amount'])
    return invoices, amounts


def identify_files_to_zip(invoices_dir):
    """
    List all files in *invoices_dir* whose extension is in AppConfig.file_extensions_to_zip.

    Only the immediate directory is scanned (non-recursive) to avoid pulling in
    unrelated files from subdirectories.

    Args:
        invoices_dir (str): Path to the invoice directory.

    Returns:
        list[str]: Absolute paths of the files to include in the ZIP.
    """
    if app_config.bDebug:
        print("identify_files_to_zip -> invoices dir:", invoices_dir)

    file_list = []
    for file_name in os.listdir(invoices_dir):
        _, extension = os.path.splitext(file_name)
        extension = extension.lower().lstrip('.')
        if extension in app_config.file_extensions_to_zip:
            file_list.append(os.path.join(invoices_dir, file_name))

    if app_config.bDebug:
        print("identify_files_to_zip -> file list in dir:", file_list)

    return file_list


def zip_invoices_insurance_file(invoices_dir, insurance_generated_files, zip_file_path):
    """
    Create a ZIP archive containing all invoices and the generated PDF forms.

    Collects XML and PDF files from *invoices_dir* via identify_files_to_zip,
    then appends any generated PDFs that are stored outside that directory.
    All files are stored flat (no subdirectory structure) inside the archive.

    Args:
        invoices_dir (str): Directory with the original invoice files.
        insurance_generated_files (list[str]): Paths to the generated PDFs.
        zip_file_path (str): Destination path for the output ZIP file.

    Returns:
        bool: True when the archive is created successfully.
    """
    files_to_zip = identify_files_to_zip(invoices_dir)

    for insurance_generated_file in insurance_generated_files:
        if insurance_generated_file not in files_to_zip:
            files_to_zip.append(insurance_generated_file)

    if app_config.bDebug:
        print("zip_invoices_insurance_file -> files to zip:", files_to_zip)

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate Insurance refund format based on XML invoices in a directory.'
    )
    parser.add_argument('-d', '--directory', required=True,
                        help='The directory containing XML invoices files.')
    parser.add_argument('-i', '--insurance_file', required=False,
                        help='Insurance file path.',
                        default=app_config.insurance_pdf_format_file_path)
    parser.add_argument('-o', '--output_directory', required=False,
                        help='Output directory path.')
    parser.add_argument('-a', '--adjustment', required=False, type=float, default=0.0,
                        help='Amount to add or subtract from the total (e.g. 150.00 or -50.00).')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"The provided directory {args.directory} does not exist.")
        return

    if not os.path.exists(args.insurance_file):
        print(f"The Insurance file path {args.insurance_file} does not exist.")
        return

    if args.output_directory and not os.path.exists(args.output_directory):
        print(f"The output directory {args.output_directory} does not exist.")
        return

    if args.directory and args.output_directory is None:
        args.output_directory = args.directory

    print("Starts at: ", datetime.now())
    print(
        "main -> executing arguments:"
        f"\n\tInvoices directory: {args.directory}"
        f"\n\tInsurance file:     {args.insurance_file}"
        f"\n\tOutput directory:   {args.output_directory}"
        f"\n\tAdjustment:         {args.adjustment}\n"
    )

    invoices, amounts = extract_data_from_invoices(args.directory)

    insurance_generated_files = generate_documents(
        args.insurance_file, args.output_directory, invoices, amounts, args.adjustment
    )

    if len(insurance_generated_files) > 0:
        zip_file_path = get_file_name_with_timestamp(
            args.output_directory,
            app_config.zip_base_name,
            None,
            app_config.zip_extension,
            True,
            app_config.zip_prefix_timestamp_format,
        )
        is_zip_generated = zip_invoices_insurance_file(
            args.directory, insurance_generated_files, zip_file_path
        )
        if is_zip_generated:
            print("Zip file name created:", zip_file_path, "\n")
            print("sending mail\n")

    print("Ends at: ", datetime.now())


if __name__ == "__main__":
    main()
