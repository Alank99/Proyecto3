from Parser import *
from globalTypes import *

#Archivo donde se genera la tabla de simbolos y checa la semantica
#imprime la tabla de simbolos y la tabla de funciones
#Creado para C- 
#Creado por: Alan Anthony Hernandez Perez
#Creado el: 13/05/2025
#con el asistente de copilot de vscode

#Operadores logicos que se pueden usar en el lenguaje
OPERADORES_LOGICOS = ["==", "!=", "<", "<=", ">", ">="]
# Definición de variable que checa si existe la función main
#con el proposito de semantica
MAIN_EXISTE = False

#funcion ver si una variable es un array
def es_array(nodo):
    return nodo.longitud is not None

#region Preorden
#Funcion que recorre el arbol en preorden y genera la tabla de simbolos
#donde al iniciar el recorrido siempre el ambito es global
def recorrer_preorden(nodo, tabla, ambito_actual="global"):
    # Si el nodo es una lista, recorrer cada elemento
    if isinstance(nodo, list):
        for subnodo in nodo:
            recorrer_preorden(subnodo, tabla, ambito_actual)
        return

    if not isinstance(nodo, NodoArbol):
        return  # Ignoramos cualquier cosa que no sea un nodo del AST

    # Comprobación de tipo de nodo de los cuales nos interesa
    # declaración de variable o función
    tipo = nodo.tipoNodo

    # Si es una declaración de variable, se agrega a la tabla de símbolos
    if tipo == TipoExpresion.VarDec:
        # Comprobar si la variable ya existe en el ámbito actual
        if ambito_actual not in tabla:
            tabla[ambito_actual] = []
        
        # generacion de fila para la tabla de simbolos
        #donde se llena los campos de la tabla
        nombre = nodo.nombre
        tipo_var = nodo.tipo
        es_array = nodo.longitud is not None
        logitudArr = nodo.longitud if es_array else "-"
        linea = nodo.lineaAparicion
        entrada = {
            "nombre": nombre,
            "tipo": tipo_var,
            "tipoRetorno": "-",
            "array": es_array,
            "tamaño": "0" if logitudArr == "[]" else logitudArr,
            "linea": linea,
            "parametros": "-"

        }
        #se inserta a tabla en el ambito actual
        tabla[ambito_actual].append(entrada)

    #si es una declaracion de funcion se agrega a la pila de las tablas
    elif tipo == TipoExpresion.FunDec:
        nombre_func = nodo.nombre
        nuevo_ambito = nombre_func  # nombre de la función como nuevo ámbito

        # Agregar la función al ámbito global
        if "global" not in tabla:
            tabla["global"] = []

        #Checamos si tiene parametros internos y los almacenamos como atributos de la funcion
        parametros_funcion = []
        for param in nodo.parametros:
            tipo_param = param.tipo
            es_array = param.longitud is not None
            parametros_funcion.append((tipo_param, es_array))

        tabla["global"].append({
            "nombre": nombre_func,
            "tipo": "funcion",
            "tipoRetorno": nodo.tipo,
            "array": False,
            "tamaño": "-",
            "linea": nodo.lineaAparicion,
            "parametros": parametros_funcion
        })

        # Cambiar el ámbito a la función
        if nuevo_ambito not in tabla:
            # Si el ámbito no existe, lo creamos
            tabla[nuevo_ambito] = []
            #validar si la funcion es main
            if nuevo_ambito == "main":
                global MAIN_EXISTE
                MAIN_EXISTE = True

            
        # Agregar parámetros a la tabla de la función
        for param in nodo.parametros:
            tamaño_param = param.longitud if param.longitud is not None else "-"
            entrada = {
                "nombre": param.nombre,
                "tipo": param.tipo,
                "tipoRetorno": "-",
                "array": param.longitud is not None,
                "tamaño": "0" if param.longitud == "[]" else tamaño_param,
                "linea": param.lineaAparicion,
                "parametros": "-"
            }
            tabla[nuevo_ambito].append(entrada)

        # Recorrer el cuerpo de la función
        if nodo.parteInterna:
            recorrer_preorden(nodo.parteInterna, tabla, nuevo_ambito)

        return  # Evita repetir recorrido

    # Recorrer posibles hijos del nodo
    if nodo.hijoIzquierdo:
        recorrer_preorden(nodo.hijoIzquierdo, tabla, ambito_actual)
    if nodo.hijoDerecho:
        recorrer_preorden(nodo.hijoDerecho, tabla, ambito_actual)

    for stmt in nodo.sentencias:
        recorrer_preorden(stmt, tabla, ambito_actual)

    for arg in nodo.argumentos:
        recorrer_preorden(arg, tabla, ambito_actual)

    for param in nodo.parametros:
        recorrer_preorden(param, tabla, ambito_actual)

    if nodo.expresion:
        recorrer_preorden(nodo.expresion, tabla, ambito_actual)

    if nodo.entonces:
        recorrer_preorden(nodo.entonces, tabla, ambito_actual)

    if nodo.sino:
        recorrer_preorden(nodo.sino, tabla, ambito_actual)

    if nodo.parteInterna:
        recorrer_preorden(nodo.parteInterna, tabla, ambito_actual)

    if nodo.condicion:
        recorrer_preorden(nodo.condicion, tabla, ambito_actual)

#Funcion que fue creada con ayuda de chatgpt para imprimir la tabla de simbolos
#con un formato mas legible

def imprimir_tabla(tabla):
    for ambito, simbolos in tabla.items():
        print(f"\nÁmbito: {ambito}")
        if not simbolos:
            print("  (sin símbolos declarados)")
            continue

        # Encabezados
        print(f"{'Nombre'.ljust(15)}{'Tipo'.ljust(10)}{'Array'.ljust(10)}{'Tamaño'.ljust(10)}{'Línea'.ljust(10)}{'Parámetros int y array'.ljust(10)}")
        print("-" * 60)

        for entrada in simbolos:
            nombre = str(entrada['nombre']).ljust(15)
            tipo = str(entrada['tipo']).ljust(10)
            es_array = str(entrada['array']).ljust(10)
            tam = str(entrada['tamaño']).ljust(10)
            linea = str(entrada['linea']).ljust(10)
            parametros = str(entrada['parametros']).ljust(10)
            print(f"{nombre}{tipo}{es_array}{tam}{linea}{parametros}")

#funcion donde se llama a la funcion de recorrer preorden
#ademas de generar la estructura base de la tabla de simbolos
def tabla(tree, imprime=True):
    #donde la tabla se maneja como un diccionario de ambitos 
    #donde cada ambito tiene una lista de simbolos/variables
    #siendo que cada simbolo es un diccionario con los atributos de las variable
    tabla_resultado = {}
    recorrer_preorden(tree, tabla_resultado)
    if imprime:
        imprimir_tabla(tabla_resultado)
    return tabla_resultado

#endregion

#region Postorden
def recorre_postorden(nodo, tabla, ambito_actual="global"):
    #recorremos los nodos en postorden
    if isinstance(nodo, list):
        for subnodo in nodo:
            recorre_postorden(subnodo, tabla, ambito_actual)
        return

    # nos detenemos si el nodo es None
    if nodo is None:
        return

    # Si el nodo es una declaración de función, cambiar ámbito antes de procesar hijos
    if nodo.tipoNodo == TipoExpresion.FunDec:
        nuevo_ambito = nodo.nombre
        # Procesamos el cuerpo de la función con su nuevo ámbito
        recorre_postorden(nodo.parteInterna, tabla, nuevo_ambito)
    else:
        # Recorrer los hijos con el mismo ámbito actual
        for hijo in (
            nodo.hijoIzquierdo,
            nodo.hijoDerecho,
            nodo.sino,
            nodo.entonces,
            nodo.expresion,
            nodo.condicion,
            nodo.parteInterna,
        ):
            recorre_postorden(hijo, tabla, ambito_actual)

        for lista in (
            nodo.argumentos,
            nodo.parametros,
            nodo.sentencias,
        ):
            for hijo in lista:
                recorre_postorden(hijo, tabla, ambito_actual)

    # **Semántica: Comprobaciones en cada tipo de nodo**
    
    # Si el nodo es una variable (para comprobar su existencia y tipo)
    if nodo.tipoNodo == TipoExpresion.Var:
        # Comprobar si la variable ya existe en el ámbito actual
        simbolo = buscar_variable(tabla, ambito_actual, nodo.nombre)
        if simbolo is None:
            # Si no existe, imprimir error
            print(f"[Error línea {nodo.lineaAparicion}] Variable '{nodo.nombre}' no declarada.")
        else:
            # Si existe, dejamos que pase
            pass

    # Si el nodo es una declaración de función
    elif nodo.tipoNodo == TipoExpresion.FunDec:
        for stmt in nodo.sentencias:  # Recorremos las sentencias dentro de la función
            recorre_postorden(stmt, tabla, nodo.nombre)  # Cambiar el ámbito a la función

    # Si el nodo es una expresión de retorno, donde se checa el tipo de retorno
    #debido a que tenemos en cuenta el contexto de la funcion
    #por ende sabes que si debe tener un returno o no en caso de ser void la funcion
    #en caso de ser int solo se checa que el tipo de la expresion sea int
    elif nodo.tipoNodo == TipoExpresion.Return:
        # Checar si la función tiene un tipo de retorno
        tipo_func = buscar_funcion(tabla, ambito_actual)
        if nodo.expresion is None and tipo_func != "void":
            print(f"[Error línea {nodo.lineaAparicion}] Se esperaba una expresión en return (tipo {tipo_func}).")
        elif nodo.expresion and tipo_func == "void":
            print(f"[Error línea {nodo.lineaAparicion}] Return no debe tener expresión en función void.")

    # Si el nodo es una asignación
    #al poder tener expresiones anidadas
    #se checa que el lado izquierdo sea una variable
    #y el lado derecho sea una expresion
    elif nodo.tipoNodo == TipoExpresion.Op:
        tipo_izq = buscar_tipo_expresion(tabla, ambito_actual, nodo.hijoIzquierdo)
        tipo_der = buscar_tipo_expresion(tabla, ambito_actual, nodo.hijoDerecho)

    # Si el nodo es un condicional if o un bucle while, la condición debe ser un entero
    #checamos que al menos tenga un operador logico
    # que cada expresion sea un entero
    elif nodo.tipoNodo == TipoExpresion.If or nodo.tipoNodo == TipoExpresion.While:
        if nodo.condicion:
            tipo_condicion = buscar_tipo_expresion(tabla, ambito_actual, nodo.condicion)
            if tipo_condicion != "int":
                print(f"[Error línea {nodo.lineaAparicion}] La condición debe ser de tipo 'int', pero se encontró tipo '{tipo_condicion}'.")
            if not buscar_operador_logico(nodo.condicion):
                print(f"[Error línea {nodo.lineaAparicion}] La condición requiere por lo menos un operador lógico.")
    
    # Si el nodo es una llamada a función
    #se checa que la funcion exista y que el numero de argumentos sea correcto
    #ademas de que los tipos de los argumentos sean correctos
    elif nodo.tipoNodo == TipoExpresion.Call:
        nombre_func = nodo.nombre

        # Manejo especial para funciones predefinidas (input y output)
        if nombre_func == "input" or nombre_func == "output":
            # No se realiza ninguna validación adicional, solo se pasa
            pass
            return  # Después de pasar, se termina la validación

        # Validación normal para funciones declaradas
        simbolo = buscar_variable(tabla, ambito_actual, nombre_func)

        if simbolo is None or simbolo['tipo'] != 'funcion':
            print(f"[Error línea {nodo.lineaAparicion}] Función '{nombre_func}' no declarada.")
            return

        # Verificar que el número de argumentos sea correcto
        num_parametros = len(simbolo['parametros'])
        num_argumentos = len(nodo.argumentos)

        if num_argumentos != num_parametros:
            print(f"[Error línea {nodo.lineaAparicion}] Función '{nombre_func}' espera {num_parametros} argumentos, pero se proporcionaron {num_argumentos}.")
            return

        # Verificar tipos de argumentos
        for i in range(num_argumentos):
            argumento = nodo.argumentos[i]

            # Buscar si es una variable declarada
            tipo_arg_entry = buscar_variable(tabla, ambito_actual, argumento.nombre) if hasattr(argumento, 'nombre') else None
            
            if tipo_arg_entry is not None:
                tipo_arg = tipo_arg_entry['tipo']
                es_array_arg = tipo_arg_entry['array']
            else:
                tipo_arg = buscar_tipo_expresion(tabla, ambito_actual, argumento)
                es_array_arg = False  # Asumimos que una constante o expresión no es array

            tipo_param = simbolo['parametros'][i][0]
            es_array_param = simbolo['parametros'][i][1]

            # Comparación de tipo
            if tipo_arg != tipo_param:
                print(f"[Error línea {nodo.lineaAparicion}] Tipo de argumento '{tipo_arg}' no coincide con el tipo esperado '{tipo_param}' en la función '{nombre_func}'.")

            # Comparación si es array o no
            if es_array_arg != es_array_param:
                print(f"[Error línea {nodo.lineaAparicion}] El argumento '{getattr(argumento, 'nombre', 'expresión')}' no coincide con la definición (array vs no-array) en la función '{nombre_func}'.")

#endregion
#region funciones auxiliares para buscar variables y funciones
def buscar_variable(tabla, ambito, nombre):
    # Buscar una variable en el ámbito actual y global
    for scope in [ambito, "global"]:
        if scope in tabla:
            for simbolo in tabla[scope]:
                if simbolo['nombre'] == nombre:
                    #print(f"La variable '{nombre}' se declaró en el ámbito '{scope}'")
                    return simbolo
    return None

#funcion que busca una funcion en la tabla de simbolos
def buscar_funcion(tabla, ambito):
    # Buscar una función en el ámbito actual y global
    for scope in [ambito, "global"]:
        if scope in tabla:
            for simbolo in tabla[scope]:
                if simbolo['nombre'] == ambito:
                    #print(f"La función '{ambito}' se declaró en el ámbito '{scope}'")
                    return simbolo['tipoRetorno']            
    return None
#endregion

#region funciones para buscar operadores logicos
#Funcion que busca si existe un operador logico en la expresion
#donde se checa si el nodo es un operador logico
def buscar_operador_logico(expresion):
    if not isinstance(expresion, NodoArbol):
        return False

    tipo = expresion.tipoNodo

    if tipo == TipoExpresion.Op:
        if expresion.operador in OPERADORES_LOGICOS:
            return True
        return buscar_operador_logico(expresion.hijoIzquierdo) or buscar_operador_logico(expresion.hijoDerecho)
    
    return False
#endregion    

#region funciones para buscar el tipo de expresion
# Función que busca en los hijos de operadores consecutivos para ver que los hijos cumplan con el tipo de expresión
# También funciona cuando se les asigna un call de una función
def buscar_tipo_expresion(tabla, ambito, expresion):
    # Si no es un nodo del árbol (por ejemplo, un número constante como 1), se asume int
    if not isinstance(expresion, NodoArbol):
        return "int"

    tipo = expresion.tipoNodo

    # Si el nodo es una variable, se busca su tipo en la tabla de símbolos
    if tipo == TipoExpresion.Var:
        simbolo = buscar_variable(tabla, ambito, expresion.nombre)
        if simbolo:
            return simbolo['tipo']
        else:
            print(f"[Error] Variable '{expresion.nombre}' no declarada.")
            return "error"

    # Si el nodo es una constante, se asume tipo int
    elif tipo == TipoExpresion.Const:
        return "int"

    # Si el nodo es una operación, se revisan los tipos de los operandos
    elif tipo == TipoExpresion.Op:
        tipo_izq = buscar_tipo_expresion(tabla, ambito, expresion.hijoIzquierdo)
        tipo_der = buscar_tipo_expresion(tabla, ambito, expresion.hijoDerecho)

        # Si alguno de los operandos no es int, se reporta error
        if tipo_izq != "int" or tipo_der != "int":
            print(f"[Error línea {expresion.lineaAparicion}] Operación '{expresion.operador}' con operandos no enteros: {tipo_izq}, {tipo_der}")
            # Se retorna el tipo incorrecto para propagar el error
            if tipo_izq == "int":
                return tipo_der
            else:
                return tipo_izq

        # Si el operador es lógico (>, <, ==, etc), se retorna int como tipo de comparación
        if expresion.operador in OPERADORES_LOGICOS:
            return "int"

        # Si es un operador aritmético, también retorna int
        elif expresion.operador in ["+", "-", "*", "/"]:
            return "int"

        # En asignaciones, se retorna el tipo del lado izquierdo
        elif expresion.operador == "=":
            return tipo_izq

        # Si el operador no es reconocido, se muestra error
        else:
            print(f"[Error línea {expresion.lineaAparicion}] Operador desconocido '{expresion.operador}'")
            return "error"

    # Si el nodo es una llamada a función, se busca su tipo de retorno
    elif tipo == TipoExpresion.Call:
        funcion = buscar_variable(tabla, "global", expresion.nombre)
        if funcion:
            return funcion.get("tipoRetorno", "void")
        else:
            # Se permiten funciones predefinidas como input y output
            if expresion.nombre == "input" or expresion.nombre == "output":
                return "int"
            print(f"[Error línea {expresion.lineaAparicion}] Función '{expresion.nombre}' no declarada.")
            return "error"

    # Caso por defecto, si no se identificó el tipo, se retorna int
    return "int"


#endregion

#region funcion principal
def semantica(tree, imprime=True):
    tabla_resultado = {}
    tabla_resultado =  tabla(tree, imprime)
    if not MAIN_EXISTE:
        print("[Error] No se encontró la función 'main' en el programa.")
    #checha que main sea la ultima declaracion de tabla
    if "main" in tabla_resultado and tabla_resultado["main"][-1]["nombre"] == "main":
        print("[Error] La función 'main' debe ser la última declaración en el programa.")
    #procesamiento 
    print("\n\nAnalizador sematico empezando:")
    recorre_postorden(tree, tabla_resultado)
    print("\n\nterminado:")

    #una vez obtenido la tabla de simbolos, se procede a recorrer el arbol en postorden

