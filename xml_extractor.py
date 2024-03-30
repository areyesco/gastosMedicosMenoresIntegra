import os
from app_config import AppConfig
import xml.etree.ElementTree as ET

# Load configuration
app_config = AppConfig()

# Define the namespaces used in the XML files
namespaces = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
}

def extract_xml_data(directory, print_result=False):
    """
    Extract data from all XML files in the specified directory.
    
    :param directory: The directory containing the XML files.
    :return: A list of dictionaries containing extracted data.
    """
    # Initialize a list to store extracted data
    extracted_data = []
    
    # Initialize a list to store summary information
    summary = []
    
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the file is an XML file
        if filename.lower().endswith('.xml'):
            # Construct the full file path
            file_path = os.path.join(directory, filename)
            
            try:
                # Parse the XML file
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract data from the XML file
                invoice_number = root.find(".//cfdi:Complemento/tfd:TimbreFiscalDigital", namespaces).get('UUID')
                amount = root.get('Total')
                
                # Append the extracted data to the list
                extracted_data.append({
                    'invoice_number': invoice_number,
                    'amount': amount
                })
                
                # Append success information to the summary
                summary.append({
                    'Filename': filename,
                    'Status': 'Success',
                    'Invoice Number': invoice_number,
                    'Amount': amount,
                    'Error': ''
                })
                
            except Exception as e:
                # If an error occurs, append the error information to the summary
                summary.append({
                    'Filename': filename,
                    'Status': 'Error',
                    'Invoice Number': '',
                    'Amount': '',
                    'Error': str(e)
                })
                
    # Print the summary in a markdown table
    if print_result:
        print("Extracted data from invoices files")
        print("| Filename | Status | Invoice Number | Amount | Error |")
        print("|----------|--------|----------------|--------|-------|")
        for entry in summary:
            print(f"| {entry['Filename']} | {entry['Status']} | {entry['Invoice Number']} | {entry['Amount']} | {entry['Error']} |")
        print("")
    # Return the extracted data
    return extracted_data

# Example of calling the function from another file
if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    data = extract_xml_data(directory, app_config.xml_extractor_print_summary)
    if app_config.bDebug:
        print(data)
