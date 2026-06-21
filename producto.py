# -----------------------------------------------
# Archivo: producto.py
# Clase: Producto
# Responsable: Paola Belgiovane
# Descripcion: Esta clase representa un producto
#              de la maquina expendedora.
#              Mapea los datos que vienen del JSON.
# -----------------------------------------------

class Producto:

    # Aqui recibimos los datos y los guardamos
    def __init__(self, codigo_del_producto, nombre_del_producto, precio_del_producto, despedida_del_producto):

        # Estos datos vienen del JSON (cod, prod, precio, despedida)
        self.codigo = codigo_del_producto
        self.nombre = nombre_del_producto
        self.precio = precio_del_producto
        self.despedida = despedida_del_producto

        # Estos los inicializa el controlador despues, por eso arrancan en None / 0
        self.stock = 0
        self.posicion = None   # va a ser una tupla tipo (fila, columna) en la matriz


    # --- GETTERS (para leer los atributos) ---

    def get_codigo(self):
        return self.codigo

    def get_nombre(self):
        return self.nombre

    def get_precio(self):
        return self.precio

    def get_despedida(self):
        return self.despedida

    def get_stock(self):
        return self.stock

    def get_posicion(self):
        return self.posicion


    # --- SETTERS (para modificar los atributos) ---

    def set_stock(self, nuevo_stock):
        self.stock = nuevo_stock

    def set_posicion(self, nueva_posicion):
        # nueva_posicion tiene que ser una tupla, ej: (0, 2)
        self.posicion = nueva_posicion


    # --- METODOS DE ESTADO ---

    def hay_stock(self):
        # Devuelve True si quedan productos, False si no hay ninguno
        if self.stock > 0:
            return True
        else:
            return False


    # --- METODO PARA MOSTRAR EL PRODUCTO (para imprimir en consola) ---

    def __str__(self):
        texto_del_producto = (
            f"Codigo: {self.codigo} | "
            f"Nombre: {self.nombre} | "
            f"Precio: ${self.precio} | "
            f"Stock: {self.stock} | "
            f"Posicion: {self.posicion}"
        )
        return texto_del_producto
