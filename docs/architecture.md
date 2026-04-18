# Arquitectura y flujo de datos

## Visión general

La aplicación sigue un pipeline lineal de tres etapas:

```
Facturas XML  →  Extracción de datos  →  Generación de PDF  →  Empaquetado ZIP
```

Cada etapa es independiente y está encapsulada en su propio módulo o función.

---

## Módulos

### `app_config.py` — Configuración

Clase `AppConfig` que centraliza todos los parámetros de la aplicación.  Se instancia una sola vez en cada módulo como variable de módulo (`app_config = AppConfig()`).

Contiene:
- Listas de xrefs de los campos del formulario PDF
- Rutas de archivos (plantilla PDF, directorio de salida)
- Límites de validación (`max_amount`)
- Flags de comportamiento (`bDebug`, `xml_extractor_print_summary`)
- Formatos de nombre y extensiones de archivo

### `xml_extractor.py` — Extracción de facturas

Función principal: `extract_xml_data(directory, print_result)`

Parsea facturas electrónicas en formato **CFDI v4** (SAT México).  Por cada archivo XML válido extrae:

| Campo | Atributo XML | Descripción |
|---|---|---|
| `invoice_number` | `TimbreFiscalDigital/@UUID` | Folio fiscal único |
| `amount` | `Comprobante/@Total` | Monto total de la factura |

Los namespaces XML utilizados son:
```
cfdi → http://www.sat.gob.mx/cfd/4
tfd  → http://www.sat.gob.mx/TimbreFiscalDigital
```

Archivos que no se pueden parsear se registran con estado `Error` en el resumen, sin interrumpir el proceso.

### `generateInsurancePDF.py` — Motor principal

Punto de entrada de la aplicación.  Orquesta el pipeline completo.

#### Funciones

| Función | Responsabilidad |
|---|---|
| `extract_data_from_invoices(dir)` | Wrapper sobre `extract_xml_data`; retorna dos listas paralelas |
| `generate_documents(...)` | Loop principal; genera un PDF por cada bloque de ≤12 facturas |
| `update_document(page, invoices, amounts, adjustment)` | Rellena los campos de una página del formulario |
| `update_widget(page, xref, value)` | Escribe un valor en un campo individual del PDF |
| `convert_string_to_number(s)` | Limpia y convierte strings de monto a float |
| `identify_files_to_zip(dir)` | Lista archivos XML y PDF del directorio de entrada |
| `zip_invoices_insurance_file(...)` | Crea el archivo ZIP final |
| `get_file_name_with_timestamp(...)` | Construye rutas con prefijo de timestamp |

---

## Flujo de datos detallado

```
1. main()
   │
   ├─ Valida argumentos CLI (-d, -i, -o, -a)
   │
   ├─ extract_data_from_invoices(directory)
   │   └─ extract_xml_data(directory)          # lee todos los .xml
   │       └─ retorna [{invoice_number, amount}, ...]
   │           → invoices = [UUID1, UUID2, ...]
   │           → amounts  = ["1500.00", "800.00", ...]
   │
   ├─ generate_documents(pdf_template, output_dir, invoices, amounts, adjustment)
   │   │
   │   └─ while invoices:                      # itera en bloques de 12
   │       ├─ fitz.open(pdf_template)          # abre plantilla virgen
   │       ├─ update_document(page, subset, adjustment)
   │       │   ├─ update_widget(xref_invoice, UUID)
   │       │   ├─ update_widget(xref_amount, "1,500.00")
   │       │   └─ update_widget(xref_total, suma + adjustment)
   │       └─ doc.save(timestamped_path)       # guarda PDF relleno
   │
   └─ zip_invoices_insurance_file(dir, pdfs, zip_path)
       ├─ identify_files_to_zip(dir)           # XML + PDF del directorio
       └─ ZipFile.write(files)                 # empaqueta todo
```

---

## Estructura del formulario PDF

El formulario `ARG_SolDeReembolsoINTEGRASalud.pdf` tiene capacidad para **12 facturas por página**.  Los campos se identifican internamente por su número `xref` dentro del PDF:

| Fila | xref Número de factura | xref Importe |
|------|----------------------|--------------|
| 1    | 34                   | 36           |
| 2    | 38                   | 40           |
| 3    | 42                   | 44           |
| 4    | 46                   | 48           |
| 5    | 50                   | 58           |
| 6    | 52                   | 60           |
| 7    | 54                   | 62           |
| 8    | 56                   | 64           |
| 9    | 66                   | 68           |
| 10   | 70                   | 72           |
| 11   | 73                   | 75           |
| 12   | 77                   | 79           |
| **TOTAL** | —            | **81**       |

Si se tienen más de 12 facturas, se genera un segundo PDF con las restantes (y así sucesivamente).

---

## Ajuste al total (`--adjustment`)

El argumento `-a` / `--adjustment` permite modificar el total calculado antes de escribirlo en el campo TOTAL del formulario.  Es útil cuando existe una diferencia conocida entre la suma de facturas y el monto a reclamar (p. ej. copagos, deducciones, redondeos).

```
total_en_pdf = suma(importes) + adjustment
```

El ajuste se aplica a **todos** los PDFs generados cuando hay más de 12 facturas.

---

## Manejo de múltiples páginas

Cuando el número de facturas supera la capacidad del formulario (12), `generate_documents` divide la lista en bloques y genera un archivo PDF separado por bloque:

```
20241017_143022_ARG_SolDeReembolsoINTEGRASalud_generated_1.pdf  ← facturas 1–12
20241017_143022_ARG_SolDeReembolsoINTEGRASalud_generated_2.pdf  ← facturas 13–24
...
```

Todos los PDFs generados, junto con los XML originales, se incluyen en el ZIP final.

---

## Dependencias externas

| Librería | Versión | Uso |
|---|---|---|
| [PyMuPDF](https://pymupdf.readthedocs.io/) | 1.23.3 | Apertura, edición y guardado del PDF |
| xmltodict | 0.13.0 | Auxiliar de parseo XML |
| xml.etree.ElementTree | stdlib | Parseo principal de CFDI XML |
| argparse | stdlib | Interfaz de línea de comandos |
| zipfile | stdlib | Creación del archivo ZIP |
