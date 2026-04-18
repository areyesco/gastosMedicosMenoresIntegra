import os
from app_config import AppConfig
import xml.etree.ElementTree as ET

app_config = AppConfig()

# SAT CFDI v4 namespaces required to locate the UUID inside the XML complement
namespaces = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
}

def extract_xml_data(directory, print_result=False):
    """
    Parse all CFDI XML invoices in *directory* and return their UUID and total.

    Iterates every .xml file, extracts the fiscal UUID from the
    TimbreFiscalDigital complement and the Total attribute from the root
    Comprobante element.  Files that fail to parse are recorded in the summary
    but do not abort the process.

    Args:
        directory (str): Path to the folder containing the XML invoice files.
        print_result (bool): When True, prints a markdown summary table to stdout.

    Returns:
        list[dict]: Each entry has keys 'invoice_number' (UUID str) and
                    'amount' (str as it appears in the XML, e.g. '1500.00').
    """
    extracted_data = []
    summary = []

    for filename in os.listdir(directory):
        if not filename.lower().endswith('.xml'):
            continue

        file_path = os.path.join(directory, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            invoice_number = root.find(
                ".//cfdi:Complemento/tfd:TimbreFiscalDigital", namespaces
            ).get('UUID')
            amount = root.get('Total')

            extracted_data.append({
                'invoice_number': invoice_number,
                'amount': amount
            })
            summary.append({
                'Filename': filename,
                'Status': 'Success',
                'Invoice Number': invoice_number,
                'Amount': amount,
                'Error': ''
            })

        except Exception as e:
            summary.append({
                'Filename': filename,
                'Status': 'Error',
                'Invoice Number': '',
                'Amount': '',
                'Error': str(e)
            })

    if print_result:
        print("Extracted data from invoices files")
        print("| Filename | Status | Invoice Number | Amount | Error |")
        print("|----------|--------|----------------|--------|-------|")
        for entry in summary:
            print(f"| {entry['Filename']} | {entry['Status']} | {entry['Invoice Number']} | {entry['Amount']} | {entry['Error']} |")
        print("")

    return extracted_data


if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    data = extract_xml_data(directory, app_config.xml_extractor_print_summary)
    if app_config.bDebug:
        print(data)
