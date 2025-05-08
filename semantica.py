from Parser import *
from globalTypes import *

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
            "linea": linea

        }
        tabla[ambito_actual].append(entrada)
    #si es una declaracion de funcion se agrega a la pila de las tablas
    elif tipo == TipoExpresion.FunDec:
        nombre_func = nodo.nombre
        nuevo_ambito = nombre_func  # nombre de la función como nuevo ámbito

        # Agregar la función al ámbito global
        if "global" not in tabla:
            tabla["global"] = []

        tabla["global"].append({
            "nombre": nombre_func,
            "tipo": "funcion",
            "tipoRetorno": nodo.tipo,
            "array": False,
            "tamaño": "-",
            "linea": nodo.lineaAparicion
        })

        if nuevo_ambito not in tabla:
            tabla[nuevo_ambito] = []

        # Agregar parámetros a la tabla de la función
        for param in nodo.parametros:
            tamaño_param = param.longitud if param.longitud is not None else "-"
            entrada = {
                "nombre": param.nombre,
                "tipo": param.tipo,
                "tipoRetorno": "-",
                "array": param.longitud is not None,
                "tamaño": "0" if param.longitud == "[]" else tamaño_param,
                "linea": param.lineaAparicion
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
        print(f"{'Nombre'.ljust(15)}{'Tipo'.ljust(10)}{'Array'.ljust(10)}{'Tamaño'.ljust(10)}{'Línea'.ljust(10)}")
        print("-" * 60)

        for entrada in simbolos:
            nombre = str(entrada['nombre']).ljust(15)
            tipo = str(entrada['tipo']).ljust(10)
            es_array = str(entrada['array']).ljust(10)
            tam = str(entrada['tamaño']).ljust(10)
            linea = str(entrada['linea']).ljust(10)
            print(f"{nombre}{tipo}{es_array}{tam}{linea}")

def tabla(tree, imprime=True):
    tabla_resultado = {}
    recorrer_preorden(tree, tabla_resultado)
    if imprime:
        imprimir_tabla(tabla_resultado)
    return tabla_resultado

def recorre_postorden(nodo, tabla, ambito_actual="global"):
    # Si el nodo es una lista, recorrer todos los elementos
    if isinstance(nodo, list):
        for subnodo in nodo:
            recorre_postorden(subnodo, tabla, ambito_actual)
        return None

    # Si el nodo es None, no hacer nada
    if nodo is None:
        return None

    # Primero recorrer los hijos del nodo
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

    # Recorrer las listas de argumentos, parámetros y sentencias
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
            pass

    # Si el nodo es una declaración de función, comprobar si el tipo de retorno es consistente
    elif nodo.tipoNodo == TipoExpresion.FunDec:
        for stmt in nodo.sentencias:  # Recorremos las sentencias dentro de la función
            recorre_postorden(stmt, tabla, nodo.nombre)  # Cambiar el ámbito a la función

    # Si el nodo es una expresión de retorno
    elif nodo.tipoNodo == TipoExpresion.Return:
        tipo_func = buscar_tipo_funcion(tabla, ambito_actual)
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

def buscar_variable(tabla, ambito, nombre):
    # Buscar una variable en el ámbito actual y global
    for scope in [ambito, "global"]:
        if scope in tabla:
            for simbolo in tabla[scope]:
                if simbolo['nombre'] == nombre and simbolo['tipo'] != 'funcion':
                    return simbolo
    return None

def buscar_tipo_funcion(tabla, nombre_funcion):
    # Buscar el tipo de retorno de una función
    if nombre_funcion in tabla:
        for entrada in tabla["global"]:
            if entrada["nombre"] == nombre_funcion:
                return entrada["tipoRetorno"]
    return None

def buscar_tipo_expresion(tabla, ambito, expresion):
    # Aquí sería necesario agregar lógica que determine el tipo de una expresión
    # Esto es solo un ejemplo muy básico
    if isinstance(expresion, NodoArbol):
        if expresion.tipoNodo == TipoExpresion.Var:
            return buscar_variable(tabla, ambito, expresion.nombre)['tipo']
    return "int"  # Valor por defecto, si la expresión no es válida


def semantica(tree, imprime=True):
    tabla_resultado = {}
    tabla_resultado =  tabla(tree, imprime)

    #una vez obtenido la tabla de simbolos, se procede a recorrer el arbol en postorden

    



f = open("test.c-", "r")
program = f.read()
programLong = len(program)
program = program + "$"
posicion = 0

#funciones para pasar los valores iniciales de las variables globales

globales(program, posicion, programLong)

AST = parser(True)

tabla(AST, True)
