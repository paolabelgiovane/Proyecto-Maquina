# -----------------------------------------------
# Archivo: producto.py
# Clase: Producto
# Responsable: Paola Belgiovane
# Descripcion: Esta clase representa un producto
#              de la maquina expendedora.
#              Mapea los datos que vienen del archivo TXT local.
# -----------------------------------------------

class Producto:
    """
    Clase que representa un producto individual de la maquina expendedora.

    Cada objeto Producto almacena los datos basicos (codigo, nombre, precio,
    despedida) y los datos operativos (stock, posicion en la vitrina).
    Los datos basicos se cargan desde el archivo TXT local, mientras que
    stock y posicion se asignan luego por el controlador.

    Eficiencia: todos los atributos se almacenan directamente en la instancia,
    lo que permite acceso en tiempo constante O(1) a cualquier dato del producto
    sin necesidad de buscar en estructuras adicionales.
    """

    # Aqui recibimos los datos y los guardamos
    def __init__(self, codigo_del_producto, nombre_del_producto, precio_del_producto, despedida_del_producto):
        """
        Constructor de la clase Producto.

        Recibe los cuatro datos fundamentales que vienen del archivo TXT
        y los almacena como atributos de la instancia. Ademas inicializa
        stock en 0 y posicion en None, ya que estos se configuran despues
        por el controlador cuando se hace un restock o se asigna posicion.

        Parametros:
            codigo_del_producto (str): Codigo unico del producto (ej: 'CocaC').
            nombre_del_producto (str): Nombre descriptivo del producto.
            precio_del_producto (float): Precio unitario del producto.
            despedida_del_producto (str): Mensaje de despedida al comprar.

        Eficiencia: O(1) - solo asigna valores a atributos, sin recorrer
        ninguna estructura de datos.
        """

        # Estos datos vienen del TXT (cod, prod, precio, despedida)
        self.codigo = codigo_del_producto
        self.nombre = nombre_del_producto
        self.precio = precio_del_producto
        self.despedida = despedida_del_producto

        # Estos los inicializa el controlador despues, por eso arrancan en None / 0
        self.stock = 0
        self.posicion = None   # va a ser una tupla tipo (fila, columna) en la matriz


    # --- GETTERS (para leer los atributos) ---

    def get_codigo(self):
        """
        Devuelve el codigo unico del producto.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.codigo

    def get_nombre(self):
        """
        Devuelve el nombre descriptivo del producto.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.nombre

    def get_precio(self):
        """
        Devuelve el precio unitario del producto.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.precio

    def get_despedida(self):
        """
        Devuelve el mensaje de despedida que se muestra tras la compra.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.despedida

    def get_stock(self):
        """
        Devuelve la cantidad de unidades disponibles en stock.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.stock

    def get_posicion(self):
        """
        Devuelve la posicion del producto en la vitrina como una tupla
        (fila, columna), o None si el producto no tiene posicion asignada.

        Eficiencia: O(1) - acceso directo al atributo.
        """
        return self.posicion


    # --- SETTERS (para modificar los atributos) ---

    def set_stock(self, nuevo_stock):
        """
        Actualiza la cantidad de stock del producto.

        Parametros:
            nuevo_stock (int): La nueva cantidad de unidades disponibles.

        Eficiencia: O(1) - asignacion directa al atributo.
        """
        self.stock = nuevo_stock

    def set_posicion(self, nueva_posicion):
        """
        Asigna o cambia la posicion del producto en la vitrina.

        Parametros:
            nueva_posicion (tuple): Tupla con (fila, columna), ej: (0, 2).

        Eficiencia: O(1) - asignacion directa al atributo.
        """
        # nueva_posicion tiene que ser una tupla, ej: (0, 2)
        self.posicion = nueva_posicion


    # --- METODOS DE ESTADO ---

    def hay_stock(self):
        """
        Verifica si el producto tiene al menos una unidad disponible.

        Retorna:
            True si el stock es mayor a 0, False en caso contrario.

        Eficiencia: O(1) - una sola comparacion numerica.
        """
        # Devuelve True si quedan productos, False si no hay ninguno
        if self.stock > 0:
            return True
        else:
            return False


    # --- METODO PARA MOSTRAR EL PRODUCTO (para imprimir en consola) ---

    def __str__(self):
        """
        Devuelve una representacion en texto del producto para imprimir en consola.
        Incluye codigo, nombre, precio, stock y posicion en un formato legible.

        Eficiencia: O(1) - construye un string con f-string usando acceso directo
        a los atributos, sin recorrer ninguna coleccion.
        """
        texto_del_producto = (
            f"Codigo: {self.codigo} | "
            f"Nombre: {self.nombre} | "
            f"Precio: ${self.precio} | "
            f"Stock: {self.stock} | "
            f"Posicion: {self.posicion}"
        )
        return texto_del_producto
