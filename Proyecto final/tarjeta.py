# Responsables: Paola Belgiovane e Ivana Lopez


class Tarjeta:
    """
    Clase que representa la tarjeta de pago de un cliente.

    Cada objeto Tarjeta almacena un hash identificador (que viene del JSON
    de clientes descargado de GitHub) y el saldo disponible para compras.
    El controlador usa esta clase para verificar identidad y cobrar.

    Eficiencia: todos los atributos se almacenan directamente en la instancia,
    permitiendo acceso y modificacion en tiempo constante O(1).
    """

    # Aqui recibimos los datos y los guardamos
    # El campo "id" del JSON lo guardamos como hash_numero
    # El campo "saldo" del JSON lo guardamos como saldo
    def __init__(self, hash_numero_de_la_tarjeta, saldo_de_la_tarjeta):
        """
        Constructor de la clase Tarjeta.

        Recibe el identificador hash y el saldo inicial del cliente
        desde el JSON de GitHub y los almacena como atributos.

        Parametros:
            hash_numero_de_la_tarjeta: Identificador unico (hash) de la tarjeta.
            saldo_de_la_tarjeta (float): Saldo disponible en la tarjeta.

        Eficiencia: O(1) - solo asigna valores a atributos.
        """

        self.hash_numero = hash_numero_de_la_tarjeta
        self.saldo = saldo_de_la_tarjeta


    # --- GETTERS ---

    def get_hash_numero(self):
        """
        Devuelve el identificador hash unico de la tarjeta.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.hash_numero

    def get_saldo(self):
        """
        Devuelve el saldo actual disponible en la tarjeta.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.saldo


    # --- SETTERS ---

    def set_saldo(self, nuevo_saldo_de_la_tarjeta):
        """
        Actualiza el saldo de la tarjeta con un nuevo valor.

        Parametros:
            nuevo_saldo_de_la_tarjeta (float): El nuevo saldo a establecer.

        Eficiencia: O(1) - asignacion directa al atributo.
        """
        self.saldo = nuevo_saldo_de_la_tarjeta


    # --- METODOS SIMPLES ---

    def tiene_saldo(self, monto_a_verificar):
        """
        Verifica si la tarjeta tiene saldo suficiente para cubrir un monto.

        Parametros:
            monto_a_verificar (float): El monto que se quiere cobrar.

        Retorna:
            True si el saldo es mayor o igual al monto, False si no alcanza.

        Eficiencia: O(1) - una sola comparacion numerica.
        """
        # Devuelve True si el saldo alcanza para pagar el monto
        # Devuelve False si no alcanza
        if self.saldo >= monto_a_verificar:
            return True
        else:
            return False

    def descontar_saldo(self, monto_a_descontar):
        """
        Resta un monto del saldo actual de la tarjeta.

        Parametros:
            monto_a_descontar (float): El monto a restar del saldo.

        Nota: el controlador debe verificar previamente con tiene_saldo()
        que el saldo sea suficiente antes de llamar a este metodo.

        Eficiencia: O(1) - una sola operacion aritmetica.
        """
        # Le resta el monto al saldo actual
        # NOTA: el controlador ya deberia verificar antes de llamar esto
        #       que el saldo es suficiente con tiene_saldo()
        self.saldo = self.saldo - monto_a_descontar


    # --- METODO PARA MOSTRAR LA TARJETA (para imprimir en consola) ---

    def __str__(self):
        """
        Devuelve una representacion en texto de la tarjeta para imprimir en consola.
        Incluye el hash identificador y el saldo actual.

        Eficiencia: O(1) - construye un string con f-string usando acceso directo
        a los atributos.
        """
        texto_de_la_tarjeta = (
            f"Tarjeta: {self.hash_numero} | "
            f"Saldo actual: ${self.saldo}"
        )
        return texto_de_la_tarjeta
