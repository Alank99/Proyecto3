from Parser import *
from globalTypes import *

OPERADORES_LOGICOS = ["==", "!=", "<", "<=", ">", ">="]

MAIN_EXISTE = False

#recorrido preordenado del arbol
def es_array(nodo):
    return nodo.longitud is not None

def recorrer_preorden(nodo, tabla, ambito_actual="global"):
    if isinstance(nodo, list):
        for subnodo in nodo:
            recorrer_preorden(subnodo, tabla, ambito_actual)
        return

    if not isinstance(nodo, NodoArbol):
        return  # Ignoramos cualquier cosa que no sea un nodo del AST

    # Ya es seguro usar nodo.tipoNodo
    tipo = nodo.tipoNodo

    if tipo == TipoExpresion.VarDec:
        if ambito_actual not in tabla:
            tabla[ambito_actual] = []

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
        tabla[ambito_actual].append(entrada)
    #si es una declaracion de funcion se agrega a la pila de las tablas
    elif tipo == TipoExpresion.FunDec:
        nombre_func = nodo.nombre
        nuevo_ambito = nombre_func  # nombre de la función como nuevo ámbito

        # Agregar la función al ámbito global
        if "global" not in tabla:
            tabla["global"] = []

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


        if nuevo_ambito not in tabla:
            tabla[nuevo_ambito] = []
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

def tabla(tree, imprime=True):
    tabla_resultado = {}
    recorrer_preorden(tree, tabla_resultado)
    if imprime:
        imprimir_tabla(tabla_resultado)
    return tabla_resultado


def recorre_postorden(nodo, tabla, ambito_actual="global"):
    if isinstance(nodo, list):
        for subnodo in nodo:
            recorre_postorden(subnodo, tabla, ambito_actual)
        return

    if nodo is None:
        return

    # Si el nodo es una declaración de función, cambiar ámbito ANTES de procesar hijos
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
        simbolo = buscar_variable(tabla, ambito_actual, nodo.nombre)
        if simbolo is None:
            print(f"[Error línea {nodo.lineaAparicion}] Variable '{nodo.nombre}' no declarada.")
        else:
            # Aquí puedes verificar que el tipo sea correcto si es necesario
            #print(f"[Info línea {nodo.lineaAparicion}] Variable '{nodo.nombre}' de tipo '{simbolo['tipo']}' encontrada en el ámbito '{ambito_actual}'.")
            pass

    # Si el nodo es una declaración de función, comprobar si el tipo de retorno es consistente
    elif nodo.tipoNodo == TipoExpresion.FunDec:
        for stmt in nodo.sentencias:  # Recorremos las sentencias dentro de la función
            recorre_postorden(stmt, tabla, nodo.nombre)  # Cambiar el ámbito a la función

    # Si el nodo es una expresión de retorno
    elif nodo.tipoNodo == TipoExpresion.Return:
        tipo_func = buscar_funcion(tabla, ambito_actual)
        if nodo.expresion is None and tipo_func != "void":
            print(f"[Error línea {nodo.lineaAparicion}] Se esperaba una expresión en return (tipo {tipo_func}).")
        elif nodo.expresion and tipo_func == "void":
            print(f"[Error línea {nodo.lineaAparicion}] Return no debe tener expresión en función void.")

    # Si el nodo es una asignación
    elif nodo.tipoNodo == TipoExpresion.Op:
        if nodo.operador == "=":
            # Si es una asignación, verificamos que la variable de la izquierda esté declarada
            simbolo = buscar_variable(tabla, ambito_actual, nodo.hijoIzquierdo.nombre)
            if simbolo is None:
                print(f"[Error línea {nodo.lineaAparicion}] Variable '{nodo.hijoIzquierdo.nombre}' no declarada para asignación.")
            # También podríamos verificar que el tipo de la izquierda y derecha sean compatibles
            # Ejemplo: Si la izquierda es un int, la derecha también debe ser un int
            if simbolo and nodo.hijoIzquierdo.tipo != nodo.hijoDerecho.tipo:
                print(f"[Error línea {nodo.lineaAparicion}] Tipos incompatibles en asignación: {nodo.hijoIzquierdo.tipo} = {nodo.hijoDerecho.tipo}")

    # Si el nodo es un condicional if o un bucle while, la condición debe ser un entero
    elif nodo.tipoNodo == TipoExpresion.If or nodo.tipoNodo == TipoExpresion.While:
        if nodo.condicion:
            tipo_condicion = buscar_tipo_expresion(tabla, ambito_actual, nodo.condicion)
            if tipo_condicion != "int":
                print(f"[Error línea {nodo.lineaAparicion}] La condición debe ser de tipo 'int', pero se encontró tipo '{tipo_condicion}'.")

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



def buscar_variable(tabla, ambito, nombre):
    # Buscar una variable en el ámbito actual y global
    for scope in [ambito, "global"]:
        if scope in tabla:
            for simbolo in tabla[scope]:
                if simbolo['nombre'] == nombre:
                    #print(f"La variable '{nombre}' se declaró en el ámbito '{scope}'")
                    return simbolo
    return None

def buscar_funcion(tabla, ambito):
    # Buscar una función en el ámbito actual y global
    for scope in [ambito, "global"]:
        if scope in tabla:
            for simbolo in tabla[scope]:
                if simbolo['nombre'] == ambito:
                    #print(f"La función '{ambito}' se declaró en el ámbito '{scope}'")
                    return simbolo['tipoRetorno']            
    return None


def buscar_tipo_expresion(tabla, ambito, expresion):
    if not isinstance(expresion, NodoArbol):
        return "int"

    tipo = expresion.tipoNodo

    if tipo == TipoExpresion.Var:
        simbolo = buscar_variable(tabla, ambito, expresion.nombre)
        if simbolo:
            return simbolo['tipo']
        else:
            print(f"[Error] Variable '{expresion.nombre}' no declarada.")
            return "error"

    elif tipo == TipoExpresion.Const:
        return "int"

    elif tipo == TipoExpresion.Op:
        tipo_izq = buscar_tipo_expresion(tabla, ambito, expresion.hijoIzquierdo)
        tipo_der = buscar_tipo_expresion(tabla, ambito, expresion.hijoDerecho)

        if tipo_izq != "int" or tipo_der != "int":
            print(f"[Error línea {expresion.lineaAparicion}] Operación '{expresion.operador}' con operandos no enteros: {tipo_izq}, {tipo_der}")
            if tipo_izq  == "int":
                return tipo_der
            else:
                return tipo_izq

        if expresion.operador in OPERADORES_LOGICOS:
            return "int"  # Comparación devuelve int

        elif expresion.operador in ["+", "-", "*", "/"]:
            return "int"

        elif expresion.operador == "=":
            # Validación de asignación ocurre en semántica general
            return tipo_izq

        else:
            print(f"[Error línea {expresion.lineaAparicion}] Operador desconocido '{expresion.operador}'")
            return "error"

    elif tipo == TipoExpresion.Call:
        funcion = buscar_variable(tabla, "global", expresion.nombre)
        if funcion:
            return funcion.get("tipoRetorno", "void")
        else:
            print(f"[Error línea {expresion.lineaAparicion}] Función '{expresion.nombre}' no declarada.")
            return "error"

    return "int"



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

    



f = open("test.c-", "r")
program = f.read()
programLong = len(program)
program = program + "$"
posicion = 0

#funciones para pasar los valores iniciales de las variables globales

globales(program, posicion, programLong)

AST = parser(True)

semantica(AST, True)
