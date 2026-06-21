# -----------------------------------------------
# Archivo: tarjeta.py
# Clase: Tarjeta
# Responsable: Ivana Lopez
# Descripcion: Esta clase representa la tarjeta
#              del cliente en la maquina expendedora.
#              Mapea los datos que vienen del JSON.
# -----------------------------------------------

class Tarjeta:

    # Aqui recibimos los datos y los guardamos
    # El campo "id" del JSON lo guardamos como hash_numero
    # El campo "saldo" del JSON lo guardamos como saldo
    def __init__(self, hash_numero_de_la_tarjeta, saldo_de_la_tarjeta):

        self.hash_numero = hash_numero_de_la_tarjeta
        self.saldo = saldo_de_la_tarjeta


    # --- GETTERS ---

    def get_hash_numero(self):
        return self.hash_numero

    def get_saldo(self):
        return self.saldo


    # --- SETTERS ---

    def set_saldo(self, nuevo_saldo_de_la_tarjeta):
        self.saldo = nuevo_saldo_de_la_tarjeta


    # --- METODOS SIMPLES ---

    def tiene_saldo(self, monto_a_verificar):
        # Devuelve True si el saldo alcanza para pagar el monto
        # Devuelve False si no alcanza
        if self.saldo >= monto_a_verificar:
            return True
        else:
            return False

    def descontar_saldo(self, monto_a_descontar):
        # Le resta el monto al saldo actual
        # NOTA: el controlador ya deberia verificar antes de llamar esto
        #       que el saldo es suficiente con tiene_saldo()
        self.saldo = self.saldo - monto_a_descontar


    # --- METODO PARA MOSTRAR LA TARJETA (para imprimir en consola) ---

    def __str__(self):
        texto_de_la_tarjeta = (
            f"Tarjeta: {self.hash_numero} | "
            f"Saldo actual: ${self.saldo}"
        )
        return texto_de_la_tarjeta
