import json
import statistics  # statistics.correlation requiere Python 3.10 o superior
import tempfile
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  

from fuentes import FuenteDatos, FuenteCSV, FuenteJSON
from modelo import Paciente
from pipeline import convertir_numero, validar_registro, limpiar, generar_reporte, guardar_csv

RUTA_CSV = RAIZ / "data" / "mediciones.csv"
RUTA_JSON = RAIZ / "data" / "mediciones.json"

def probar(condicion, mensaje):
    assert condicion, mensaje


def debe_fallar(funcion, mensaje, error=ValueError):
    try:
        funcion()
    except error:
        return
    probar(False, mensaje)


carpeta_temporal = Path(tempfile.mkdtemp())

# --- 1. Caso normal ---
registros_csv = FuenteCSV().cargar(RUTA_CSV)
registros_json = FuenteJSON().cargar(RUTA_JSON)
probar(len(registros_csv) == 58, "FuenteCSV debe leer los 58 registros")
probar(len(registros_json) == 58, "FuenteJSON debe leer los 58 registros")
probar(isinstance(registros_csv[0], dict), "cargar() debe devolver una lista de diccionarios")
probar(set(registros_csv[0]) == {"codigo", "edad", "imc", "presion_sistolica", "grupo"},
       "Las claves de cada registro deben ser los nombres de los campos")

validos, rechazos = limpiar(registros_csv)
probar(len(validos) == 50, f"Se esperaban 50 registros válidos y se obtuvieron {len(validos)}")
probar(len(rechazos) == 8, f"Se esperaban 8 rechazos y se obtuvieron {len(rechazos)}")
probar(all(isinstance(p, Paciente) for p in validos), "limpiar() debe devolver objetos Paciente")
probar(all(isinstance(p.edad, float) and isinstance(p.presion, float) for p in validos),
       "Los atributos numéricos de Paciente deben ser float")
probar(all(r["motivo"] for r in rechazos), "Cada rechazo debe indicar un motivo")
probar(validar_registro({"codigo": "PAC-001", "edad": "21", "imc": "28.8",
                         "presion_sistolica": "97", "grupo": "B"}) == [],
       "Un registro correcto no debe tener motivos de rechazo")

# --- 2. Entradas inválidas y casos límite ---
probar(convertir_numero("28.8") == 28.8 and convertir_numero(28.8) == 28.8,
       "convertir_numero debe aceptar texto y números")
probar(convertir_numero("") is None and convertir_numero(None) is None,
       "Un valor faltante debe convertirse en None")
debe_fallar(lambda: convertir_numero("abc"), "convertir_numero('abc') debe lanzar ValueError")

base = {"codigo": "PAC-001", "edad": "40", "imc": "25", "presion_sistolica": "120", "grupo": "A"}
for codigo in ["PAC01", "PAC-0001", "pac-001", "XPAC-001"]:
    probar(validar_registro({**base, "codigo": codigo}) != [], f"El código {codigo} debe rechazarse")
probar(validar_registro({**base, "edad": "-45"}) != [], "Una edad negativa debe rechazarse")
probar(validar_registro({**base, "presion_sistolica": None}) != [], "Una presión faltante debe rechazarse")
probar(validar_registro({**base, "grupo": "C"}) != [], "Un grupo distinto de A y B debe rechazarse")
probar(validar_registro({**base, "imc": "abc"}) != [], "Un IMC no numérico debe rechazarse")

codigos_rechazados = [r["codigo"] for r in rechazos]
probar("PAC01" in codigos_rechazados, "El código PAC01 debe figurar entre los rechazos")
probar([r["fila"] for r in rechazos if r["codigo"] == "PAC01"] == [6],
       "El rechazo de PAC01 debe indicar la fila 6 (contando desde 1)")
probar("PAC-012" in codigos_rechazados, "La segunda aparición de PAC-012 debe rechazarse por duplicada")
paciente_12 = [p for p in validos if p.codigo == "PAC-012"]
probar(len(paciente_12) == 1 and paciente_12[0].presion == 123.0,
       "Ante un código duplicado debe conservarse la primera aparición")

debe_fallar(lambda: FuenteCSV().cargar("no_existe.csv"),
            "Un archivo inexistente debe lanzar FileNotFoundError", FileNotFoundError)
ruta_no_lista = carpeta_temporal / "no_lista.json"
ruta_no_lista.write_text(json.dumps({"codigo": "PAC-001"}), encoding="utf-8")
debe_fallar(lambda: FuenteJSON().cargar(ruta_no_lista),
            "FuenteJSON debe lanzar ValueError si el contenido no es una lista")
debe_fallar(lambda: FuenteDatos(), "FuenteDatos debe ser abstracta", TypeError)

for edad, franja in [(18, "18-39"), (39, "18-39"), (40, "40-59"), (59, "40-59"), (60, "60+")]:
    probar(Paciente("PAC-001", float(edad), 25.0, 120.0, "A").franja_etaria() == franja,
           f"La edad {edad} corresponde a la franja {franja}")
probar(Paciente("PAC-001", 50.0, 25.0, 140.0, "A").es_hipertenso(), "PAS = 140 debe considerarse hipertensión")
probar(not Paciente("PAC-001", 50.0, 25.0, 139.0, "A").es_hipertenso(), "PAS = 139 no es hipertensión")
probar("PAC-001" in str(Paciente("PAC-001", 50.0, 25.0, 120.0, "A")), "__str__ debe mostrar el código")

try:
    reporte_vacio = generar_reporte([])
except ZeroDivisionError:
    probar(False, "generar_reporte([]) no debe dividir por cero")
probar(all(fila["cantidad"] == 0 for fila in reporte_vacio), "Un reporte vacío no debe contar pacientes")

# --- 3. Propiedades del resultado ---
probar(len(validos) + len(rechazos) == len(registros_csv),
       "Ningún registro puede perderse: válidos + rechazados = leídos")
probar(len({p.codigo for p in validos}) == len(validos), "No debe haber códigos repetidos entre los válidos")

validos_json, rechazos_json = limpiar(registros_json)
reporte_csv = generar_reporte(validos)
probar(generar_reporte(validos_json) == reporte_csv, "Las lecturas CSV y JSON deben producir el mismo reporte")
probar([r["motivo"] for r in rechazos_json] == [r["motivo"] for r in rechazos],
       "Las lecturas CSV y JSON deben producir los mismos rechazos")

probar([fila["grupo"] for fila in reporte_csv] == ["A", "B"], "El reporte debe tener una fila por grupo, ordenadas")
fila_a, fila_b = reporte_csv
probar(fila_a["cantidad"] == 27 and fila_b["cantidad"] == 23, "El grupo A debe tener 27 pacientes y el B, 23")
probar(abs(fila_a["presion_media"] - 127.26) < 0.01, "La PAS media del grupo A debe ser 127.26")
probar(abs(fila_b["presion_media"] - 118.61) < 0.01, "La PAS media del grupo B debe ser 118.61")
probar(abs(fila_a["proporcion_hipertensos"] - 5 / 27) < 0.001, "La proporción de hipertensos del grupo A debe ser 5/27")

r = statistics.correlation([p.edad for p in validos], [p.presion for p in validos])
probar(abs(r - 0.794) < 0.001, f"r(edad, PAS) debe ser 0.794 (Anexo A del TP de EDA) y se obtuvo {r:.4f}")

ruta_reporte = carpeta_temporal / "reporte.csv"
guardar_csv(reporte_csv, ruta_reporte)
releido = FuenteCSV().cargar(ruta_reporte)
probar(len(releido) == 2 and releido[0]["grupo"] == "A", "guardar_csv debe escribir un CSV legible por FuenteCSV")

print("Todas las pruebas pasaron.")