class AppConfig:
    """
    Central configuration for the insurance PDF generator.

    Holds PDF form field xrefs, file paths, and runtime flags. All values are
    set at construction time; edit this class to adapt the tool to a different
    PDF template or output location.
    """

    def __init__(self):
        # xref IDs of the invoice-number text fields in the PDF form (one per row)
        self.invoice_widgets = [34, 38, 42, 46, 50, 52, 54, 56, 66, 70, 73, 77]

        # xref IDs of the amount text fields that pair with each invoice_widget
        self.amount_widgets =  [36, 40, 44, 48, 58, 60, 62, 64, 68, 72, 75, 79]

        # xref ID of the grand-total field at the bottom of the form
        self.total_amount_xref_widget = 81

        # Page index (0-based) in the PDF that contains the form
        self.doc_page = 0

        # Upper limit per invoice amount; raises ValueError if exceeded
        self.max_amount = 20000

        # Set to True to enable verbose debug output
        self.bDebug = False

        self.output_directory_path = "./generatedFiles"

        # Path to the editable PDF template used as the base form
        self.insurance_pdf_format_file_path_original = "SolDeReembolsoINTEGRASaludEditable.pdf"
        self.insurance_pdf_format_file_path = "/home/areyes/datos/personal/gastosMedicos/menores/formatos/integra/ARG_SolDeReembolsoINTEGRASalud.pdf"

        # Print the extraction summary table to stdout after parsing XMLs
        self.xml_extractor_print_summary = True

        # Extension used to identify invoice files in the input directory
        self.invoice_extensions = '.xml'

        # Extensions included when building the output ZIP archive
        self.file_extensions_to_zip = ['xml', 'pdf']

        self.zip_base_name = "ArmandoReyesGtz_SolReembolsoGMMenores"
        self.zip_prefix_timestamp_format = "%Y%m%d"
        self.zip_extension = "zip"

        # Timestamp prefix format for individual generated PDF file names
        self.prefix_timestamp_format_default = "%Y%m%d_%H%M%S"


"""
PDF form field map (name → xref) for the ARG_SolDeReembolsoINTEGRASalud template:

| Field    | xref | Role          |
|----------|------|---------------|
| Texto8   |  34  | invoice 1     |
| Texto9   |  36  | amount 1      |
| Texto10  |  38  | invoice 2     |
| Texto11  |  40  | amount 2      |
| Texto12  |  42  | invoice 3     |
| Texto13  |  44  | amount 3      |
| Texto14  |  46  | invoice 4     |
| Texto15  |  48  | amount 4      |
| Texto17  |  50  | invoice 5     |
| Texto18  |  52  | invoice 6     |
| Texto19  |  54  | invoice 7     |
| Texto20  |  56  | invoice 8     |
| Texto22  |  58  | amount 5      |
| Texto23  |  60  | amount 6      |
| Texto24  |  62  | amount 7      |
| Texto25  |  64  | amount 8      |
| Texto28  |  66  | invoice 9     |
| Texto29  |  68  | amount 9      |
| Texto30  |  70  | invoice 10    |
| Texto31  |  72  | amount 10     |
| Texto32  |  73  | invoice 11    |
| Texto33  |  75  | amount 11     |
| Texto34  |  77  | invoice 12    |
| Texto35  |  79  | amount 12     |
| Texto36  |  81  | TOTAL         |
"""
