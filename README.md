# Gastos Médicos Menores INTEGRA

Herramienta de línea de comandos que automatiza la generación del formato **Solicitud de Reembolso INTEGRA Salud** a partir de facturas electrónicas (CFDI XML).  Lee los XML, extrae el UUID y el total de cada factura, rellena el formulario PDF editable y empaqueta todo en un ZIP listo para enviar.

---

## Requisitos

- Python 3.10+
- Entorno virtual con las dependencias instaladas (ver [Instalación](#instalación))
- Plantilla PDF editable `ARG_SolDeReembolsoINTEGRASalud.pdf`

### Dependencias Python

| Paquete      | Versión  | Uso                          |
|--------------|----------|------------------------------|
| PyMuPDF      | 1.23.3   | Manipulación del formulario PDF |
| PyMuPDFb     | 1.23.3   | Binarios de soporte de PyMuPDF |
| xmltodict    | 0.13.0   | Parseo auxiliar de XML       |

---

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd gastosMedicosMenoresIntegra

# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Uso

```bash
python3 generateInsurancePDF.py -d <directorio_facturas> [opciones]
```

### Argumentos

| Argumento              | Obligatorio | Descripción |
|------------------------|-------------|-------------|
| `-d`, `--directory`    | Sí          | Directorio que contiene los archivos XML de las facturas |
| `-i`, `--insurance_file` | No        | Ruta a la plantilla PDF editable (usa la ruta configurada en `AppConfig` por defecto) |
| `-o`, `--output_directory` | No      | Directorio de salida para los archivos generados (por defecto: mismo que `-d`) |
| `-a`, `--adjustment`   | No          | Monto a sumar o restar del total calculado (positivo o negativo, p. ej. `150.00` o `-50.00`) |

### Ejemplos

```bash
# Caso básico: facturas en /tmp/facturas
python3 generateInsurancePDF.py -d /tmp/facturas

# Con ajuste positivo al total
python3 generateInsurancePDF.py -d /tmp/facturas -a 150.00

# Con ajuste negativo al total
python3 generateInsurancePDF.py -d /tmp/facturas -a -50.00

# Especificando plantilla y directorio de salida
python3 generateInsurancePDF.py \
    -d /tmp/facturas \
    -i /ruta/a/plantilla.pdf \
    -o /tmp/salida \
    -a 200.00
```

### Alias de shell (`gmm`)

El alias `gmm` en `~/.bash_aliases` simplifica la ejecución:

```bash
# Uso básico
gmm /ruta/facturas

# Con ajuste
gmm /ruta/facturas 150.00
gmm /ruta/facturas -50.00
```

---

## Salida

Por cada ejecución se genera:

1. **PDF(s) rellenos** — uno por cada 12 facturas (capacidad del formulario).  
   Nombre: `YYYYMMDD_HHMMSS_<nombre_plantilla>_generated_N.pdf`

2. **Archivo ZIP** — contiene todos los XML del directorio de entrada más los PDFs generados.  
   Nombre: `YYYYMMDD_ArmandoReyesGtz_SolReembolsoGMMenores.zip`

---

## Configuración

Los parámetros de configuración se centralizan en `app_config.py`:

| Atributo | Descripción |
|---|---|
| `insurance_pdf_format_file_path` | Ruta a la plantilla PDF |
| `output_directory_path` | Directorio de salida por defecto |
| `max_amount` | Monto máximo por factura (20,000) |
| `zip_base_name` | Nombre base del ZIP generado |
| `bDebug` | Activar salida de depuración en consola |

Ver [docs/architecture.md](docs/architecture.md) para la documentación técnica completa.

---

## Estructura del proyecto

```
gastosMedicosMenoresIntegra/
├── generateInsurancePDF.py   # Script principal (punto de entrada)
├── xml_extractor.py          # Extracción de datos de facturas CFDI XML
├── app_config.py             # Configuración centralizada
├── requirements.txt          # Dependencias Python
├── generatedFiles/           # Directorio de salida (PDFs y ZIPs)
└── docs/
    └── architecture.md       # Documentación técnica y flujo de datos
```
