
import csv
import json
from abc import ABC, abstractmethod


class FuenteDatos(ABC):


    @abstractmethod
    def cargar(self, ruta):
        raise NotImplementedError


class FuenteCSV(FuenteDatos):
    def cargar(self, ruta):
        with open(ruta, encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))


class FuenteJSON(FuenteDatos):
    def cargar(self, ruta):
        with open(ruta, encoding="utf-8") as archivo:
            contenido = json.load(archivo)
        if not isinstance(contenido, list):
            raise ValueError(
                "El JSON debe contener una lista de registros, "
                f"pero contiene un valor de tipo {type(contenido).__name__}."
            )
        return contenido