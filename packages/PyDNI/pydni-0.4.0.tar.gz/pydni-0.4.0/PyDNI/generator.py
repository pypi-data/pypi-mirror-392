# generator.py

import random
from .dni import verificar_dni
from .cif import verificar_cif

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF = "ABCDEFGHJKLMNPQRSUVW"


class Generator:
    """Generador de DNIs, NIEs, CIFs y NIF para pruebas."""

    def generar_dni(self) -> str:
        numero = random.randint(0, 99999999)
        letra = LETRAS_DNI[numero % 23]
        return f"{numero:08d}{letra}"

    def generar_nie(self) -> str:
        inicial = random.choice("XYZ")
        numero = random.randint(0, 9999999)
        # Transformación NIE → DNI para cálculo
        mapa = {"X": "0", "Y": "1", "Z": "2"}
        numero_transformado = int(mapa[inicial] + f"{numero:07d}")
        letra = LETRAS_DNI[numero_transformado % 23]
        return f"{inicial}{numero:07d}{letra}"

    def generar_cif(self) -> str:
        inicial = random.choice(LETRAS_CIF)
        numero = f"{random.randint(0, 9999999):07d}"

        # Cálculo control (AEAT)
        suma_pares = sum(int(numero[i]) for i in range(1, 7, 2))
        suma_impares = 0
        for i in range(0, 7, 2):
            doble = int(numero[i]) * 2
            suma_impares += doble if doble < 10 else doble - 9

        total = suma_pares + suma_impares
        digito = (10 - (total % 10)) % 10

        control_letras = "JABCDEFGHI"
        control_letra = control_letras[digito]

        # Reglas según tipo
        if inicial in "PQRSNW":     # Solo letra
            control = control_letra
        elif inicial in "ABEH":     # Solo número
            control = str(digito)
        else:                       # Ambos válidos
            control = random.choice([str(digito), control_letra])

        return f"{inicial}{numero}{control}"

    def generar_varios(self, cantidad: int, tipo: str) -> list:
        """Genera una lista de documentos válidos sin repetir."""
        generados = set()

        while len(generados) < cantidad:
            if tipo == "DNI":
                doc = self.generar_dni()
            elif tipo == "NIE":
                doc = self.generar_nie()
            elif tipo == "CIF":
                doc = self.generar_cif()
            elif tipo == "AUTO":
                # Genera un tipo aleatorio
                doc = random.choice([
                    self.generar_dni(),
                    self.generar_nie(),
                    self.generar_cif()
                ])
            else:
                raise ValueError("Tipo no reconocido (DNI, NIE, CIF, AUTO)")

            generados.add(doc)

        return list(generados)