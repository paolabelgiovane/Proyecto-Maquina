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


    # =======================================================
    # LOGICA PARA MOSTRAR LA VITRINA
    # =======================================================

    def mostrar_catalogo(self):
        # Dibuja la matriz de productos en pantalla (estilo ajedrez).
        # Asumimos una maquina de 4 filas (A, B, C, D) y 3 columnas (1, 2, 3)
        # porque en total tenemos 12 productos en el JSON.

        print("")
        print("+" + "-"*47 + "+")
        print("|" + "VITRINA DE LA MAQUINA EXPENDEDORA".center(47) + "|")
        print("+" + "-"*47 + "+")

        letras_de_filas = ["A", "B", "C", "D"]
        numeros_de_columnas = [1, 2, 3]

        # Imprimimos el encabezado de las columnas
        encabezado = "    "
        for numero_columna in numeros_de_columnas:
            # Centramos cada numero de columna en 12 espacios
            encabezado += f"Columna {numero_columna}".center(14)
        print(encabezado)

        # Recorremos cada fila y cada columna de la matriz
        for indice_fila, letra_fila in enumerate(letras_de_filas):
            fila_texto = f" {letra_fila} |"
            
            for indice_col, numero_col in enumerate(numeros_de_columnas):
                
                producto_en_esta_posicion = None
                
                # Buscamos en toda la lista si algun producto tiene esta posicion
                for producto_actual in self.lista_de_productos:
                    posicion_del_producto = producto_actual.get_posicion()
                    
                    # Verificamos que tenga posicion y coincida con nuestra (fila, columna) actual
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
                # Importamos Venta solo cuando la necesitamos, para evitar referencias circulares
                from operaciones import Venta
                
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
        # Le pide al usuario el codigo y le asigna una fila y columna
        codigo_del_producto = input("\n  Ingrese el codigo del producto a posicionar: ")
        producto_a_modificar = self.buscar_producto_por_codigo(codigo_del_producto)
        
        if producto_a_modificar is not None:
            print("  La vitrina tiene filas A, B, C, D y columnas 1, 2, 3.")
            letra_de_fila = input("  Ingrese la letra de la fila (ej. A): ").strip().upper()
            numero_de_columna = input("  Ingrese el numero de la columna (ej. 1): ").strip()
            
            # Mapeamos la letra a un indice numerico (0-3) para nuestro iterador interno
            diccionario_de_filas = {"A": 0, "B": 1, "C": 2, "D": 3}
            
            try:
                # Validamos que lo ingresado exista en nuestro mapa y en las columnas validas
                if letra_de_fila in diccionario_de_filas and numero_de_columna in ["1", "2", "3"]:
                    indice_fila = diccionario_de_filas[letra_de_fila]
                    indice_col = int(numero_de_columna) - 1  # restamos 1 para manejar indices desde 0 pero esto no es estrictamente necesario si usamos el numero directo, pero es mejor asi.
                    
                    # Guardamos la tupla (indice_fila, indice_col)
                    producto_a_modificar.set_posicion((indice_fila, int(numero_de_columna)))
                    
                    print(f"  EXITO: Producto '{producto_a_modificar.get_nombre()}' posicionado en {letra_de_fila}{numero_de_columna}.")
                    self.guardar_inventario_en_archivo_de_texto()
                else:
                    print("  ERROR: Fila o columna fuera de rango.")
            except Exception as error_posicion:
                print(f"  ERROR inesperado al posicionar: {error_posicion}")
                
        else:
            print("  ERROR: Producto no encontrado en la lista.")


    def agregar_stock_a_producto(self):
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
                    from operaciones import Restock
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
        # Este metodo guarda todo el inventario de nuevo en el archivo productos.json
        # para que en futuras ejecuciones la maquina "recuerde" posiciones y stock.
        
        lista_de_diccionarios_para_json = []
        
        for producto_actual in self.lista_de_productos:
            # Creamos un diccionario a mano para cada producto
            diccionario_del_producto = {
                "cod": producto_actual.get_codigo(),
                "prod": producto_actual.get_nombre(),
                "precio": producto_actual.get_precio(),
                "despedida": producto_actual.get_despedida(),
                "stock": producto_actual.get_stock(),
                "posicion": producto_actual.get_posicion()
            }
            lista_de_diccionarios_para_json.append(diccionario_del_producto)
            
        try:
            # Sobreescribimos el archivo local de productos (modo "w")
            archivo_local_inventario = open("productos.json", "w", encoding="utf-8")
            # Usamos indent=4 para que quede bonito y legible
            json.dump(lista_de_diccionarios_para_json, archivo_local_inventario, indent=4)
            archivo_local_inventario.close()
            
            print("  (Inventario guardado en archivo local exitosamente para futuras ejecuciones)")
            
        except Exception as error_al_escribir_json:
            print(f"  ERROR interno al guardar inventario: {error_al_escribir_json}")

