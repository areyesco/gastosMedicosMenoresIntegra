import fitz  # PyMuPDF
from datetime import datetime
import os

def modificar_pdf(input_pdf, facturas, importes):
    # Abrir el archivo PDF
    doc = fitz.open(input_pdf)
    
    # Obtener la primera página del PDF
    page = doc[0]
    
    # Iterar sobre las facturas e importes y actualizar los campos correspondientes
    for i in range(len(facturas)):
        factura = facturas[i]
        importe = importes[i]
        
        # Buscar y actualizar campos de factura e importe
        field_factura = page.widget_get_by_name("Texto" + str(9 + i*2))
        field_importe = page.widget_get_by_name("Texto" + str(10 + i*2))
        
        if field_factura:
            field_factura.field_value = factura
            field_factura.update()
        
        if field_importe:
            field_importe.field_value = importe
            field_importe.update()
    
    # Calcular la suma de los importes
    suma_importes = sum([float(importe[1:].replace(',', '')) for importe in importes])
    
    # Actualizar el campo de suma
    field_suma = page.widget_get_by_name("Texto33")
    if field_suma:
        field_suma.field_value = f"${suma_importes:,.2f}"
        field_suma.update()
    
    # Nombre del archivo de salida
    fecha = datetime.now().strftime("%Y%m%d")
    base_name = os.path.basename(input_pdf).split('.')[0]
    output_pdf = f"{fecha}_{base_name}_modified.pdf"
    
    # Guardar los cambios en un nuevo archivo PDF
    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    # Datos de entrada
    facturas = ["17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148"]
    importes = ["$1598.80", "$298.91", "$1183.50", "$869.79"]
    
    # Nombre del archivo de entrada
    input_pdf = "ARG_SolDeReembolsoINTEGRASalud.pdf"
    
    # Llamar a la función para modificar el PDF
    modificar_pdf(input_pdf, facturas, importes)
