# Responsables: Paola Belgiovane e Ivana Lopez

# Importamos la clase principal desde el controlador
from controlador import MaquinaExpendedora

def principal():
    """
    Funcion principal del programa. Crea una instancia de la maquina
    expendedora y arranca el bucle principal de interaccion con el usuario.

    Al crear la instancia de MaquinaExpendedora se cargan automaticamente
    los productos desde el archivo TXT local y los clientes desde GitHub.
    Luego se inicia el motor (bucle while) que mantiene el programa vivo.

    Eficiencia: O(1) en si misma, ya que solo instancia un objeto y llama
    a un metodo. La carga de datos y el bucle principal corren dentro de
    la clase MaquinaExpendedora.
    """
    print("========================================")
    print(" INICIANDO SISTEMA EXPENDEDOR...")
    print("========================================")
    
    # 1. Creamos la maquina
    #    (Al crearla ya se cargan los datos)
    mi_maquina = MaquinaExpendedora()
    
    # 2. Encendemos el motor (bucle principal)
    mi_maquina.iniciar()
    
    print("Programa finalizado correctamente.")

# Le indicamos a Python que este es el archivo principal a ejecutar
if __name__ == "__main__":
    principal()
