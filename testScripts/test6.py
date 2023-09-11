factura_widgets = [36, 40, 44, 48, 50, 52, 54, 56, 64, 68, 72]
importe_widgets = [38, 42, 46, 50, 52, 54, 56, 58, 60, 66, 70, 73]

facturas = ["17225", "17224", "E59EF017-0A0A-46F3-800E-7B945D614CB9", "17148"]
importes = ["$1598.80", "$298.91", "$1183.50", "$869.79"]

modificaciones = []

for factura, importe in zip(facturas, importes):
    factura_xref = factura_widgets.pop(0)
    importe_xref = importe_widgets.pop(0)
    
    mod_factura = {"xref": factura_xref, "value": factura}
    mod_importe = {"xref": importe_xref, "value": importe}
    
    modificaciones.extend([mod_factura, mod_importe])

print(modificaciones)
