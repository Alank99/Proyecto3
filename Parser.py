#importando las librerias necesarias para el funcionamiento del parser
from globalTypes import *
from lexer import * 

#Archivo donde se genera el arbol de sintaxis abstracta
#Regresa el arbol de sintaxis abstracta y un error lo marca en que linea y intenta seguir
#Creado para C- 
#Creado por: Alan Anthony Hernandez Perez
#Creado el: 17/04/2025
#con el asistente de copilot de vscode

#definimos las variables globales que se usaran en el parser

Error = False # Bandera de error
imprimeScanner = False # Bandera para imprimir el scanner

edentacion = 0 # Variable para la edentacionacion del arbol
#endregion

#region declaracion del arbol de sintaxis abstracta
#Generacion del arbol de sintaxis abstracta
def nodoNuevo(tipo):
    arbol =  NodoArbol()
    arbol.tipoNodo = tipo # Se le asigna el tipo de la expresion
    return arbol # Se regresa el arbol de sintaxis abstracta

#endregion

#funcion para sincronizar el analizador sintactico
#para que no se detenga en un error de sintaxis
#y pueda seguir analizando el programa

#El manejado de errores de sintaxis se hace en la funcion syntaxError
#donde se imprime el error en syntax Error , pero se llama a la funcion sincronizar
#del cual hace que el programa avance al siguiente token
#de este se evalue el token y se considera si es valido dento de los sincronizadores
#donde el programa encuentra un momento correcto para continuar el analisis
def sincronizar():
    global token, tokenString, lineno, columna
    #TokenType de los cuales permiten continuar el analisis
    sincronizadores ={
        TokenType.INT,TokenType.VOID,TokenType.WHILE,
        TokenType.RETURN,TokenType.IF,TokenType.ID, TokenType.PUNTO_Y_COMA
    }
    #mientras el token no sea de los que permiten continuar el analisis
    while token not in sincronizadores and token != TokenType.ENDFILE:
        #se obtiene el siguiente token
        token, tokenString, lineno, columna = getToken(False)

#region Error de sintaxis
def syntaxError(message):
    global tokenString, lineno, position, columna
    print("Error de sintaxis en la linea " + str(lineno) + ": " + message) 

    #imprime la flecha de error
    #Este extracto fue sacado de ChatGPT
    #para imprimir la linea de error y la flecha
    try:
        linea = program.splitlines()[lineno - 1]
        print("    " + linea)
        print("   " + " " * columna + "^")
    except IndexError:
        print("    (No se pudo mostrar la línea)")
    #se intenta seguir sincronizando el analizador sintactico 
    #para continuar con el analisis del programa
#endregion

#region Manejo de tokens
def match(tokenEsperado):
    global token, tokenString, lineno, columna
    if(token == tokenEsperado):
        token, tokenString, lineno, columna = getToken(imprimeScanner) # Se obtiene el siguiente token
    else:
        syntaxError("Token inesperado, esperado: " + tokenEsperado.name + ", encontrado: " + tokenString)
        #se intenta seguir sincronizando el analizador sintactico
        sincronizar() # Se llama a la funcion sincronizar
#endregion

#region Argumentos
#Gramatica para argumentos
#args → [ expression { "," expression } ]
def args():
    global token
    argumentos = [] # Se inicializa la lista de argumentos
    if token != TokenType.PARENTESIS_DER: 
        argumentos.append(expression())
        # Verifica si hay mas argumentos
        while token == TokenType.COMA: # Si el token es una coma
            match(TokenType.COMA) # Se espera una coma
            argumentos.append(expression()) # Se agrega el argumento a la lista de argumentos
    return argumentos # Se regresa la lista de argumentos

#region variables
#Gramaticas para la variable
#var → ID [ "[" expression "]" ]
def var(id):
    nodo = nodoNuevo(TipoExpresion.Var) # Se crea un nodo de tipo Var
    nodo.nombre = id # Se le asigna el nombre al nodo de tipo Var
    if token == TokenType.CORCHETE_IZQ: # Si el token es un corchete izquierdo para saber si es un arreglo
        match(TokenType.CORCHETE_IZQ) # Se espera un corchete izquierdo
        nodo.indice = expression()
        match(TokenType.CORCHETE_DER) # Se espera un corchete derecho
    return nodo # Se regresa el nodo de tipo Var

#region llamada de funcion
#Gramatica para la llamada de funcion
#call →  ID "(" args ")"
def call(id):
    nodo = nodoNuevo(TipoExpresion.Call) # Se crea un nodo de tipo Call
    nodo.nombre = id # Se le asigna el nombre al nodo de tipo Call
    match(TokenType.PARENTESIS_IZQ) # Se espera un parentesis izquierdo
    nodo.argumentos = args() # Se llama a la funcion args
    match(TokenType.PARENTESIS_DER) # Se espera un parentesis derecho
    return nodo # Se regresa el nodo de tipo Call

#region factor
#Gramatica para factor
#factor → ID | NUM | "(" expression ")" | call
def factor():
    global token, tokenString
    # Verifica si el token es un ID o un numero
    if token == TokenType.ID: # Si el token es un ID
        nombre = tokenString # Se guarda el ID
        match(TokenType.ID) # Se espera un ID
        if token == TokenType.PARENTESIS_IZQ:# Si el token es un llamado de funcion
            return call(nombre)
        elif token == TokenType.CORCHETE_IZQ:# Si el token es un arreglo
            return var(nombre)
        else:
            nodo = nodoNuevo(TipoExpresion.Var)
            nodo.nombre = nombre
            return nodo # Se regresa el nodo de tipo Var
        
    elif token == TokenType.PARENTESIS_IZQ: # Si el token es un parentesis izquierdo
        match(TokenType.PARENTESIS_IZQ) # Se espera un parentesis izquierdo
        nodo = expression() # Se llama a la funcion expression
        match(TokenType.PARENTESIS_DER) # Se espera un parentesis derecho
        return nodo # Se regresa el nodo de tipo Op
    
    elif token == TokenType.NUM: # Si el token es un numero
        nodo = nodoNuevo(TipoExpresion.Const) # Se crea un nodo de tipo Num
        nodo.valor = tokenString # Se le asigna el valor al nodo de tipo Num
        match(TokenType.NUM) # Se espera un numero
        return nodo # Se regresa el nodo de tipo Num
    
    else:
        syntaxError("Se esperaba un ID, un numero o un parentesis izquierdo, encontrado: " + tokenString)

#region term
#Gramatica para Term
#term → factor { ( "*" | "/" ) factor }
def term():
    nodo = factor() # Se llama a la funcion factor
    while token == TokenType.MULTIPLICACION or token == TokenType.DIVISION: # Mientras el token sea una multiplicacion o una division
        nodoOp = nodoNuevo(TipoExpresion.Op) # Se crea un nodo de tipo Op
        nodoOp.hijoIzquierdo = nodo # Se le asigna el hijo izquierdo al nodo de tipo Op
        if token == TokenType.MULTIPLICACION:
            nodoOp.operador = '*' # Se le asigna el operador de multiplicacion
            match(TokenType.MULTIPLICACION) # Se espera una multiplicacion
        else:
            nodoOp.operador = '/' # Se le asigna el operador de division
            match(TokenType.DIVISION) # Se espera una division
        nodoOp.hijoDerecho = factor() # Se le asigna el hijo derecho al nodo de tipo Op
        nodo = nodoOp # Se le asigna el nodo de tipo Op al nodo
    return nodo # Se regresa el nodo de tipo Op

#region additive-expression
#Gramatica para la additive-expression
#additive-expression → term { ( "+" | "-" ) term }
def additive_expression():
    nodo = term() # Se llama a la funcion term
    while token == TokenType.SUMA or token == TokenType.RESTA: # Mientras el token sea una suma o una resta
        nodoOp = nodoNuevo(TipoExpresion.Op) # Se crea un nodo de tipo Op
        nodoOp.hijoIzquierdo = nodo # Se le asigna el hijo izquierdo al nodo de tipo Op
        if token == TokenType.SUMA:
            nodoOp.operador = '+'
            match(TokenType.SUMA) # Se espera una suma
        else:
            nodoOp.operador = '-'
            match(TokenType.RESTA) # Se espera una resta
        nodoOp.hijoDerecho = term() # Se le asigna el hijo derecho al nodo de tipo Op
        nodo = nodoOp # Se le asigna el nodo de tipo Op al nodo
    return nodo # Se regresa el nodo de tipo Op

#region simple-expression
#Gramatica para la simple-expression
#simple-expression → additive-expression [ relop additive-expression ]
def simple_expression():
    nodo = additive_expression() # Se llama a la funcion additive_expression
    if token == TokenType.MAYOR or token == TokenType.MENOR or token == TokenType.ASIGNACION or token == TokenType.IGUAL or token == TokenType.DISTINTO or token == TokenType.MAYOR_IGUAL or token == TokenType.MENOR_IGUAL: # Si el token es un operador relacional
        nodoOplog = nodoNuevo(TipoExpresion.Op)#operador logico
        nodoOplog.hijoIzquierdo = nodo # Se le asigna el hijo izquierdo al nodo de operador logico
        nodoOplog.operador = tokenString # Se le asigna el operador logico
        match(token) # Se espera un operador logico
        nodoOplog.hijoDerecho = additive_expression() # Se le asigna el hijo derecho al nodo de operador logico
        return nodoOplog # Se regresa el nodo de operador logico
    else:
        return nodo # Se regresa el nodo de tipo Op

#region expression
#Gramatica para la expression
#expression → var = expression | simple-expression
def expression():
    #llamamos a los token y tokenString globales
    global token, tokenString
    #chequeamos si el token es un ID
    if token == TokenType.ID:
        nombre = tokenString # Se guarda el ID

        #chechamos si el token es una llamdo de funcion o una asignacion
        #para saber si es llamado de funcion o una operacion
        if token == TokenType.PARENTESIS_IZQ or token == TokenType.CORCHETE_IZQ or token == TokenType.ASIGNACION:
            match(TokenType.ID) # Se espera un ID
            if token == TokenType.PARENTESIS_IZQ:
                return call(nombre) # Se llama a la funcion call
            #en caso de que sea un corchete izquierdo es una operacion o una variable con arreglo
            elif token == TokenType.CORCHETE_IZQ:
                #generamos el nodo de la variable
                nodoVar = var(nombre) # Se crea un nodo de tipo Var
                # chechamos si no tenemos un operador
                if token == TokenType.ASIGNACION:
                    nodoOp = nodoNuevo(TipoExpresion.Op) # Se crea un nodo de tipo Op
                    nodoOp.operador = '=' # Se le asigna el operador de asignacion
                    nodoOp.hijoIzquierdo = nodoVar # Se le asigna el hijo izquierdo al nodo de tipo Op
                    match(TokenType.ASIGNACION) # Se espera un corchete izquierdo
                    nodoOp.hijoDerecho = expression() # Se le asigna el hijo derecho al nodo de tipo Op
                    return nodoOp # Se regresa el nodo de tipo Op
                return nodoVar
            #en caso de que sea igual se genera el nodo de operacion
            elif token == TokenType.ASIGNACION:
                nodoVar = nodoNuevo(TipoExpresion.Var) # Se crea un nodo de tipo Var
                nodoVar.nombre = nombre # Se le asigna el nombre al nodo de tipo Var
                match(TokenType.ASIGNACION) # Se espera un operador de asignacion
                nodoOp = nodoNuevo(TipoExpresion.Op) # Se crea un nodo de tipo Op
                nodoOp.operador = '=' # Se le asigna el operador de asignacion
                nodoOp.hijoIzquierdo = nodoVar # Se le asigna el hijo izquierdo al nodo de tipo Op
                nodoOp.hijoDerecho = expression() # Se le asigna el hijo derecho al nodo de tipo Op
                return nodoOp # Se regresa el nodo de tipo Op
    return simple_expression() # Se llama a la funcion simple_expression

#region expression-statement
#Gramatica para la expression-statement
#expression-statement → [expression] ";"
def expression_stmt():
    nodo = nodoNuevo(TipoExpresion.ExpreStmt)
    
    if token != TokenType.PUNTO_Y_COMA:
        nodo.expresion = expression()
    
    match(TokenType.PUNTO_Y_COMA)
    return nodo

#Gramatica para la iteration_stmt
#iteration-statement → "while" "(" expression ")" statement
def iteration_stmt():
    nodo = nodoNuevo(TipoExpresion.While) # Se crea un nodo de tipo While
    match(TokenType.WHILE) # Se espera un while
    match(TokenType.PARENTESIS_IZQ) # Se espera un parentesis izquierdo
    nodo.condicion = expression() # Se llama a la funcion expression
    match(TokenType.PARENTESIS_DER) # Se espera un parentesis derecho
    nodo.entonces = statement() # Se llama a la funcion statement
    return nodo # Se regresa el nodo de tipo While

#region return_stmt
#Gramatica para la return_stmt
#return-statement → "return" [expression] ";"
def return_stmt():
    nodo = nodoNuevo(TipoExpresion.Return) # Se crea un nodo de tipo Return
    match(TokenType.RETURN) # Se espera un return
    if token != TokenType.PUNTO_Y_COMA: # Si el token no es un punto y coma
        nodo.expresion = expression() # Se llama a la funcion expression
    match(TokenType.PUNTO_Y_COMA) # Se espera un punto y coma
    return nodo # Se regresa el nodo de tipo Return

#region selection_stmt
#Gramatica para la selection_stmt
#selection-statement → "if" "(" expression ")" statement [ "else" statement ]
def selection_stmt():
    nodo = nodoNuevo(TipoExpresion.If) # Se crea un nodo de tipo If
    match(TokenType.IF) # Se espera un if
    match(TokenType.PARENTESIS_IZQ) # Se espera un parentesis izquierdo
    nodo.condicion = expression() # Se llama a la funcion expression
    match(TokenType.PARENTESIS_DER) # Se espera un parentesis derecho
    nodo.entonces = statement() # Se llama a la funcion statement
    if token == TokenType.ELSE: # Si el token es un else
        match(TokenType.ELSE) # Se espera un else
        nodo.sino = statement() # Se llama a la funcion statement
    return nodo # Se regresa el nodo de tipo If


#region statement
#Gramatica para la statement
#statement → expression-statement | compound-statement | selection-statement | iteration-statement | return-statement
def statement():
    #chechamos de que tipo es el token y llamamos a la funcion correspondiente
    if token == TokenType.WHILE: # Si el token es un while
        return iteration_stmt() # Se llama a la funcion iteration_stmt
    elif token == TokenType.LLAVE_IZQ:# Si el token es una llave izquierda
        return compound_stmt() # Se llama a la funcion compound_stmt
    elif token == TokenType.RETURN: # Si el token es un return
        return return_stmt() # Se llama a la funcion return_stmt
    elif token == TokenType.IF: # Si el token es un if 
        return selection_stmt() # Se llama a la funcion selection_stmt
    elif token in (TokenType.ID, TokenType.NUM, TokenType.PARENTESIS_IZQ):    
        return expression_stmt()
    else:
        syntaxError("Se esperaba una sentencia, encontrado: " + tokenString)
        sincronizar()  #avanza
        return None

#region compound_stmt
#Gramatica para la compound_stmt
#compound-stmt → "{"  local-declarations statement-list"}"
#local-declarations = {declaration}, 
#statement-list = {statement}
def compound_stmt():
    match(TokenType.LLAVE_IZQ) # Se espera una llave izquierda
    nodo = nodoNuevo(TipoExpresion.compoundStmt) # Se crea un nodo de tipo CompoundStmt
    nodo.sentencias =  [] # Se inicializa la lista de sentencias
    #vamos guardando los ints y los void en la lista de sentencias
    #es decir, las declaraciones de variables y funciones 
    while token in (TokenType.INT, TokenType.VOID): # Mientras el token sea un int o un void
        nodo.sentencias.append(declaration())
    #luego de que ya no sea declaracion de variables o funciones
    #toca que sea statement
    #que termina en llave derecha o que se termine el archivo
    while (token != TokenType.LLAVE_DER and token != TokenType.ENDFILE):
        nodo.sentencias.append(statement())
    match(TokenType.LLAVE_DER) # Se espera una llave derecha
    return nodo # Se regresa el nodo de tipo CompoundStmt

#region param
#Gramatica para la param
#param → type-specifier ID ( [] )
def param():
    tipo = tokenString # Se guarda el tipo del parametro
    match(token) # Se espera el token
    nombre = tokenString # Se guarda el nombre del parametro
    match(TokenType.ID) # Se espera el token ID
    nodo = nodoNuevo(TipoExpresion.VarDec) # Se crea un nodo de tipo VarDec
    nodo.tipo = tipo # Se le asigna el tipo al nodo
    nodo.nombre = nombre # Se le asigna el nombre al nodo
    if token == TokenType.CORCHETE_IZQ:
        match(TokenType.CORCHETE_IZQ)
        match(TokenType.CORCHETE_DER) # Se espera un corchete derecho
        nodo.longitud = "[]"
    return nodo # Se regresa el nodo de tipo VarDec

#region params
#Gramatica para la params
#params → param {"," param}
def params():
    parametros = [] # Se inicializa la lista de parametros
    if token == TokenType.VOID:
        match(TokenType.VOID)
        return parametros # Se regresa la lista de parametros
    elif token == TokenType.PARENTESIS_DER:# Si el token es un parentesis derecho es decir se termina la lista de parametros
        return parametros
    else:
        parametros.append(param()) # Se agrega el parametro a la lista de parametros
        # Verifica si hay mas parametros
        while token == TokenType.COMA: # Si el token es una coma
            match(TokenType.COMA) # Se espera una coma
            parametros.append(param()) # Se agrega el parametro a la lista de parametros
    return parametros # Se regresa la lista de parametros

#region funDeclaration
#Gramatica para la funDeclaration
#fun-declaration → type ID "(" params ")" comound-stmt
def funDeclaration(tipo, nombre):
    nodo = nodoNuevo(TipoExpresion.FunDec) # Se crea un nodo de tipo FunDec
    nodo.tipo = tipo # Se le asigna el tipo a la funcion
    nodo.nombre = nombre # Se le asigna el nombre a la funcion
    match(TokenType.PARENTESIS_IZQ) # Se espera un parentesis izquierdo
    nodo.parametros = params() # Se llama a la funcion params
    match(TokenType.PARENTESIS_DER) # Se espera un parentesis derecho
    nodo.parteInterna = compound_stmt() # Se llama a la funcion compound_stmt
    return nodo # Se regresa el nodo de tipo FunDec

#region varDeclaration
#Gramatica para la varDeclaration
#var-declaration → type-specifier ID [ "[" NUM "]" ] ;
def varDeclaration(tipo, nombre):
    nodo = nodoNuevo(TipoExpresion.VarDec) # Se crea un nodo de tipo VarDec
    nodo.tipo = tipo # Se le asigna el tipo a la variable
    nodo.nombre = nombre # Se le asigna el nombre a la variable
    if token == TokenType.CORCHETE_IZQ: # Si el token es un corchete izquierdo
        match(TokenType.CORCHETE_IZQ) # Se espera un corchete izquierdo
        nodo.longitud = tokenString # Se le asigna el tamaño a la variable
        match(TokenType.NUM) # Se espera un numero siendo que type-specifier es igual a int
        match(TokenType.CORCHETE_DER) # Se espera un corchete derecho
    match(TokenType.PUNTO_Y_COMA) # Se espera un punto y coma
    return nodo # Se regresa el nodo de tipo VarDec

#region declaration
#gramatica para la funcion declaration
#declaration → var-declaration | fun-declaration
def declaration():
    #Mandamos error si el token no es un int o un void
    if token != TokenType.INT and token != TokenType.VOID:
        syntaxError("Se esperaba un tipo de vacio o entero, encontrado: " + tokenString)
        return None
    
    #Una sabemos que el token es un int o un void
    tipo = tokenString # Se guarda el tipo de la variable o funcion
    match(token) # Se espera un token de tipo int o void
    nombre = tokenString # Se guarda el nombre de la variable o funcion
    match(TokenType.ID) # Se espera un token de tipo ID
    #veificamos si es una varDeclaration o una funDeclaration
    if token == TokenType.PARENTESIS_IZQ:
        return funDeclaration(tipo, nombre)# Se llama a la funcion funDeclaration
    elif token == TokenType.PUNTO_Y_COMA or token == TokenType.CORCHETE_IZQ: # Si el token es un punto y coma
        return varDeclaration(tipo, nombre) # Se llama a la funcion varDeclaration
    else:
        syntaxError("Se esperaba un punto y coma o un parentesis izquierdo, encontrado: " + tokenString)
#region declaration_list
#gramatica de la funcion declaration_list
#declaration_list -> {declaration}
def declaration_list():

    listaTokens = [] # Lista de tokens
    #checka que el token sea un tipo entero o vacio
    while (token == TokenType.INT or token == TokenType.VOID):
        #llama a la funcion declaration
        listaTokens.append(declaration())
    return listaTokens # Regresa la lista de tokens

#inicio de la funcion del EBNF de c- siendo iniciado con program
#donde su gramatica es la siguiente: program -> {declaration}
def programa():
    return declaration_list()

#region imprimir el arbol de sintaxis abstracta
# La función fue inspirada en un extracto dado de ChatGPT, del cual se tomó el 
# método para recorrer e imprimir el árbol en forma de lista. ademas de tener interno la sangria
#y extraer el tipo de nodo, para que se imprima de una manera mas legible
def ArbolImprimir(arbol, edentacion=0):
    if isinstance(arbol, list):
        for nodo in arbol:
            ArbolImprimir(nodo, edentacion)
    elif arbol is not None:
        prefijo = " " * edentacion# Se imprime la sangria
        tipo = arbol.tipoNodo.name if hasattr(arbol.tipoNodo, "name") else str(arbol.tipoNodo) # Se obtiene el tipo del nodo
        if tipo == "VarDec":
            if arbol.longitud is None:
                print(f"{prefijo}Declaracion Variable: {arbol.tipo} {arbol.nombre}")
            else:
                if arbol.longitud == "[]":
                    print(f"{prefijo}Declaracion Variable: {arbol.tipo} {arbol.nombre} []")
                else:
                    print(f"{prefijo}Declaracion Variable: {arbol.tipo} {arbol.nombre} [{arbol.longitud}]")
        elif tipo == "FunDec":
            print(f"{prefijo}Declaracion de Funcion: {arbol.tipo} {arbol.nombre}")
            ArbolImprimir(arbol.parametros, edentacion + 2)
            ArbolImprimir(arbol.parteInterna, edentacion + 2)
        elif tipo == "Var":
            print(f"{prefijo}Variable: {arbol.nombre}")
            ArbolImprimir(arbol.indice, edentacion + 2)
        elif tipo == "Call":
            print(f"{prefijo}Llamada de funcion: {arbol.nombre}")
            ArbolImprimir(arbol.argumentos, edentacion + 2)
        elif tipo == "Op":
            print(f"{prefijo}Operador: {arbol.operador}")
        elif tipo == "Const":
            print(f"{prefijo}Constante: {arbol.valor}")
        elif tipo == "Return":
            print(f"{prefijo}Return")
            ArbolImprimir(arbol.expresion, edentacion + 2)
        elif tipo == "compoundStmt":
            print(f"{prefijo}Sentencia compuesta")
            ArbolImprimir(arbol.sentencias, edentacion + 2)
        elif tipo == "ExpreStmt":
            print(f"{prefijo}Expresion")
            ArbolImprimir(arbol.expresion, edentacion + 2)
        elif tipo == "If":
            print(f"{prefijo}If")
            ArbolImprimir(arbol.condicion, edentacion + 2)
            print(f"{prefijo}Then:")
            ArbolImprimir(arbol.entonces, edentacion + 2)
            if arbol.sino:
                print(f"{prefijo}else:")
                ArbolImprimir(arbol.sino, edentacion + 2)
        elif tipo == "While":
            print(f"{prefijo}While")
            ArbolImprimir(arbol.condicion, edentacion + 2)
            ArbolImprimir(arbol.entonces, edentacion + 2)
        else:
            print(f"{prefijo}Nodo desconocido: {tipo}")
        # chechamos si el nodo tiene hijos
        # y los imprimimos
        if hasattr(arbol, 'hijoIzquierdo'):
            ArbolImprimir(arbol.hijoIzquierdo, edentacion + 2)
        if hasattr(arbol, 'hijoDerecho'):
            ArbolImprimir(arbol.hijoDerecho, edentacion + 2)

#
def globales(prog, pos, long):
    global program, position, proLong
    program = prog # Se asigna el programa
    position = pos # Se asigna la posicion
    proLong = long # Se asigna la longitud del programa
    #activa el scanner
    recibeScanner(prog, pos, long) # Se llama a la funcion recibeScanner

#Llamada a la funcion inicia el analizador sintactico
def parser(imprime= True):
    global token, tokenString, program, position, proLong,edentacion
    edentacion = 0 # Se inicializa la edentacionacion
    #Nota : el lexer anterio se tuvo que modifica para que devuelva la columna, para que imprima el error correctamente
    token, tokenString, lineno, columna = getToken(False) # Se obtiene el primer token
    
    arbolabstrato = programa() # Se llama a la funcion principal del analizador sintactico

    #Verifica si hubo un error de sintaxis
    if token != TokenType.ENDFILE:
        syntaxError("El archivo no ha terminado correctamente")
    
    #if empieza a imprimir el arbol de sintaxis abstracta
    if imprime:
        ArbolImprimir(arbolabstrato)


    return arbolabstrato