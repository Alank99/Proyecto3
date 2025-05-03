from Parser import *
from globalTypes import *

#recorrido preordenado del arbol
def es_array(nodo):
    return nodo.longitud is not None

def insertar_en_tabla(tabla, ambito, nombre, tipo, es_array_flag, linea):
    if ambito not in tabla:
        tabla[ambito] = {}

    if nombre in tabla[ambito]:
        print(f"Error: '{nombre}' ya está declarado en el ámbito '{ambito}'")
    else:
        tabla[ambito][nombre] = {
            "tipo": tipo,
            "es_array": es_array_flag,
            "linea": linea
        }

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
        linea = nodo.lineaAparicion
        entrada = {
            "nombre": nombre,
            "tipo": tipo_var,
            "array": es_array,
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
            "array": False,
            "linea": nodo.lineaAparicion
        })

        if nuevo_ambito not in tabla:
            tabla[nuevo_ambito] = []

        # Agregar parámetros a la tabla de la función
        for param in nodo.parametros:
            entrada = {
                "nombre": param.nombre,
                "tipo": param.tipo,
                "array": param.longitud is not None,
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
        print(f"{'Nombre'.ljust(15)}{'Tipo'.ljust(10)}{'Array'.ljust(10)}{'Línea'.ljust(10)}")
        print("-" * 45)

        # Filas
        for entrada in simbolos:
            nombre = str(entrada['nombre']).ljust(15)
            tipo = str(entrada['tipo']).ljust(10)
            es_array = str(entrada['array']).ljust(10)
            linea = str(entrada['linea']).ljust(10)
            print(f"{nombre}{tipo}{es_array}{linea}")


def tabla(tree, imprime=True):
    tabla_resultado = {}
    recorrer_preorden(tree, tabla_resultado)
    if imprime:
        imprimir_tabla(tabla_resultado)
    return tabla_resultado

def postorden(nodo, indent=0):
    if isinstance(nodo, list):
        for subnodo in nodo:
            postorden(subnodo, indent)
        return

    if nodo is None:
        return

    for hijo in (
        nodo.hijoIzquierdo,
        nodo.hijoDerecho,
        nodo.parteInterna,
        nodo.expresion,
        nodo.entonces,
        nodo.sino,
        nodo.condicion
    ):
        postorden(hijo, indent + 1)

    for lista in (
        nodo.parametros,
        nodo.sentencias,
        nodo.argumentos,
    ):
        if lista:
            for subnodo in lista:
                postorden(subnodo, indent + 1)

    tipo_nodo = nodo.tipoNodo.name if nodo.tipoNodo else "Ninguno"
    print("  " * indent + f"[POST] Nodo: {tipo_nodo} - {nodo.nombre or nodo.valor or nodo.operador}")



f = open("test.c-", "r")
program = f.read()
programLong = len(program)
program = program + "$"
posicion = 0

#funciones para pasar los valores iniciales de las variables globales

globales(program, posicion, programLong)

AST = parser(True)

tabla(AST, True)
