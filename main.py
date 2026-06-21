# Archivo: main.py
# Responsables: Paola Belgiovane e Ivana Lopez

from controlador import MaquinaExpendedora

def principal():
    mi_maquina = MaquinaExpendedora()
    mi_maquina.iniciar()

if __name__ == "__main__":
    principal()
