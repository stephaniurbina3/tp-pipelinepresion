# Pipeline de control de presión arterial

**Integrantes:** Chicosky Pamela, Candelaria Grosso, Stephani Urbina

## Problema y usuario
Un equipo de salud recibe mediciones de presión arterial en CSV y JSON con errores de carga.
El programa descarta los registros inválidos, informa el motivo de cada rechazo y resume
la presión sistólica por grupo del estudio (A: control, B: intervención).

## Datos
Ver `data/README.md`. Cada fila corresponde a un paciente con una medición.

## Ejecución
No requiere bibliotecas externas (Python 3.10 o superior).
```bash
python src/main.py data/mediciones.csv
```
Genera `outputs/reporte.csv` y `outputs/rechazos.csv`.

## Pruebas
```bash
python tests/test_pipeline.py
```
Debe imprimir `Todas las pruebas pasaron.`

## Reglas de limpieza
- Código con formato `PAC-` y tres dígitos (expresión regular `PAC-\d{3}`, con `fullmatch`).
- Rangos válidos: edad 18–100, IMC 12–60, presión sistólica 70–250 mmHg.
- Grupos admitidos: `A` y `B`.
- Faltantes y valores no numéricos: el registro se rechaza con su motivo.
- Duplicados: se conserva la primera aparición; las siguientes se rechazan.

## Resultado de ejemplo
```
Leídos: 58 | válidos: 50 | rechazados: 8
{'grupo': 'A', 'cantidad': 27, 'presion_media': 127.26, 'proporcion_hipertensos': 0.185}
{'grupo': 'B', 'cantidad': 23, 'presion_media': 118.61, 'proporcion_hipertensos': 0.13}
```

## Limitaciones
- Datos simulados con fines didácticos; solo 50 pacientes válidos.
- El umbral de 140 mmHg es un criterio simplificado, no un diagnóstico clínico.
- `main.py` solo lee CSV.