# Archivo: main.py
# Responsables: Paola Belgiovane e Ivana Lopez
# Descripcion: Archivo de prueba para correr el menu principal

from controlador import MaquinaExpendedora

def principal():
    print("Iniciando pruebas de la maquina...")
    mi_maquina = MaquinaExpendedora()
    mi_maquina.iniciar()

if __name__ == "__main__":
    principal()
