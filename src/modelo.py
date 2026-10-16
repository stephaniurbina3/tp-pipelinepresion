


class Paciente:
    UMBRAL_HIPERTENSION = 140  

    def __init__(self, codigo, edad, imc, presion, grupo):
        self.codigo = codigo
        self.edad = edad
        self.imc = imc
        self.presion = presion
        self.grupo = grupo

    def franja_etaria(self):
        if self.edad < 40:
            return "18-39"
        if self.edad < 60:
            return "40-59"
        return "60+"

    def es_hipertenso(self):
        return self.presion >= self.UMBRAL_HIPERTENSION

    def __str__(self):
        return (f"{self.codigo} | grupo {self.grupo} | "
                f"{self.edad:g} años | PAS {self.presion:g} mmHg")