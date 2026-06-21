# -----------------------------------------------
# Archivo: operaciones.py
# Clases: Venta, Restock
# Responsable: Paola Belgiovane
# Descripcion: Estas clases sirven para registrar
#              las operaciones que ocurren en la
#              maquina expendedora.
#              NO escriben archivos por su cuenta,
#              solo preparan los datos. El controlador
#              es el que se encarga de guardar todo.
# -----------------------------------------------

# Necesitamos datetime para saber cuando ocurrio la operacion
import datetime


# =======================================================
# CLASE: Venta
# =======================================================
class Venta:

    def __init__(self, producto_vendido, tarjeta_usada, cantidad_vendida):

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
        return self.producto_de_la_venta

    def get_tarjeta_de_la_venta(self):
        return self.tarjeta_de_la_venta

    def get_cantidad_de_la_venta(self):
        return self.cantidad_de_la_venta

    def get_fecha_y_hora_de_la_venta(self):
        return self.fecha_y_hora_de_la_venta

    def get_total_cobrado_en_la_venta(self):
        return self.total_cobrado_en_la_venta


    # --- METODO QUE PREPARA EL TEXTO PARA GUARDAR ---

    def guardar_venta_txt(self):
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

    def __init__(self, producto_a_reponer, cantidad_repuesta):

        # Guardamos el objeto producto y cuantas unidades se agregaron
        self.producto_del_restock = producto_a_reponer
        self.cantidad_repuesta_en_el_restock = cantidad_repuesta

        # Registramos automaticamente la fecha y hora del restock
        self.fecha_y_hora_del_restock = datetime.datetime.now()


    # --- GETTERS ---

    def get_producto_del_restock(self):
        return self.producto_del_restock

    def get_cantidad_repuesta_en_el_restock(self):
        return self.cantidad_repuesta_en_el_restock

    def get_fecha_y_hora_del_restock(self):
        return self.fecha_y_hora_del_restock


    # --- METODO QUE PREPARA EL TEXTO PARA GUARDAR ---

    def guardar_restock_txt(self):
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
        nombre_del_producto_repuesto = self.producto_del_restock.get_nombre()
        texto_del_restock = (
            f"Restock -> Producto: {nombre_del_producto_repuesto} | "
            f"Cantidad repuesta: {self.cantidad_repuesta_en_el_restock}"
        )
        return texto_del_restock
