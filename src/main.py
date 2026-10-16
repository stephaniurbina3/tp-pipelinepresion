import sys
from pathlib import Path

from fuentes import FuenteCSV
from pipeline import limpiar, generar_reporte, guardar_csv

CARPETA_SALIDA = Path("outputs")


def main(ruta_entrada):
    registros = FuenteCSV().cargar(ruta_entrada)
    validos, rechazos = limpiar(registros)
    reporte = generar_reporte(validos)

    print(f"Leídos: {len(registros)} | válidos: {len(validos)} | rechazados: {len(rechazos)}")
    for fila in reporte:
        print(fila)

    CARPETA_SALIDA.mkdir(exist_ok=True)
    guardar_csv(reporte, CARPETA_SALIDA / "reporte.csv")
    if rechazos:
        guardar_csv(rechazos, CARPETA_SALIDA / "rechazos.csv")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python src/main.py <archivo_de_mediciones.csv>")
    main(sys.argv[1])