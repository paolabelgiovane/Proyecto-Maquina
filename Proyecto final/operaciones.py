# Responsables: Paola Belgiovane e Ivana Lopez


# Necesitamos datetime para saber cuando ocurrio la operacion
import datetime


# =======================================================
# CLASE: Venta
# =======================================================
class Venta:
    """
    Clase que representa una operacion de venta en la maquina expendedora.

    Almacena el producto vendido, la tarjeta utilizada, la cantidad vendida,
    la fecha/hora de la operacion y el total cobrado. Esta clase NO escribe
    archivos por su cuenta; solo prepara los datos para que el controlador
    los guarde en ventas.txt.

    Eficiencia: el constructor calcula el total cobrado en O(1) usando una
    multiplicacion simple, y el metodo guardar_venta_txt() genera el texto
    en O(1) ya que solo concatena atributos sin recorrer colecciones.
    """

    def __init__(self, producto_vendido, tarjeta_usada, cantidad_vendida):
        """
        Constructor de la clase Venta.

        Registra automaticamente la fecha y hora de la operacion usando
        datetime.now() y calcula el total cobrado multiplicando el precio
        del producto por la cantidad vendida.

        Parametros:
            producto_vendido (Producto): El objeto Producto que se vendio.
            tarjeta_usada (Tarjeta): El objeto Tarjeta con la que se pago.
            cantidad_vendida (int): Cuantas unidades se vendieron.

        Eficiencia: O(1) - asigna atributos, obtiene la hora del sistema
        y hace una multiplicacion.
        """

        # Guardamos el objeto producto, el objeto tarjeta y cuantos se vendieron
        self.producto_de_la_venta = producto_vendido
        self.tarjeta_de_la_venta = tarjeta_usada
        self.cantidad_de_la_venta = cantidad_vendida

        # Registramos automaticamente la fecha y hora en que se creo la venta
        self.fecha_y_hora_de_la_venta = datetime.datetime.now()

        # Calculamos el total que se cobro
        self.total_cobrado_en_la_venta = producto_vendido.get_precio() * cantidad_vendida


    # --- GETTERS ---

    def get_producto_de_la_venta(self):
        """
        Devuelve el objeto Producto asociado a esta venta.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.producto_de_la_venta

    def get_tarjeta_de_la_venta(self):
        """
        Devuelve el objeto Tarjeta utilizada en esta venta.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.tarjeta_de_la_venta

    def get_cantidad_de_la_venta(self):
        """
        Devuelve la cantidad de unidades vendidas en esta operacion.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.cantidad_de_la_venta

    def get_fecha_y_hora_de_la_venta(self):
        """
        Devuelve el objeto datetime con la fecha y hora de la venta.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.fecha_y_hora_de_la_venta

    def get_total_cobrado_en_la_venta(self):
        """
        Devuelve el monto total cobrado en esta venta (precio * cantidad).

        Eficiencia: O(1) - acceso directo al atributo, ya que el total
        fue pre-calculado en el constructor.
        """
        return self.total_cobrado_en_la_venta


    # --- METODO QUE PREPARA EL TEXTO PARA GUARDAR ---

    def guardar_venta_txt(self):
        """
        Arma y devuelve un string con el registro de la venta en formato legible.

        Este metodo NO guarda el archivo por su cuenta. Solo devuelve el texto
        formateado para que el controlador lo escriba en el archivo ventas.txt.
        El formato incluye: fecha y hora, nombre y codigo del producto,
        cantidad vendida, total cobrado y hash de la tarjeta del cliente.

        Retorna:
            str: Bloque de texto formateado listo para escribir en archivo.

        Eficiencia: O(1) - construye un string concatenando valores de atributos
        con f-string, sin recorrer ninguna estructura de datos.
        """
        # Este metodo arma el texto de la venta con formato lindo
        # NO guarda el archivo. Solo devuelve el string.
        # El controlador es el que va a escribir en el archivo de verdad.

        linea_separadora = "=" * 40
        nombre_del_producto_vendido = self.producto_de_la_venta.get_nombre()
        codigo_del_producto_vendido = self.producto_de_la_venta.get_codigo()
        hash_de_la_tarjeta_usada = self.tarjeta_de_la_venta.get_hash_numero()
        fecha_formateada = self.fecha_y_hora_de_la_venta.strftime("%d/%m/%Y %H:%M:%S")

        texto_de_la_venta = (
            f"{linea_separadora}\n"
            f"REGISTRO DE VENTA\n"
            f"Fecha y hora: {fecha_formateada}\n"
            f"Producto: {nombre_del_producto_vendido} (Cod: {codigo_del_producto_vendido})\n"
            f"Cantidad vendida: {self.cantidad_de_la_venta}\n"
            f"Total cobrado: ${self.total_cobrado_en_la_venta}\n"
            f"Tarjeta del cliente: {hash_de_la_tarjeta_usada}\n"
            f"{linea_separadora}\n"
        )

        return texto_de_la_venta


    # --- METODO PARA MOSTRAR LA VENTA (para imprimir en consola) ---

    def __str__(self):
        """
        Devuelve una representacion resumida de la venta para imprimir en consola.

        Eficiencia: O(1) - construye un string con f-string usando acceso directo
        a los atributos del objeto.
        """
        nombre_del_producto_vendido = self.producto_de_la_venta.get_nombre()
        texto_de_la_venta = (
            f"Venta -> Producto: {nombre_del_producto_vendido} | "
            f"Cantidad: {self.cantidad_de_la_venta} | "
            f"Total: ${self.total_cobrado_en_la_venta}"
        )
        return texto_de_la_venta


# =======================================================
# CLASE: Restock
# =======================================================
class Restock:
    """
    Clase que representa una operacion de reabastecimiento (restock).

    Almacena el producto que fue reabastecido, la cantidad de unidades
    agregadas y la fecha/hora de la operacion. Al igual que Venta, esta
    clase NO escribe archivos; solo prepara los datos para que el
    controlador los guarde en restock.txt.

    Eficiencia: tanto el constructor como guardar_restock_txt() operan
    en O(1), ya que solo asignan atributos y concatenan strings sin
    recorrer estructuras de datos.
    """

    def __init__(self, producto_a_reponer, cantidad_repuesta):
        """
        Constructor de la clase Restock.

        Registra automaticamente la fecha y hora de la operacion usando
        datetime.now().

        Parametros:
            producto_a_reponer (Producto): El objeto Producto que se reabastecio.
            cantidad_repuesta (int): Cuantas unidades se agregaron al stock.

        Eficiencia: O(1) - asigna atributos y obtiene la hora del sistema.
        """

        # Guardamos el objeto producto y cuantas unidades se agregaron
        self.producto_del_restock = producto_a_reponer
        self.cantidad_repuesta_en_el_restock = cantidad_repuesta

        # Registramos automaticamente la fecha y hora del restock
        self.fecha_y_hora_del_restock = datetime.datetime.now()


    # --- GETTERS ---

    def get_producto_del_restock(self):
        """
        Devuelve el objeto Producto asociado a esta operacion de restock.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.producto_del_restock

    def get_cantidad_repuesta_en_el_restock(self):
        """
        Devuelve la cantidad de unidades que fueron agregadas al stock.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.cantidad_repuesta_en_el_restock

    def get_fecha_y_hora_del_restock(self):
        """
        Devuelve el objeto datetime con la fecha y hora del restock.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.fecha_y_hora_del_restock


    # --- METODO QUE PREPARA EL TEXTO PARA GUARDAR ---

    def guardar_restock_txt(self):
        """
        Arma y devuelve un string con el registro del restock en formato legible.

        Este metodo NO guarda el archivo por su cuenta. Solo devuelve el texto
        formateado para que el controlador lo escriba en restock.txt.
        El formato incluye: fecha y hora, nombre y codigo del producto,
        y la cantidad de unidades repuestas.

        Retorna:
            str: Bloque de texto formateado listo para escribir en archivo.

        Eficiencia: O(1) - construye un string con f-string usando acceso
        directo a atributos, sin recorrer colecciones.
        """
        # Al igual que en Venta, este metodo solo prepara el texto.
        # El controlador es quien lo escribe en el archivo de verdad.

        linea_separadora = "-" * 40
        nombre_del_producto_repuesto = self.producto_del_restock.get_nombre()
        codigo_del_producto_repuesto = self.producto_del_restock.get_codigo()
        fecha_formateada = self.fecha_y_hora_del_restock.strftime("%d/%m/%Y %H:%M:%S")

        texto_del_restock = (
            f"{linea_separadora}\n"
            f"REGISTRO DE RESTOCK\n"
            f"Fecha y hora: {fecha_formateada}\n"
            f"Producto: {nombre_del_producto_repuesto} (Cod: {codigo_del_producto_repuesto})\n"
            f"Cantidad repuesta: {self.cantidad_repuesta_en_el_restock}\n"
            f"{linea_separadora}\n"
        )

        return texto_del_restock


    # --- METODO PARA MOSTRAR EL RESTOCK (para imprimir en consola) ---

    def __str__(self):
        """
        Devuelve una representacion resumida del restock para imprimir en consola.

        Eficiencia: O(1) - construye un string con f-string usando acceso directo
        a los atributos del objeto.
        """
        nombre_del_producto_repuesto = self.producto_del_restock.get_nombre()
        texto_del_restock = (
            f"Restock -> Producto: {nombre_del_producto_repuesto} | "
            f"Cantidad repuesta: {self.cantidad_repuesta_en_el_restock}"
        )
        return texto_del_restock
