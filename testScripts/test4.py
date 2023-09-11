import fitz  # PyMuPDF
from datetime import datetime

def modificar_pdf(input_pdf, output_pdf, facturas, importes):
    # Abrir el archivo PDF
    doc = fitz.open(input_pdf)
    
    # Obtener el primer formulario del PDF
    formulario = doc[0]
    
    # Iterar sobre las facturas e importes y actualizar los campos correspondientes
    for i in range(len(facturas)):
        factura = facturas[i]
        importe = importes[i]
        
        # Actualizar campos de factura e importe
        formulario.set_text("Texto" + str(9 + i*2), factura)
        formulario.set_text("Texto" + str(10 + i*2), importe)
    
    # Calcular la suma de los importes
    suma_importes = sum([float(importe[1:].replace(',', '')) for importe in importes])
    
    # Actualizar el campo de suma
    formulario.set_text("Texto33", f"${suma_importes:,.2f}")
    
    # Guardar los cambios en un nuevo archivo PDF
    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    # Datos de entrada
    facturas = ["17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148"]
    importes = ["$1598.80", "$298.91", "$1183.50", "$869.79"]
    
    # Nombre del archivo de entrada y salida
    input_pdf = "ARG_SolDeReembolsoINTEGRASalud.pdf"
    fecha = datetime.now().strftime("%Y%m%d")
    output_pdf = f"{fecha}_modified.pdf"
    
    # Llamar a la función para modificar el PDF
    modificar_pdf(input_pdf, output_pdf, facturas, importes)
