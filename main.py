# -----------------------------------------------
# Archivo: main.py
# Responsables: Paola Belgiovane e Ivana Lopez
# Descripcion: Ejecucion del sistema
# -----------------------------------------------

from controlador import MaquinaExpendedora

def principal():
    print("Iniciando el sistema de la Maquina Expendedora...")
    
    # Instanciamos la maquina
    mi_maquina = MaquinaExpendedora()
    
    # Encendemos el motor
    mi_maquina.iniciar()
    
    print("Programa finalizado.")

if __name__ == "__main__":
    principal()
