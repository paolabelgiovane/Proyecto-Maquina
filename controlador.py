# -----------------------------------------------
# Archivo: controlador.py
# Clase: MaquinaExpendedora
# Responsable: Ivana Lopez
# Descripcion: Aca va toda la logica pesada de la
#              maquina expendedora. Esta clase es la
#              que conecta con internet, carga los
#              datos, y coordina todo el resto.
# -----------------------------------------------

# Importamos las librerias que necesitamos
import requests   # para hacer los GET a GitHub
import json       # para leer los archivos locales de respaldo

# Importamos nuestras clases entidad
from producto import Producto
from tarjeta import Tarjeta


# Estas son las URLs de GitHub de donde bajamos los datos
URL_DEL_JSON_DE_PRODUCTOS = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/productos.json"
URL_DEL_JSON_DE_CLIENTES  = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/clientes.json"

# Estos son los archivos locales de respaldo, por si no hay internet
RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS = "productos.json"
RUTA_DEL_ARCHIVO_LOCAL_DE_CLIENTES  = "clientes.json"


class MaquinaExpendedora:

    def __init__(self):
        # Usamos listas para guardar todos los objetos, como dice el estilo del proyecto
        self.lista_de_productos = []
        self.lista_de_tarjetas  = []

        # Llamamos a cargar datos cuando se crea la maquina
        self.cargar_datos_iniciales()


    # =======================================================
    # LOGICA DE CARGA DE DATOS
    # =======================================================
    def cargar_datos_iniciales(self):
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
    # Funciones modulares para cargar productos
    # -------------------------------------------------------

    def cargar_lista_de_productos(self):
        # Intenta bajar el JSON de productos de GitHub
        # Si falla, llama a la funcion que lee el archivo local

        datos_crudos_de_productos = None

        try:
            print("  Conectando a GitHub para bajar productos...")
            respuesta_del_servidor = requests.get(URL_DEL_JSON_DE_PRODUCTOS, timeout=10)

            # Si el servidor devolvio un error (ej: 404, 500), esto lanza una excepcion
            respuesta_del_servidor.raise_for_status()

            datos_crudos_de_productos = respuesta_del_servidor.json()
            print("  Productos descargados de GitHub correctamente.")

        except requests.exceptions.ConnectionError:
            # No hay internet o no se pudo conectar
            print("  ERROR: No se pudo conectar a internet.")
            print("  Usando archivo local de respaldo para productos...")
            datos_crudos_de_productos = self.leer_json_local_de_productos()

        except requests.exceptions.Timeout:
            # La conexion tardo demasiado y se corto
            print("  ERROR: La conexion con GitHub tardo demasiado (timeout).")
            print("  Usando archivo local de respaldo para productos...")
            datos_crudos_de_productos = self.leer_json_local_de_productos()

        except requests.exceptions.HTTPError as error_http:
            # El servidor respondio pero con un codigo de error (404, 500, etc)
            print(f"  ERROR HTTP al bajar productos: {error_http}")
            print("  Usando archivo local de respaldo para productos...")
            datos_crudos_de_productos = self.leer_json_local_de_productos()

        except requests.exceptions.RequestException as error_general_de_requests:
            # Cualquier otro error de la libreria requests que no cubrimos arriba
            print(f"  ERROR inesperado de requests: {error_general_de_requests}")
            print("  Usando archivo local de respaldo para productos...")
            datos_crudos_de_productos = self.leer_json_local_de_productos()

        # Si pudimos obtener datos (de internet o del archivo local), instanciamos los objetos
        if datos_crudos_de_productos is not None:
            self.instanciar_objetos_producto(datos_crudos_de_productos)
        else:
            print("  ADVERTENCIA: No se pudieron cargar los productos por ninguna via.")


    def leer_json_local_de_productos(self):
        # Lee el archivo JSON local de productos y devuelve los datos
        # Si el archivo tampoco existe, devuelve None

        datos_leidos_del_archivo = None

        try:
            archivo_local_de_productos = open(RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS, "r", encoding="utf-8")
            datos_leidos_del_archivo = json.load(archivo_local_de_productos)
            archivo_local_de_productos.close()
            print("  Archivo local de productos leido correctamente.")

        except FileNotFoundError:
            print(f"  ERROR: Tampoco existe el archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS}'.")

        except json.JSONDecodeError:
            print(f"  ERROR: El archivo local '{RUTA_DEL_ARCHIVO_LOCAL_DE_PRODUCTOS}' tiene un formato JSON invalido.")

        except Exception as error_al_leer_archivo:
            print(f"  ERROR inesperado al leer el archivo local de productos: {error_al_leer_archivo}")

        return datos_leidos_del_archivo


    def instanciar_objetos_producto(self, lista_de_datos_de_productos):
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

                self.lista_de_productos.append(nuevo_objeto_producto)

            except KeyError as clave_que_falta:
                # Si al diccionario le falta alguna clave, avisamos y seguimos con el proximo
                print(f"  ERROR: Al producto le falta la clave {clave_que_falta}. Se omite ese producto.")

            except Exception as error_al_instanciar_producto:
                print(f"  ERROR inesperado al crear un producto: {error_al_instanciar_producto}. Se omite.")


    # -------------------------------------------------------
    # Funciones modulares para cargar tarjetas (clientes)
    # -------------------------------------------------------

    def cargar_lista_de_tarjetas(self):
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
            self.instanciar_objetos_tarjeta(datos_crudos_de_clientes)
        else:
            print("  ADVERTENCIA: No se pudieron cargar los clientes por ninguna via.")


    def leer_json_local_de_clientes(self):
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


    def instanciar_objetos_tarjeta(self, lista_de_datos_de_clientes):
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

            except Exception as error_al_instanciar_tarjeta:
                print(f"  ERROR inesperado al crear una tarjeta: {error_al_instanciar_tarjeta}. Se omite.")


    # -------------------------------------------------------
    # Getters de las listas (para usar desde afuera)
    # -------------------------------------------------------

    def get_lista_de_productos(self):
        return self.lista_de_productos

    def get_lista_de_tarjetas(self):
        return self.lista_de_tarjetas


    # =======================================================
    # LOGICA DEL BUCLE PRINCIPAL Y MENU
    # =======================================================

    def iniciar(self):
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
                # Por ahora avisamos que esta funcion viene en el proximo avance
                print("   (La logica de venta se implementa en el la proxima entrega)")

            elif entrada_del_usuario == "RS":
                # El usuario escribio RS -> quiere hacer un restock
                print("")
                print(">> Modo RESTOCK activado.")
                # Por ahora avisamos que esta funcion viene en el proximo avance
                print("   (La logica de restock se implementa en el la proxima entrega)")

            elif entrada_del_usuario == "RP":
                # El usuario escribio RP -> quiere ver el reporte
                print("")
                print(">> Modo REPORTE activado.")
                # Por ahora avisamos que esta funcion viene en el proximo avance
                print("   (La logica de reporte se implementa en el la proxima entrega)")

            else:
                # Asumimos que el usuario escribio un codigo de producto
                # Llamamos a consultar_precio() con lo que escribio
                self.consultar_precio(entrada_del_usuario)


    def pedir_entrada_al_usuario(self):
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
