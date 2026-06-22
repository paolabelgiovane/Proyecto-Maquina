# -----------------------------------------------
# Archivo: controlador.py
# Clase: MaquinaExpendedora
# Responsable: Ivana Lopez
# Descripcion: Aca va toda la logica pesada de la
#              maquina expendedora. Esta clase es la
#              que conecta con internet, carga los
#              datos desde un TXT local y GitHub,
#              y coordina todo el resto.
# -----------------------------------------------

# Importamos las librerias que necesitamos
import requests   # para hacer los GET a GitHub
import json       # para leer los archivos locales de respaldo
import os         # para verificar si existe el archivo local

# Importamos nuestras clases entidad
from producto import Producto
from tarjeta import Tarjeta
from operaciones import Venta, Restock

# Importamos la libreria para los graficos
import matplotlib.pyplot as plt

# Estas son las URLs de GitHub de donde bajamos los datos
URL_DEL_JSON_DE_PRODUCTOS = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/productos.json"
URL_DEL_JSON_DE_CLIENTES  = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/clientes.json"

# Estos son los archivos locales de respaldo, por si no hay internet
RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS = "productos.txt"
RUTA_DEL_ARCHIVO_LOCAL_DE_CLIENTES  = "clientes.json"


class MaquinaExpendedora:
    """
    Clase principal que controla toda la logica de la maquina expendedora.

    Coordina la carga de datos (productos desde TXT local, clientes desde
    GitHub), el bucle principal de interaccion con el usuario, la venta de
    productos, el reabastecimiento (restock) y la generacion de reportes
    con estadisticas y graficos.

    Usa listas para almacenar los objetos Producto y Tarjeta, lo cual
    resulta en busquedas lineales O(n) al buscar por codigo o por hash.
    Para el volumen de datos de una maquina expendedora (decenas de productos
    y pocos clientes), esta complejidad es aceptable y mantiene el codigo
    simple y legible.
    """

    def __init__(self):
        """
        Constructor de la clase MaquinaExpendedora.

        Inicializa las listas vacias de productos y tarjetas, y luego
        llama a cargar_datos_iniciales() para poblarlas desde el archivo
        TXT local y desde GitHub.

        Eficiencia: O(n + m) donde n es la cantidad de productos en el
        archivo TXT y m la cantidad de clientes en el JSON de GitHub,
        ya que la carga recorre ambas fuentes una vez.
        """
        # Usamos listas para guardar todos los objetos, como dice el estilo del proyecto
        self.lista_de_productos = []
        self.lista_de_tarjetas  = []

        # Llamamos a cargar datos cuando se crea la maquina
        self.cargar_datos_iniciales()


    # =======================================================
    # LOGICA DE CARGA DE DATOS
    # =======================================================
    def cargar_datos_iniciales(self):
        """
        Metodo que coordina la carga completa de datos al iniciar la maquina.

        Primero carga los productos desde el archivo TXT local, luego
        los clientes desde GitHub (con respaldo JSON local si falla).
        Imprime un resumen con la cantidad de productos y tarjetas cargados.

        Eficiencia: O(n + m) donde n es la cantidad de productos y m la
        cantidad de clientes. Cada fuente de datos se recorre una sola vez.
        """
        # Este metodo intenta bajar los datos de GitHub.
        # Si algo falla, usa los archivos locales de respaldo.

        print("Iniciando carga de datos...")

        # Primero cargamos los productos, despues los clientes
        self.cargar_lista_de_productos()
        self.cargar_lista_de_tarjetas()

        print("Carga de datos finalizada.")
        print(f"  Productos cargados: {len(self.lista_de_productos)}")
        print(f"  Tarjetas cargadas:  {len(self.lista_de_tarjetas)}")


    # -------------------------------------------------------
    # Funciones para cargar productos
    # -------------------------------------------------------

    def cargar_lista_de_productos(self):
        """
        Carga los productos desde el archivo TXT local y luego actualiza
        los precios consultando GitHub.

        Primero verifica si existe el archivo TXT local. Si existe, lo lee
        y crea los objetos Producto. Despues se conecta a GitHub para
        sincronizar los precios (por si cambiaron remotamente). Si no hay
        conexion, se queda con los precios que tenia el archivo local.

        Eficiencia: O(n * p) en el peor caso, donde n es la cantidad de
        productos locales y p la cantidad de productos en GitHub, porque
        por cada producto de GitHub se busca linealmente en la lista local
        con buscar_producto_por_codigo(). Para el volumen tipico de una
        maquina expendedora esto es despreciable.
        """
        # Intentamos leer el archivo local primero
        
        datos_crudos_locales = None
        if os.path.exists(RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS):
            print("  INFO: Se encontro un inventario guardado localmente. Cargando desde el archivo local...")
            datos_crudos_locales = self.leer_txt_local_de_productos()
        
        # Si el archivo local existia, creamos los objetos
        if datos_crudos_locales is not None:
            self.crear_objetos_producto(datos_crudos_locales)
        else:
            print("  INFO: No se encontro el archivo de productos. Se supone que la maquina esta vacia.")

        # Ahora nos conectamos a GitHub solo para actualizar precios
        try:
            print("  Conectando a GitHub para revisar si cambiaron los precios...")
            respuesta_del_servidor = requests.get(URL_DEL_JSON_DE_PRODUCTOS, timeout=10)
            respuesta_del_servidor.raise_for_status()

            datos_crudos_de_github = respuesta_del_servidor.json()
            
            # Recorremos lo que vino de GitHub y actualizamos precios si el producto existe
            for producto_github in datos_crudos_de_github:
                codigo_github = producto_github.get("cod")
                nuevo_precio = producto_github.get("precio")
                
                # Buscamos si tenemos ese producto en nuestra maquina
                producto_local = self.buscar_producto_por_codigo(codigo_github)
                if producto_local is not None and nuevo_precio is not None:
                    # Actualizamos el precio
                    producto_local.precio = float(nuevo_precio)

            print("  Precios actualizados desde GitHub correctamente.")

        except requests.exceptions.ConnectionError:
            print("  ERROR: No se pudo conectar a internet. Suponemos que los precios no han cambiado.")
        except requests.exceptions.Timeout:
            print("  ERROR: La conexion con GitHub tardo demasiado. Suponemos que los precios no han cambiado.")
        except requests.exceptions.HTTPError as error_http:
            print(f"  ERROR HTTP al bajar productos: {error_http}. Suponemos que los precios no han cambiado.")
        except requests.exceptions.RequestException as error_general_de_requests:
            print(f"  ERROR inesperado de requests: {error_general_de_requests}. Suponemos que los precios no han cambiado.")


    def leer_txt_local_de_productos(self):
        """
        Lee el archivo TXT local de productos y devuelve los datos como
        lista de diccionarios.

        El formato esperado por linea es: cod;prod;precio;despedida;stock;fila;columna
        Los campos stock, fila y columna son opcionales. Si fila y columna
        valen -1, se interpreta como que el producto no tiene posicion asignada.
        Si el archivo no existe o tiene errores, devuelve None.

        Retorna:
            list o None: Lista de diccionarios con los datos de cada producto,
            o None si hubo algun error al leer el archivo.

        Eficiencia: O(n) donde n es la cantidad de lineas en el archivo.
        Cada linea se procesa una sola vez con split(';') que es O(k)
        donde k es la longitud de la linea.
        """
        # Lee el archivo TXT local de productos y devuelve los datos como lista de diccionarios
        # El formato esperado por linea es: cod;prod;precio;despedida;stock;fila;columna
        # Si el archivo tampoco existe, devuelve None

        datos_leidos_del_archivo = []

        try:
            archivo_local_de_productos = open(RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS, "r", encoding="utf-8")
            lineas_del_archivo = archivo_local_de_productos.readlines()
            archivo_local_de_productos.close()

            for linea_actual in lineas_del_archivo:
                linea_limpia = linea_actual.strip()
                if linea_limpia != "":
                    partes_de_la_linea = linea_limpia.split(";")
                    # Verificamos que tenga los datos minimos
                    if len(partes_de_la_linea) >= 4:
                        diccionario_de_un_producto = {
                            "cod": partes_de_la_linea[0],
                            "prod": partes_de_la_linea[1],
                            "precio": float(partes_de_la_linea[2]),
                            "despedida": partes_de_la_linea[3]
                        }
                        # Si tiene stock guardado
                        if len(partes_de_la_linea) >= 5:
                            diccionario_de_un_producto["stock"] = int(partes_de_la_linea[4])
                        # Si tiene posicion guardada (fila y columna separadas)
                        if len(partes_de_la_linea) >= 7:
                            if int(partes_de_la_linea[5]) != -1 and int(partes_de_la_linea[6]) != -1:
                                diccionario_de_un_producto["posicion"] = [int(partes_de_la_linea[5]), int(partes_de_la_linea[6])]
                        
                        datos_leidos_del_archivo.append(diccionario_de_un_producto)
                        
            print("  Archivo local de productos TXT leido correctamente.")

        except FileNotFoundError:
            print(f"  ERROR: Tampoco existe el archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS}'.")
            datos_leidos_del_archivo = None

        except ValueError as error_de_valor:
            print(f"  ERROR: El archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS}' tiene datos invalidos (ej. precio no numerico). Detalles: {error_de_valor}")
            datos_leidos_del_archivo = None

        except Exception as error_al_leer_archivo:
            print(f"  ERROR inesperado al leer el archivo local de productos: {error_al_leer_archivo}")
            datos_leidos_del_archivo = None

        return datos_leidos_del_archivo


    def crear_objetos_producto(self, lista_de_datos_de_productos):
        """
        Recorre la lista de diccionarios y crea un objeto Producto por cada uno.

        Los diccionarios deben tener al menos las claves 'cod', 'prod', 'precio'
        y 'despedida'. Opcionalmente pueden tener 'stock' y 'posicion'.
        Los objetos creados se agregan a self.lista_de_productos.
        Si un diccionario tiene datos incompletos, se omite con un mensaje
        de error y se continua con el siguiente.

        Parametros:
            lista_de_datos_de_productos (list): Lista de diccionarios, cada uno
            con los datos de un producto.

        Eficiencia: O(n) donde n es la cantidad de diccionarios en la lista.
        Cada diccionario se procesa una sola vez para crear el objeto Producto.
        """
        # Recorre la lista de diccionarios y crea un objeto Producto por cada uno
        # Despues los guarda en self.lista_de_productos

        for diccionario_de_un_producto in lista_de_datos_de_productos:
            try:
                codigo_del_producto   = diccionario_de_un_producto["cod"]
                nombre_del_producto   = diccionario_de_un_producto["prod"]
                precio_del_producto   = diccionario_de_un_producto["precio"]
                despedida_del_producto = diccionario_de_un_producto["despedida"]

                nuevo_objeto_producto = Producto(
                    codigo_del_producto,
                    nombre_del_producto,
                    precio_del_producto,
                    despedida_del_producto
                )

                # Sacamos stock y posicion del diccionario
                # Usamos .get() porque el JSON de GitHub no tiene estos campos
                stock_guardado = diccionario_de_un_producto.get("stock")
                posicion_guardada = diccionario_de_un_producto.get("posicion")

                if stock_guardado is not None:
                    nuevo_objeto_producto.set_stock(stock_guardado)
                
                if posicion_guardada is not None:
                    # El archivo guarda las posiciones como listas [fila, columna]
                    # Nosotros las usamos como tuplas (fila, columna) dentro del programa
                    if type(posicion_guardada) == list:
                        posicion_guardada = (posicion_guardada[0], posicion_guardada[1])
                    nuevo_objeto_producto.set_posicion(posicion_guardada)

                self.lista_de_productos.append(nuevo_objeto_producto)

            except KeyError as clave_que_falta:
                # Si al diccionario le falta alguna clave, avisamos y seguimos con el proximo
                print(f"  ERROR: Al producto le falta la clave {clave_que_falta}. Se omite ese producto.")

            except Exception as error_al_crear_producto:
                print(f"  ERROR inesperado al crear un producto: {error_al_crear_producto}. Se omite.")


    # -------------------------------------------------------
    # Funciones para cargar tarjetas (clientes)
    # -------------------------------------------------------

    def cargar_lista_de_tarjetas(self):
        """
        Descarga los datos de clientes desde GitHub y crea los objetos Tarjeta.

        Intenta conectarse a GitHub para obtener el JSON de clientes.
        Si la conexion falla por cualquier motivo (sin internet, timeout,
        error HTTP), usa el archivo JSON local como respaldo.
        Los datos obtenidos se pasan a crear_objetos_tarjeta() para
        crear las instancias de la clase Tarjeta.

        Eficiencia: O(m) donde m es la cantidad de clientes en el JSON.
        La descarga desde GitHub depende de la velocidad de red pero se
        limita con un timeout de 10 segundos.
        """
        # Hace lo mismo que cargar_lista_de_productos pero para los clientes

        datos_crudos_de_clientes = None

        try:
            print("  Conectando a GitHub para bajar clientes...")
            respuesta_del_servidor = requests.get(URL_DEL_JSON_DE_CLIENTES, timeout=10)
            respuesta_del_servidor.raise_for_status()

            datos_crudos_de_clientes = respuesta_del_servidor.json()
            print("  Clientes descargados de GitHub correctamente.")

        except requests.exceptions.ConnectionError:
            print("  ERROR: No se pudo conectar a internet.")
            print("  Usando archivo local de respaldo para clientes...")
            datos_crudos_de_clientes = self.leer_json_local_de_clientes()

        except requests.exceptions.Timeout:
            print("  ERROR: La conexion con GitHub tardo demasiado (timeout).")
            print("  Usando archivo local de respaldo para clientes...")
            datos_crudos_de_clientes = self.leer_json_local_de_clientes()

        except requests.exceptions.HTTPError as error_http:
            print(f"  ERROR HTTP al bajar clientes: {error_http}")
            print("  Usando archivo local de respaldo para clientes...")
            datos_crudos_de_clientes = self.leer_json_local_de_clientes()

        except requests.exceptions.RequestException as error_general_de_requests:
            print(f"  ERROR inesperado de requests: {error_general_de_requests}")
            print("  Usando archivo local de respaldo para clientes...")
            datos_crudos_de_clientes = self.leer_json_local_de_clientes()

        if datos_crudos_de_clientes is not None:
            self.crear_objetos_tarjeta(datos_crudos_de_clientes)
        else:
            print("  ADVERTENCIA: No se pudieron cargar los clientes por ninguna via.")


    def leer_json_local_de_clientes(self):
        """
        Lee el archivo JSON local de clientes y devuelve los datos como
        lista de diccionarios.

        Este metodo es el respaldo para cuando no se puede acceder a GitHub.
        Si el archivo no existe o tiene formato invalido, devuelve None.

        Retorna:
            list o None: Lista de diccionarios con los datos de cada cliente,
            o None si hubo algun error.

        Eficiencia: O(m) donde m es la cantidad de clientes en el archivo.
        json.load() parsea todo el archivo de una sola vez.
        """
        # Lee el archivo JSON local de clientes y devuelve los datos

        datos_leidos_del_archivo = None

        try:
            archivo_local_de_clientes = open(RUTA_DEL_ARCHIVO_LOCAL_DE_CLIENTES, "r", encoding="utf-8")
            datos_leidos_del_archivo = json.load(archivo_local_de_clientes)
            archivo_local_de_clientes.close()
            print("  Archivo local de clientes leido correctamente.")

        except FileNotFoundError:
            print(f"  ERROR: Tampoco existe el archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_CLIENTES}'.")

        except json.JSONDecodeError:
            print(f"  ERROR: El archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_CLIENTES}' tiene un formato JSON invalido.")

        except Exception as error_al_leer_archivo:
            print(f"  ERROR inesperado al leer el archivo local de clientes: {error_al_leer_archivo}")

        return datos_leidos_del_archivo


    def crear_objetos_tarjeta(self, lista_de_datos_de_clientes):
        """
        Recorre la lista de diccionarios de clientes y crea un objeto Tarjeta
        por cada uno.

        Los diccionarios deben tener las claves 'id' (que se guarda como
        hash_numero) y 'saldo'. Si un diccionario tiene datos incompletos,
        se omite con un mensaje de error.

        Parametros:
            lista_de_datos_de_clientes (list): Lista de diccionarios con
            los datos de cada cliente provenientes del JSON.

        Eficiencia: O(m) donde m es la cantidad de diccionarios en la lista.
        Cada diccionario se procesa una sola vez.
        """
        # Recorre la lista de diccionarios y crea un objeto Tarjeta por cada uno

        for diccionario_de_un_cliente in lista_de_datos_de_clientes:
            try:
                # El campo "id" del JSON va al atributo hash_numero de Tarjeta
                hash_numero_de_la_tarjeta = diccionario_de_un_cliente["id"]
                saldo_de_la_tarjeta       = diccionario_de_un_cliente["saldo"]

                nuevo_objeto_tarjeta = Tarjeta(
                    hash_numero_de_la_tarjeta,
                    saldo_de_la_tarjeta
                )

                self.lista_de_tarjetas.append(nuevo_objeto_tarjeta)

            except KeyError as clave_que_falta:
                print(f"  ERROR: A la tarjeta le falta la clave {clave_que_falta}. Se omite esa tarjeta.")

            except Exception as error_al_crear_tarjeta:
                print(f"  ERROR inesperado al crear una tarjeta: {error_al_crear_tarjeta}. Se omite.")


    # -------------------------------------------------------
    # Getters de las listas (para usar desde afuera)
    # -------------------------------------------------------

    def get_lista_de_productos(self):
        """
        Devuelve la lista completa de objetos Producto cargados en la maquina.

        Eficiencia: O(1) - devuelve la referencia a la lista existente.
        """
        return self.lista_de_productos

    def get_lista_de_tarjetas(self):
        """
        Devuelve la lista completa de objetos Tarjeta cargados en la maquina.

        Eficiencia: O(1) - devuelve la referencia a la lista existente.
        """
        return self.lista_de_tarjetas


    # =======================================================
    # LOGICA DEL BUCLE PRINCIPAL Y MENU
    # =======================================================

    def iniciar(self):
        """
        Motor principal de la maquina expendedora.

        Muestra el menu de opciones y mantiene un bucle while que se ejecuta
        hasta que el usuario escriba 'salir'. En cada iteracion muestra el
        catalogo, pide una entrada y enruta a la funcion correspondiente:
        - Codigo de producto: consulta el precio
        - ENTER en blanco: inicia una venta
        - RS: abre el menu de restock
        - RP: genera el reporte de estadisticas

        Eficiencia: el bucle en si es O(1) por iteracion (sin contar las
        operaciones internas de cada opcion). La cantidad de iteraciones
        depende del usuario. mostrar_catalogo() se llama en cada iteracion
        y es O(filas * columnas * n) donde n es la cantidad de productos.
        """
        # Este es el motor principal de la maquina expendedora.
        # El programa vive aca adentro hasta que el usuario escriba "salir".

        print("")
        print("=" * 50)
        print("   BIENVENIDO A LA MAQUINA EXPENDEDORA")
        print("=" * 50)
        print("  Ingrese un CODIGO de producto para ver el precio.")
        print("  Deje la linea en BLANCO y presione Enter para comprar.")
        print("  Escriba  RS  para hacer un restock.")
        print("  Escriba  RP  para ver el reporte.")
        print("  Escriba  salir  para apagar la maquina.")
        print("=" * 50)

        la_maquina_esta_encendida = True

        while la_maquina_esta_encendida:

            # Mostramos el catalogo de productos antes de pedir opciones
            self.mostrar_catalogo()

            # Capturamos lo que escribe el usuario de forma robusta
            entrada_del_usuario = self.pedir_entrada_al_usuario()

            # Ahora revisamos que escribio y enrutamos a la funcion correcta
            if entrada_del_usuario == "salir":
                # El usuario quiere apagar la maquina
                print("")
                print("Apagando la maquina... Hasta luego!")
                la_maquina_esta_encendida = False

            elif entrada_del_usuario == "":
                # El usuario dejo la linea en blanco -> quiere hacer una compra
                print("")
                print(">> Modo VENTA activado.")
                self.procesar_venta()

            elif entrada_del_usuario == "RS":
                # El usuario escribio RS -> quiere hacer un restock
                print("")
                print(">> Modo RESTOCK activado.")
                self.realizar_restock()

            elif entrada_del_usuario == "RP":
                # El usuario escribio RP -> quiere ver el reporte
                print("")
                print(">> Modo REPORTE activado.")
                self.generar_reporte()

            else:
                # Asumimos que el usuario escribio un codigo de producto
                # Llamamos a consultar_precio() con lo que escribio
                self.consultar_precio(entrada_del_usuario)


    def pedir_entrada_al_usuario(self):
        """
        Solicita una entrada por teclado al usuario y la normaliza.

        Maneja los comandos especiales (RS, RP, salir) de forma
        case-insensitive, y devuelve el texto limpio (sin espacios
        al inicio/fin). Captura EOFError y KeyboardInterrupt para
        cerrar la maquina de forma segura si ocurren.

        Retorna:
            str: El texto ingresado por el usuario, normalizado.
            Devuelve 'salir' si hubo un error de entrada.

        Eficiencia: O(1) - solo lee un input, le saca espacios con
        strip() y hace comparaciones de strings constantes.
        """
        # Esta funcion se encarga de pedir el input y manejarlo de forma segura.
        # La separamos en su propia funcion para mantener iniciar() limpio.

        entrada_valida = None

        while entrada_valida is None:
            try:
                print("")
                texto_del_prompt = input("Ingrese opcion (codigo / ENTER / RS / RP / salir): ")

                # Le sacamos los espacios al principio y al final por si el usuario
                # apreta la barra espaciadora de mas, pero SIN convertir a mayusculas
                # todavia, porque el codigo de producto podria ser minuscula
                texto_limpio = texto_del_prompt.strip()

                # Convertimos a mayusculas solo los comandos especiales
                # Si escribio "rs" o "rp" en minuscula, igual lo aceptamos
                if texto_limpio.lower() == "rs":
                    entrada_valida = "RS"
                elif texto_limpio.lower() == "rp":
                    entrada_valida = "RP"
                elif texto_limpio.lower() == "salir":
                    entrada_valida = "salir"
                else:
                    # Para el codigo de producto y el ENTER en blanco, lo devolvemos como esta
                    entrada_valida = texto_limpio

            except EOFError:
                # Esto pasa si el programa se ejecuta sin una terminal real (ej: redireccion)
                print("ERROR: No se pudo leer la entrada. Cerrando maquina...")
                entrada_valida = "salir"

            except KeyboardInterrupt:
                # El usuario aperto Ctrl+C
                print("")
                print("Interrupcion detectada. Cerrando maquina...")
                entrada_valida = "salir"

        return entrada_valida


    def consultar_precio(self, codigo_ingresado_por_el_usuario):
        """
        Busca un producto por su codigo y muestra su precio y stock en pantalla.

        Si el producto existe, imprime nombre, precio y disponibilidad.
        Si no lo encuentra, muestra un mensaje de error al usuario.

        Parametros:
            codigo_ingresado_por_el_usuario (str): El codigo que el usuario
            escribio en el prompt.

        Eficiencia: O(n) donde n es la cantidad de productos, porque
        internamente llama a buscar_producto_por_codigo() que recorre
        la lista de forma lineal.
        """
        # Busca un producto en la lista por su codigo y muestra el precio.
        # Si no lo encuentra, avisa al usuario.

        producto_encontrado = self.buscar_producto_por_codigo(codigo_ingresado_por_el_usuario)

        if producto_encontrado is not None:
            # Mostramos la info del producto
            nombre_del_producto_encontrado = producto_encontrado.get_nombre()
            precio_del_producto_encontrado = producto_encontrado.get_precio()
            stock_del_producto_encontrado  = producto_encontrado.get_stock()

            print("")
            print(f"  Producto: {nombre_del_producto_encontrado}")
            print(f"  Precio:   ${precio_del_producto_encontrado}")

            # Tambien avisamos si hay stock o no
            if producto_encontrado.hay_stock():
                print(f"  Stock:    {stock_del_producto_encontrado} unidades disponibles")
            else:
                print("  Stock:    SIN STOCK")

        else:
            # El codigo que escribio el usuario no existe en la lista
            print("")
            print(f"  ERROR: No se encontro ningun producto con el codigo '{codigo_ingresado_por_el_usuario}'.")
            print("  Revise el codigo e intente de nuevo.")


    def buscar_producto_por_codigo(self, codigo_a_buscar):
        """
        Recorre la lista de productos buscando uno que tenga el codigo indicado.

        La comparacion se hace en mayusculas para que no importe si el usuario
        escribio en minuscula o mayuscula. Usa un break para detenerse apenas
        encuentra el primer producto que coincide.

        Parametros:
            codigo_a_buscar (str): El codigo del producto a buscar.

        Retorna:
            Producto o None: El objeto Producto encontrado, o None si
            ningun producto tiene ese codigo.

        Eficiencia: O(n) en el peor caso, donde n es la cantidad de productos
        en la lista. En el mejor caso (el producto esta al principio), se
        detiene en la primera iteracion gracias al break.
        """
        # Recorre la lista de productos buscando uno que tenga ese codigo.
        # Si lo encuentra, devuelve el objeto Producto.
        # Si no lo encuentra, devuelve None.

        producto_que_buscamos = None

        try:
            for producto_de_la_lista in self.lista_de_productos:
                codigo_del_producto_actual = producto_de_la_lista.get_codigo()

                # Comparamos en mayusculas para que no importe si el usuario
                # escribio el codigo en minuscula o mayuscula
                if str(codigo_del_producto_actual).upper() == str(codigo_a_buscar).upper():
                    producto_que_buscamos = producto_de_la_lista
                    break   # ya lo encontramos, no hace falta seguir buscando

        except Exception as error_al_buscar:
            print(f"  ERROR inesperado al buscar el producto: {error_al_buscar}")

        return producto_que_buscamos


    # =======================================================
    # LOGICA PARA MOSTRAR LA VITRINA
    # =======================================================

    def mostrar_catalogo(self):
        """
        Dibuja la vitrina de la maquina expendedora en la consola.

        La vitrina tiene 4 filas (numeradas 1-4) y 3 columnas (letras A-C).
        Para cada celda de la vitrina, recorre la lista completa de productos
        buscando cual tiene esa posicion asignada. Solo muestra el codigo
        si el producto tiene stock mayor a 0.

        Eficiencia: O(filas * columnas * n) donde n es la cantidad de productos.
        Para cada celda de la vitrina (4 * 3 = 12 celdas) se recorre toda la
        lista de productos buscando coincidencia de posicion. Con 51 productos,
        esto da aproximadamente 612 comparaciones, lo cual es aceptable para
        una operacion de visualizacion en consola.
        """
        # Dibuja la vitrina en pantalla.
        # La maquina tiene 4 filas (numeradas 1-4) y 3 columnas (letras A-C)

        print("")
        print("+" + "-"*47 + "+")
        print("|" + "VITRINA DE LA MAQUINA EXPENDEDORA".center(47) + "|")
        print("+" + "-"*47 + "+")

        numeros_de_filas = [1, 2, 3, 4]
        letras_de_columnas = ["A", "B", "C"]

        # Imprimimos el encabezado con las letras de las columnas
        encabezado = "    "
        for letra_columna in letras_de_columnas:
            encabezado += f"Columna {letra_columna}".center(14)
        print(encabezado)

        # Recorremos cada fila y cada columna de la vitrina
        for indice_fila, numero_fila in enumerate(numeros_de_filas):
            fila_texto = f" {numero_fila} |"
            
            for indice_col, letra_col in enumerate(letras_de_columnas):
                
                producto_en_esta_posicion = None
                
                # Buscamos en toda la lista si algun producto tiene esta posicion
                for producto_actual in self.lista_de_productos:
                    posicion_del_producto = producto_actual.get_posicion()
                    
                    # Verificamos que tenga posicion y coincida con nuestra celda actual
                    if posicion_del_producto is not None:
                        if posicion_del_producto == (indice_fila, indice_col):
                            producto_en_esta_posicion = producto_actual
                            break
                            
                # Verificamos si encontramos producto y si tiene stock > 0
                if producto_en_esta_posicion is not None and producto_en_esta_posicion.get_stock() > 0:
                    codigo_a_mostrar = producto_en_esta_posicion.get_codigo()
                    fila_texto += f" {codigo_a_mostrar:^10} |"
                else:
                    # Si no hay producto, o el stock es 0, imprimimos espacio en blanco
                    fila_texto += "            |"
                    
            print(fila_texto)
            print("   +" + "-"*41 + "+")


    # =======================================================
    # LOGICA DE VENTA DE PRODUCTOS
    # =======================================================

    def procesar_venta(self):
        """
        Gestiona el proceso completo de venta de un producto.

        Solicita al usuario el codigo del producto, verifica stock,
        pide el numero de tarjeta, aplica hash para buscar al cliente,
        verifica saldo, pide confirmacion y si todo sale bien:
        1. Descuenta el saldo de la tarjeta
        2. Descuenta 1 unidad del stock
        3. Muestra el mensaje de despedida
        4. Registra la transaccion en ventas.txt usando la clase Venta

        Eficiencia: O(n + m) donde n es la cantidad de productos y m la
        cantidad de tarjetas, porque hace una busqueda lineal en cada
        lista (buscar_producto_por_codigo y buscar tarjeta por hash).
        Las operaciones de descuento y escritura en archivo son O(1).
        """
        # Primero pedimos el codigo del producto a comprar
        codigo_ingresado_por_usuario = input("  Ingrese el codigo del producto que desea comprar: ")
        
        producto_encontrado_para_vender = self.buscar_producto_por_codigo(codigo_ingresado_por_usuario)
        
        if producto_encontrado_para_vender is None:
            print(f"  ERROR: El codigo '{codigo_ingresado_por_usuario}' no existe.")
            return
            
        if not producto_encontrado_para_vender.hay_stock():
            print("  ERROR: Producto sin stock por el momento.")
            return

        # Solicitamos el numero de tarjeta al cliente
        texto_de_la_tarjeta = input("  Ingrese su numero de tarjeta para pagar: ")
        
        # Aplicamos la funcion hash de Python como nos pidieron.
        # Intentamos convertir a int primero, porque si el JSON tiene
        # el ID como numero, el hash(int) coincidira con ese numero.
        try:
            numero_de_tarjeta_entero = int(texto_de_la_tarjeta)
            hash_generado_de_la_tarjeta = hash(numero_de_tarjeta_entero)
        except ValueError:
            # Si escribio letras, le aplicamos hash al string directo
            hash_generado_de_la_tarjeta = hash(texto_de_la_tarjeta)
            
        # Comparamos el hash con los hash_numero de los clientes cargados
        tarjeta_del_cliente_encontrada = None
        
        for tarjeta_actual in self.lista_de_tarjetas:
            if tarjeta_actual.get_hash_numero() == hash_generado_de_la_tarjeta:
                tarjeta_del_cliente_encontrada = tarjeta_actual
                break
                
        if tarjeta_del_cliente_encontrada is None:
            print("  ERROR: Tarjeta invalida o no registrada en el sistema.")
            return
            
        # Revisamos si tiene saldo suficiente
        precio_del_producto = producto_encontrado_para_vender.get_precio()
        
        if not tarjeta_del_cliente_encontrada.tiene_saldo(precio_del_producto):
            print("  ERROR: Saldo insuficiente en la tarjeta.")
            return
            
        # Pedimos confirmacion de compra
        print("")
        print(f"  Producto seleccionado: {producto_encontrado_para_vender.get_nombre()}")
        print(f"  Precio a cobrar: ${precio_del_producto}")
        print(f"  Saldo actual en tarjeta: ${tarjeta_del_cliente_encontrada.get_saldo()}")
        respuesta_de_confirmacion = input("  ¿Confirma la compra? (S/N): ")
        
        # Le sacamos los espacios y la pasamos a mayuscula para que sea mas facil validar
        if respuesta_de_confirmacion.strip().upper() == "S":
            
            # 1. Aplicamos descontar_saldo()
            tarjeta_del_cliente_encontrada.descontar_saldo(precio_del_producto)
            
            # 2. Descontamos el stock del producto
            stock_actual = producto_encontrado_para_vender.get_stock()
            producto_encontrado_para_vender.set_stock(stock_actual - 1)
            
            # 3. Imprimimos el mensaje de la variable despedida
            print("")
            print("  >> COMPRA EXITOSA <<")
            print(f"  {producto_encontrado_para_vender.get_despedida()}")
            print(f"  Su nuevo saldo es: ${tarjeta_del_cliente_encontrada.get_saldo()}")
            
            # 4. Escribimos la transaccion en el archivo usando la clase Venta
            try:
                # Creamos el objeto Venta (cantidad siempre es 1 en este caso)
                nueva_venta = Venta(producto_encontrado_para_vender, tarjeta_del_cliente_encontrada, 1)
                
                # Obtenemos el texto listo llamando al metodo que armamos antes
                texto_para_guardar = nueva_venta.guardar_venta_txt()
                
                # Abrimos el archivo en modo "a" (append) para no borrar lo anterior
                archivo_de_ventas = open("ventas.txt", "a", encoding="utf-8")
                archivo_de_ventas.write(texto_para_guardar)
                archivo_de_ventas.close()
                
            except Exception as error_al_guardar_venta:
                print(f"  ERROR interno: No se pudo guardar el registro de la venta. Detalles: {error_al_guardar_venta}")
                
        else:
            print("  Compra cancelada por el usuario.")


    # =======================================================
    # LOGICA DE REABASTECIMIENTO (RESTOCK)
    # =======================================================

    def realizar_restock(self):
        """
        Despliega el menu interactivo de reabastecimiento.

        Ofrece tres opciones en un bucle:
        1. Asignar o cambiar la posicion de un producto en la vitrina
        2. Agregar stock a un producto existente
        3. Salir del menu de restock

        Eficiencia: O(1) por iteracion del menu en si. Las operaciones
        internas (asignar posicion o agregar stock) dependen de la busqueda
        del producto, que es O(n).
        """
        # Este metodo despliega el menu de reabastecimiento
        
        en_menu_de_restock = True
        
        while en_menu_de_restock:
            print("\n" + "=" * 40)
            print("         MENU DE RESTOCK")
            print("=" * 40)
            print("  1. Asignar/Cambiar producto en vitrina")
            print("  2. Actualizar existencia (Agregar stock)")
            print("  3. Salir del menu de restock")
            print("=" * 40)
            
            opcion_elegida = input("  Seleccione una opcion (1-3): ")
            
            if opcion_elegida == "1":
                self.asignar_posicion_a_producto()
                
            elif opcion_elegida == "2":
                self.agregar_stock_a_producto()
                
            elif opcion_elegida == "3":
                print("  Saliendo del menu de restock...")
                en_menu_de_restock = False
                
            else:
                print("  ERROR: Opcion invalida. Intente de nuevo.")


    def asignar_posicion_a_producto(self):
        """
        Permite al usuario asignar una posicion (fila y columna) a un producto
        en la vitrina de la maquina.

        Pide el codigo del producto, la letra de columna (A-C) y el numero
        de fila (1-4). Mapea la letra a un indice numerico usando un
        diccionario y guarda la posicion como tupla. Luego guarda el
        inventario completo en el archivo TXT local.

        Eficiencia: O(n) para buscar el producto por codigo, mas O(n) para
        guardar el inventario en el archivo TXT. El mapeo de columna usa
        un diccionario con acceso O(1).
        """
        # Le pide al usuario el codigo y le asigna una fila y columna
        codigo_del_producto = input("\n  Ingrese el codigo del producto a posicionar: ")
        producto_a_modificar = self.buscar_producto_por_codigo(codigo_del_producto)
        
        if producto_a_modificar is not None:
            print("  La vitrina tiene columnas A, B, C y filas 1, 2, 3, 4.")
            letra_de_columna = input("  Ingrese la letra de la columna (ej. A): ").strip().upper()
            numero_de_fila = input("  Ingrese el numero de la fila (ej. 1): ").strip()
            
            # Mapeamos la letra de columna a un indice numerico (0-2)
            diccionario_de_columnas = {"A": 0, "B": 1, "C": 2}
            
            try:
                # Validamos que la fila y la columna esten dentro del rango
                if letra_de_columna in diccionario_de_columnas and numero_de_fila in ["1", "2", "3", "4"]:
                    indice_fila = int(numero_de_fila) - 1
                    indice_col = diccionario_de_columnas[letra_de_columna]
                    
                    # Guardamos la tupla (indice_fila, indice_col)
                    producto_a_modificar.set_posicion((indice_fila, indice_col))
                    
                    print(f"  EXITO: Producto '{producto_a_modificar.get_nombre()}' posicionado en {letra_de_columna}{numero_de_fila}.")
                    self.guardar_inventario_en_archivo_de_texto()
                else:
                    print("  ERROR: Fila o columna fuera de rango.")
            except Exception as error_posicion:
                print(f"  ERROR inesperado al posicionar: {error_posicion}")
                
        else:
            print("  ERROR: Producto no encontrado en la lista.")


    def agregar_stock_a_producto(self):
        """
        Aumenta el stock de un producto y registra la operacion.

        Pide al usuario el codigo del producto y la cantidad de unidades
        a agregar. Valida que la cantidad sea un entero positivo.
        Si todo es correcto, actualiza el stock, crea un registro Restock,
        lo guarda en restock.txt y actualiza el inventario en productos.txt.

        Eficiencia: O(n) para buscar el producto, mas O(n) para guardar el
        inventario. La escritura del registro de restock en archivo es O(1)
        porque usa modo append.
        """
        # Aumenta el stock de un producto y guarda el registro
        codigo_del_producto = input("\n  Ingrese el codigo del producto a reabastecer: ")
        producto_a_reabastecer = self.buscar_producto_por_codigo(codigo_del_producto)
        
        if producto_a_reabastecer is not None:
            cantidad_en_texto = input("  Ingrese la cantidad de unidades a agregar: ")
            try:
                cantidad_a_sumar = int(cantidad_en_texto)
                
                if cantidad_a_sumar > 0:
                    stock_viejo = producto_a_reabastecer.get_stock()
                    producto_a_reabastecer.set_stock(stock_viejo + cantidad_a_sumar)
                    
                    print(f"  EXITO: Stock actualizado. Ahora hay {producto_a_reabastecer.get_stock()} unidades.")
                    
                    # Registramos el restock usando nuestra clase Restock
                    nuevo_registro_restock = Restock(producto_a_reabastecer, cantidad_a_sumar)
                    texto_para_archivo = nuevo_registro_restock.guardar_restock_txt()
                    
                    # Guardamos en restock.txt (modo append)
                    archivo_de_restock = open("restock.txt", "a", encoding="utf-8")
                    archivo_de_restock.write(texto_para_archivo)
                    archivo_de_restock.close()
                    
                    # Guardamos tambien el estado final del inventario
                    self.guardar_inventario_en_archivo_de_texto()
                    
                else:
                    print("  ERROR: La cantidad debe ser un numero mayor a cero.")
                    
            except ValueError:
                print("  ERROR: Debe ingresar un numero entero valido.")
        else:
            print("  ERROR: Producto no encontrado.")


    def guardar_inventario_en_archivo_de_texto(self):
        """
        Guarda todo el inventario actual en el archivo productos.txt.

        Recorre la lista completa de productos y escribe una linea por cada
        uno con el formato: cod;prod;precio;despedida;stock;fila;columna.
        Si un producto no tiene posicion asignada, guarda -1 en fila y columna.
        Usa modo 'w' (escritura) para sobrescribir el archivo completo,
        asegurando que el archivo siempre refleje el estado actual de la maquina.

        Eficiencia: O(n) donde n es la cantidad de productos. Recorre la lista
        una sola vez y escribe una linea por producto. La apertura y cierre
        del archivo es O(1).
        """
        # Este metodo guarda todo el inventario de nuevo en el archivo productos.txt
        # El formato guardado es: cod;prod;precio;despedida;stock;fila;columna
        # para que en futuras ejecuciones la maquina "recuerde" posiciones y stock.
        
        try:
            # Guardamos el archivo local de productos (modo "w")
            archivo_local_inventario = open(RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS, "w", encoding="utf-8")
            
            for producto_actual in self.lista_de_productos:
                codigo_del_producto = producto_actual.get_codigo()
                nombre_del_producto = producto_actual.get_nombre()
                precio_del_producto = producto_actual.get_precio()
                despedida_del_producto = producto_actual.get_despedida()
                stock_del_producto = producto_actual.get_stock()
                
                posicion_del_producto = producto_actual.get_posicion()
                if posicion_del_producto is not None:
                    fila_del_producto = posicion_del_producto[0]
                    columna_del_producto = posicion_del_producto[1]
                else:
                    fila_del_producto = -1
                    columna_del_producto = -1
                
                # Unimos todos los datos con punto y coma
                linea_para_guardar = f"{codigo_del_producto};{nombre_del_producto};{precio_del_producto};{despedida_del_producto};{stock_del_producto};{fila_del_producto};{columna_del_producto}\n"
                archivo_local_inventario.write(linea_para_guardar)
                
            archivo_local_inventario.close()
            
            print("  (Inventario guardado en archivo de texto local exitosamente para futuras ejecuciones)")
            
        except Exception as error_al_escribir_txt:
            print(f"  ERROR interno al guardar inventario en TXT: {error_al_escribir_txt}")


    # =======================================================
    # LOGICA DE ESTADISTICAS Y GRAFICOS
    # =======================================================

    def generar_reporte(self):
        """
        Genera un reporte completo de estadisticas de la maquina expendedora.

        Lee los archivos ventas.txt y restock.txt para extraer datos historicos,
        luego genera:
        1. Un archivo de texto (reporte_estadisticas.txt) con productos
           colocados vs vendidos, recaudacion total y gasto por cliente.
        2. Tres graficos PNG con matplotlib:
           - Barras: productos colocados vs vendidos
           - Circular: porcentaje de gasto por cliente
           - Lineas: tendencia de ventas diarias

        Usa diccionarios como acumuladores para sumar cantidades por codigo
        de producto, por tarjeta y por fecha. Evita el uso de set() y list
        comprehensions para mantener el estilo de primer semestre.

        Eficiencia: O(v + r + c) donde v es la cantidad de lineas en ventas.txt,
        r la cantidad de lineas en restock.txt, y c la cantidad de codigos
        unicos procesados. Las busquedas en diccionarios son O(1) en promedio.
        La generacion de graficos con matplotlib tiene costo adicional pero
        es constante respecto al tamano de los datos.
        """
        print("  Generando reporte de estadisticas...")
        
        # Diccionarios acumuladores para las estadisticas
        diccionario_vendidos = {}
        diccionario_colocados = {}
        gasto_por_cliente = {}
        ventas_por_fecha = {}
        recaudacion_total = 0.0
        
        # 1. Leer y extraer datos del archivo de ventas
        try:
            archivo_ventas = open("ventas.txt", "r", encoding="utf-8")
            lineas_ventas = archivo_ventas.readlines()
            archivo_ventas.close()
            
            # Vamos a ir guardando los datos de la transaccion que estamos leyendo
            transaccion_actual = {}
            for linea in lineas_ventas:
                linea_limpia = linea.strip()
                
                if linea_limpia.startswith("Fecha y hora: "):
                    transaccion_actual["fecha"] = linea_limpia.replace("Fecha y hora: ", "")
                    
                elif linea_limpia.startswith("Producto: "):
                    partes = linea_limpia.split("(Cod: ")
                    codigo_del_producto = partes[1].replace(")", "")
                    transaccion_actual["codigo"] = codigo_del_producto
                    
                elif linea_limpia.startswith("Cantidad vendida: "):
                    transaccion_actual["cantidad"] = int(linea_limpia.replace("Cantidad vendida: ", ""))
                    
                elif linea_limpia.startswith("Total cobrado: $"):
                    transaccion_actual["monto"] = float(linea_limpia.replace("Total cobrado: $", ""))
                    
                elif linea_limpia.startswith("Tarjeta del cliente: "):
                    transaccion_actual["tarjeta"] = linea_limpia.replace("Tarjeta del cliente: ", "")
                    
                    # Como la tarjeta es la ultima linea de cada bloque de venta, 
                    # aca ya tenemos todos los datos de esa venta particular y acumulamos
                    codigo = transaccion_actual["codigo"]
                    cantidad = transaccion_actual["cantidad"]
                    monto = transaccion_actual["monto"]
                    tarjeta = transaccion_actual["tarjeta"]
                    fecha = transaccion_actual["fecha"].split(" ")[0] # sacamos solo el dia
                    
                    if codigo not in diccionario_vendidos:
                        diccionario_vendidos[codigo] = 0
                    diccionario_vendidos[codigo] += cantidad
                    
                    if tarjeta not in gasto_por_cliente:
                        gasto_por_cliente[tarjeta] = 0.0
                    gasto_por_cliente[tarjeta] += monto
                    
                    if fecha not in ventas_por_fecha:
                        ventas_por_fecha[fecha] = 0
                    ventas_por_fecha[fecha] += cantidad
                    
                    recaudacion_total += monto
                    # Limpiamos el diccionario para la proxima vuelta
                    transaccion_actual = {}
                    
        except FileNotFoundError:
            print("  ADVERTENCIA: No se encontro archivo 'ventas.txt'. Tal vez no hay ventas aun.")
        except Exception as error_leer_ventas:
            print(f"  ERROR al leer ventas: {error_leer_ventas}")


        # 2. Leer y extraer datos del archivo de restock
        try:
            archivo_restock = open("restock.txt", "r", encoding="utf-8")
            lineas_restock = archivo_restock.readlines()
            archivo_restock.close()
            
            transaccion_restock_actual = {}
            for linea in lineas_restock:
                linea_limpia = linea.strip()
                
                if linea_limpia.startswith("Producto: "):
                    partes = linea_limpia.split("(Cod: ")
                    codigo_del_producto = partes[1].replace(")", "")
                    transaccion_restock_actual["codigo"] = codigo_del_producto
                    
                elif linea_limpia.startswith("Cantidad repuesta: "):
                    cantidad = int(linea_limpia.replace("Cantidad repuesta: ", ""))
                    codigo = transaccion_restock_actual["codigo"]
                    
                    if codigo not in diccionario_colocados:
                        diccionario_colocados[codigo] = 0
                    diccionario_colocados[codigo] += cantidad
                    
        except FileNotFoundError:
            print("  ADVERTENCIA: No se encontro archivo 'restock.txt'. Tal vez no hay restock aun.")
        except Exception as error_leer_restock:
            print(f"  ERROR al leer restock: {error_leer_restock}")


        # 3. Generar el reporte .txt
        try:
            archivo_reporte = open("reporte_estadisticas.txt", "w", encoding="utf-8")
            archivo_reporte.write("=" * 40 + "\n")
            archivo_reporte.write("      REPORTE DE ESTADISTICAS\n")
            archivo_reporte.write("=" * 40 + "\n\n")
            
            archivo_reporte.write("1. PRODUCTOS COLOCADOS VS VENDIDOS\n")
            
            # Buscamos todos los codigos sin usar sets (estilo primer semestre)
            todos_los_codigos_procesados = []
            
            for codigo_colocado in diccionario_colocados.keys():
                if codigo_colocado not in todos_los_codigos_procesados:
                    todos_los_codigos_procesados.append(codigo_colocado)
                    
            for codigo_vendido in diccionario_vendidos.keys():
                if codigo_vendido not in todos_los_codigos_procesados:
                    todos_los_codigos_procesados.append(codigo_vendido)
            
            for cod in todos_los_codigos_procesados:
                
                # Buscamos en el diccionario sin usar .get()
                if cod in diccionario_colocados:
                    cantidad_colocados = diccionario_colocados[cod]
                else:
                    cantidad_colocados = 0
                    
                if cod in diccionario_vendidos:
                    cantidad_vendidos = diccionario_vendidos[cod]
                else:
                    cantidad_vendidos = 0
                    
                archivo_reporte.write(f"  - Codigo [{cod}]: Colocados = {cantidad_colocados} | Vendidos = {cantidad_vendidos}\n")
                
            archivo_reporte.write(f"\n2. RECAUDACION TOTAL DE LA MAQUINA: ${recaudacion_total:.2f}\n\n")
            
            archivo_reporte.write("3. GASTO POR CADA CLIENTE\n")
            for tarjeta_cliente, gasto in gasto_por_cliente.items():
                archivo_reporte.write(f"  - Tarjeta nro {tarjeta_cliente}: gasto total de ${gasto:.2f}\n")
                
            archivo_reporte.close()
            print("  EXITO: El archivo 'reporte_estadisticas.txt' ha sido generado en texto plano.")
            
        except Exception as error_reporte_txt:
            print(f"  ERROR al escribir el archivo de reporte txt: {error_reporte_txt}")


        # 4. Generar graficos con matplotlib (Puntos Bono)
        try:
            # matplotlib.pyplot ya fue importado al principio del archivo
            
            # Usamos nuestra lista creada manualmente en vez de list()
            lista_codigos = todos_los_codigos_procesados
            if len(lista_codigos) > 0:
                
                # Gráfico 1: Barras (Colocados vs Vendidos)
                valores_colocados = []
                valores_vendidos = []
                posiciones_x_menos = []
                posiciones_x_mas = []
                
                ancho = 0.35
                
                # Llenamos las listas con un for clasico en vez de list comprehensions
                posicion_actual = 0
                for c in lista_codigos:
                    if c in diccionario_colocados:
                        valores_colocados.append(diccionario_colocados[c])
                    else:
                        valores_colocados.append(0)
                        
                    if c in diccionario_vendidos:
                        valores_vendidos.append(diccionario_vendidos[c])
                    else:
                        valores_vendidos.append(0)
                        
                    posiciones_x_menos.append(posicion_actual - ancho/2)
                    posiciones_x_mas.append(posicion_actual + ancho/2)
                    posicion_actual += 1
                
                x = range(len(lista_codigos))
                
                plt.figure(figsize=(10, 6))
                plt.bar(posiciones_x_menos, valores_colocados, width=ancho, label='Colocados', color='blue')
                plt.bar(posiciones_x_mas, valores_vendidos, width=ancho, label='Vendidos', color='orange')
                
                plt.xticks(x, lista_codigos, rotation=45)
                plt.ylabel('Unidades')
                plt.title('Estadistica: Productos Colocados vs Vendidos')
                plt.legend()
                plt.tight_layout()
                plt.savefig('grafico_1_barras_inventario.png')
                plt.close()
                
            # Gráfico 2: Circular (Gasto por Cliente)
            lista_tarjetas = []
            lista_gastos = []
            for tarjeta_key in gasto_por_cliente.keys():
                lista_tarjetas.append(tarjeta_key)
                lista_gastos.append(gasto_por_cliente[tarjeta_key])
            
            if len(lista_tarjetas) > 0:
                plt.figure(figsize=(8, 8))
                plt.pie(lista_gastos, labels=lista_tarjetas, autopct='%1.1f%%', startangle=140)
                plt.title('Porcentaje de Gasto por Cliente')
                plt.tight_layout()
                plt.savefig('grafico_2_circular_gastos.png')
                plt.close()
                
            # Gráfico 3: Líneas (Ventas en el tiempo)
            lista_fechas = []
            lista_cantidades_por_fecha = []
            for fecha_key in ventas_por_fecha.keys():
                lista_fechas.append(fecha_key)
                lista_cantidades_por_fecha.append(ventas_por_fecha[fecha_key])
            
            if len(lista_fechas) > 0:
                plt.figure(figsize=(10, 6))
                plt.plot(lista_fechas, lista_cantidades_por_fecha, marker='o', linestyle='-', color='green', linewidth=2)
                plt.xlabel('Dias de operacion')
                plt.ylabel('Cantidad de unidades vendidas')
                plt.title('Tendencia de Ventas Diarias')
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()
                plt.savefig('grafico_3_lineas_tendencia.png')
                plt.close()
                
            print("  BONO EXITO: Se generaron 3 graficos (barras, circular, lineas) mediante Matplotlib.")
            print("              Los archivos .png han sido guardados en la carpeta actual.")
            
        except Exception as error_graficos:
            print(f"  ERROR inesperado con Matplotlib: {error_graficos}")
