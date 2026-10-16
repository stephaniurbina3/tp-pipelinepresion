
import csv
import re

from modelo import Paciente

PATRON_CODIGO = re.compile(r"PAC-\d{3}")

RANGOS = {
    "edad": (18, 100),
    "imc": (12, 60),
    "presion_sistolica": (70, 250),
}
GRUPOS_VALIDOS = ("A", "B")
NOMBRES_CAMPOS = {
    "edad": "edad",
    "imc": "imc",
    "presion_sistolica": "presión sistólica",
}


def convertir_numero(valor):
    if valor is None or (isinstance(valor, str) and valor.strip() == ""):
        return None
    return float(valor)


def validar_registro(registro):
    motivos = []

    codigo = registro.get("codigo")
    if not isinstance(codigo, str) or PATRON_CODIGO.fullmatch(codigo) is None:
        motivos.append("código con formato inválido")

    for campo, (minimo, maximo) in RANGOS.items():
        nombre = NOMBRES_CAMPOS[campo]
        try:
            numero = convertir_numero(registro.get(campo))
        except (ValueError, TypeError):
            motivos.append(f"{nombre} no numérico")
            continue
        if numero is None:
            motivos.append(f"{nombre} faltante")
        elif not minimo <= numero <= maximo:
            motivos.append(f"{nombre} fuera de rango ({minimo}-{maximo})")

    if registro.get("grupo") not in GRUPOS_VALIDOS:
        motivos.append("grupo inválido")

    return motivos


def limpiar(registros):
    validos = []
    rechazos = []
    codigos_aceptados = set()

    for fila, registro in enumerate(registros, start=1):
        motivos = validar_registro(registro)
        if not motivos and registro["codigo"] in codigos_aceptados:
            motivos.append("código duplicado")  

        if motivos:
            rechazos.append({
                "fila": fila,
                "codigo": registro.get("codigo"),
                "motivo": "; ".join(motivos),
            })
        else:
            codigos_aceptados.add(registro["codigo"])
            validos.append(Paciente(
                registro["codigo"],
                float(registro["edad"]),
                float(registro["imc"]),
                float(registro["presion_sistolica"]),
                registro["grupo"],
            ))
    return validos, rechazos


def generar_reporte(pacientes):
    reporte = []
    for grupo in GRUPOS_VALIDOS:
        del_grupo = [p for p in pacientes if p.grupo == grupo]
        cantidad = len(del_grupo)
        if cantidad == 0:
            presion_media = 0.0
            proporcion = 0.0
        else:
            presion_media = round(sum(p.presion for p in del_grupo) / cantidad, 2)
            hipertensos = sum(1 for p in del_grupo if p.es_hipertenso())
            proporcion = round(hipertensos / cantidad, 3)
        reporte.append({
            "grupo": grupo,
            "cantidad": cantidad,
            "presion_media": presion_media,
            "proporcion_hipertensos": proporcion,
        })
    return reporte


def guardar_csv(filas, ruta):
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)