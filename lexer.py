from globalTypes import *

#Analizador de lexico del lenguaje de C-
# Autor: Alan Anthony Hernandez Perez
#Con asistencia de copilot 

#region declaracion de variables y palabras reservadas
#Funcion que permite que al importar el lexer, pueda acceder a las variables 
#que permita ejecutar el analizador lexico
def recibeScanner(prog, pos, long):
    global program
    global position
    global programLength
    program = prog
    position = pos
    programLength = long

lineno = 1 #linea actual del programa
columna = 0 #columna actual del programa

#Funcion que verifica si el token es una palabra reservada o caso 
# sera un identificador
def PalabrasReservadasComparacion(tokenString):
    for s in PalabrasReservadas:
        if tokenString == s.value:
            return TokenType(tokenString)
    return TokenType.ID

Espacios = " \t\n\r"
Operadores = "+-*/!=<>"
Parentisis = "()[]{}"
Puntos = ";,"
#endregion

#region Manejador de errores
#Funcion que maneja si un error es detectado
def ErrorSintactico(posicion, tipoError, textoInfo = None):
    if tipoError == 1:
        punteroDelError = posicion
        posicion = punteroDelError - 1
        textoError = ""
        
        # Retrocede hasta el inicio de la línea
        while program[posicion] != "\n" :
            posicion -= 1

        # Avanzamos uno para llegar al inicio de la línea
        posicion += 1
        inicioLinea = posicion
        c = program[posicion]

        print

        # Recorre la línea y la guarda pero guarda el error donde se detuvo
        while c not in Espacios or posicion <= punteroDelError:
            textoError += c
            posicion += 1
            if posicion >= programLength:
                break
            c = program[posicion]
        posicion -= 1

        # Calcula la posición del error dentro de la línea , que este extrato fue obtenido por chat gpt
        columnaDelError = punteroDelError - inicioLinea +1

        print("Error "+ textoInfo +" en la línea:", lineno)
        print("Texto: ", textoError)
        print("       " + " " * columnaDelError + "^")

        return posicion, textoError# Regresa del final del error
    else:
        print("Error por no cerrar el comentario, en la línea: ", lineno)
        # Regresa el puntero al final del error
        return None, None
#endregion
        


#region definicion gettoken
#Funcion que analiza el token y lo clasifica
#Regresa el el token y lexema correspondiente
def getToken(imprime = True):
    #global position, lineno
    global position, lineno, columna
    #inicializa de donde se guardara el token
    tokenString = "" 
    #estado del token
    currentToken = None
    #Guarda el estado del token
    guardado = True
    #estado del analizador
    estado = Estados.INICIO

#endregion
    #empieza a analizar el programa
    #se detiene cuando se llega al final del programa con el simbolo $ del string
    while estado != Estados.FINALIZADO:
        c = program[position]
        guardado = True
        #region Inicio del analizador
        #Comporbar el estado del analizador
        #si el estado es el inicial es decir el token string esta vacio
        #entonces se analiza el primer caracter para determinar el estado siguente

        if estado == Estados.INICIO:
            #si el caracter es un digito
            if c.isdigit():
                estado = Estados.EN_NUMERO
            #si el caracter es una letra
            elif c.isalpha():
                estado = Estados.EN_ID
            #si el caracter es un espacio o tabulador o salto de linea
            #se despecia el caracter
            elif c in Espacios:
                guardado = False
                if (c == '\n'):
                    #print("línea: ", lineno)
                    lineno += 1       
            #si el caracter es un simbolo de operacion
            elif c in Operadores:
                #Checa si es un simbolo combinado como <= >= != /*
                if c == "<":
                   estado = Estados.EN_MENOR
                elif c == ">":
                   estado = Estados.EN_MAYOR
                elif c == "=":
                   estado = Estados.EN_ASIGNACION
                elif c == "!":
                   estado = Estados.EN_DISTINTO
                elif c == "/":
                    if program[position+1] == "*":
                        c  = program[position+2]
                        guardado = False
                        estado = Estados.EN_MEDIOCOMENTARIO

                #si el caracter es un simbolo de operacion
                    else:
                        estado = Estados.EN_DIVISION
                elif c == "+":
                    estado = Estados.EN_SUMA
                elif c == "-":
                    estado = Estados.EN_RESTA
                elif c == "*":
                    estado = Estados.EN_MULTIPLICACION
            #si el caracter es un simbolo de puntuacion, parentesis o el caracter de fin de archivo
            else:
                estado = Estados.FINALIZADO
                if position == programLength or c == "$": #EOF
                    guardado = False
                    currentToken = TokenType.ENDFILE

                elif c == "(":
                    currentToken = TokenType.PARENTESIS_IZQ
                elif c == ")":
                    currentToken = TokenType.PARENTESIS_DER
                elif c == "[":
                    currentToken = TokenType.CORCHETE_IZQ
                elif c == "]":
                    currentToken = TokenType.CORCHETE_DER
                elif c == "{":
                    currentToken = TokenType.LLAVE_IZQ
                elif c == "}":
                    currentToken = TokenType.LLAVE_DER
                elif c == ";":
                    currentToken = TokenType.PUNTO_Y_COMA
                elif c == ",":
                    currentToken = TokenType.COMA
                else:
                    currentToken = TokenType.ERROR
        #endregion
         
        #region ID
        #En caso de el estado sea un identificador
        elif estado == Estados.EN_ID:
            #Evalua si el caracter ya no es una letra 
            if not c.isalpha():
                if c in Espacios or c in Operadores or c in Parentisis or c == "$" or c in Puntos:
                    #das un paso atras para que el caracter no se pierda
                    if position <= programLength:
                        position -= 1
                    #dejamos de guardar el token
                    guardado = False
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ID
                #da error si el caracter es un digito o simbolo
                else:
                    guardado = False
                    posFinal, tokenString = ErrorSintactico(position,1, "en la forma de un identificador")
                    if posFinal <= programLength:
                        position = posFinal
                    else:
                        position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
        #endregion

        #region NUMERO
        #En caso de el estado sea un numero
        elif estado == Estados.EN_NUMERO:
            #Evalua si el caracter ya no es un digito 
            if not c.isdigit():
                #si el siguiente caracter es un espacio o coma o parentesis
                if c in Espacios or c in Operadores or c in Parentisis or c == "$" or c in Puntos:
                    #das un paso atras para que el caracter no se pierda
                    if position <= programLength:
                        position -= 1
                    #dejamos de guardar el token
                    guardado = False
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.NUM
                #da error si el caracter es un simbolo o letra
                else:
                    guardado = False
                    posFinal, tokenString = ErrorSintactico(position,1, "en la forma de un numero")
                    if posFinal <= programLength:
                        position = posFinal
                    else:
                        position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
        #endregion

      
        #En caso de el estado sea menor
        #region Menor
        elif estado == Estados.EN_MENOR:
            #Checa si el siguiente caracter es un igual
            if c == "=":
                estado = Estados.FINALIZADO
                currentToken = TokenType.MENOR_IGUAL
            elif c in Espacios or c.isalpha() or c.isdigit() or c == "$":
                #das un paso atras para que el caracter no se pierda
                if position <= programLength:
                    position -= 1
                #dejamos de guardar el token
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.MENOR
            else:
                #en caso de que no sea un numero o letra o espacio
                #mandamos error
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion del menor o menor igual")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
        #endregion

        #region Mayor
        elif estado == Estados.EN_MAYOR:
            #Checa si el siguiente caracter es un igual
            if c == "=":
                estado = Estados.FINALIZADO
                currentToken = TokenType.MAYOR_IGUAL
            elif c in Espacios or c.isalpha() or c.isdigit() or c == "$":
                #das un paso atras para que el caracter no se pierda
                if position <= programLength:
                    position -= 1
                #dejamos de guardar el token
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.MAYOR
            else:
                #en caso de que no sea un numero o letra o espacio
                #mandamos error
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion del mayor o mayor igual")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
        #endregion
        #region Distinto
        elif estado == Estados.EN_DISTINTO:
            #Checa si el siguiente caracter es un igual
            if c == "=":
                estado = Estados.FINALIZADO
                currentToken = TokenType.DISTINTO
            else:
                #en caso de que no sea =
                #mandamos error
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la forma de la formacion del distinto")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
        #endregion

        #region Asignacion
        elif estado == Estados.EN_ASIGNACION:
            #Checa si el siguiente caracter es un igual
            if c == "=":
                estado = Estados.FINALIZADO
                currentToken = TokenType.IGUAL
            elif c in Espacios or c.isalpha() or c.isdigit() or c == "$":
                estado = Estados.FINALIZADO
                currentToken = TokenType.ASIGNACION
            else:
                #en caso de que no sea un numero o letra o espacio
                #mandamos error
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion de la asignacion")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR

                
        #endregion

        #region Suma
        elif estado == Estados.EN_SUMA:
            #Verifica que no sea un operador, lo demas es valido y ya se indentifico el token
            if c in Espacios or c.isalpha() or c.isdigit() or c == "$"or c in Puntos:
                #guarda el token
                if position <= programLength:
                    position -= 1
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.SUMA
            else:
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion de la suma")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                
        #endregion

        #region Resta
        elif estado == Estados.EN_RESTA:
            if c in Espacios or c.isalpha() or c.isdigit() or c == "$" or c in Puntos:
                #guarda el token
                if position <= programLength:
                    position -= 1
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.RESTA
            else:
                print("Error en resta: ", c)
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion de la resta")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                
        #endregion
        

        #region Division
        elif estado == Estados.EN_DIVISION:
            if c in Espacios or c.isalpha() or c.isdigit() or c == "$" or c in Puntos:
                #guarda el token
                if position <= programLength:
                    position -= 1
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.DIVISION
            else:
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion de la division")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR


        #region Multiplicacion
        elif estado == Estados.EN_MULTIPLICACION:
            if c in Espacios or c.isalpha() or c.isdigit() or c == "$" or c in Puntos:
                #guarda el token
                if position <= programLength:
                    position -= 1
                guardado = False
                estado = Estados.FINALIZADO
                currentToken = TokenType.MULTIPLICACION
            else:
                guardado = False
                posFinal, tokenString = ErrorSintactico(position,1, "en la formacion de la multiplicacion")
                if posFinal <= programLength:
                    position = posFinal
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR
                else:
                    position -= 1
                    c = program[position]
                    estado = Estados.FINALIZADO
                    currentToken = TokenType.ERROR

        #endregion

        #region Comentarios  

        #Se hacer de manera aislada el if del comentario debido a que si se metiera en el la estructura principal
        #se perderia el caracter de la division y no se guardaria el token y los elementos internos del comentario
        #se tomaria como un error como si fueran tokens validos
        if estado == Estados.EN_MEDIOCOMENTARIO:
        #siendo que ya se asumio que el los primeros dos caracteres son / y *
        #solo va checando que el siguiente caracter sea * para que salte al siguiente estado
        #si no es lo ignora los caracters a menos del salto de linea
            guardado = False
            if c == "\n":
                lineno += 1
            elif c == "*" and program[position-1] != "/":

                estado = Estados.EN_FINALCOMENTARIO
            #en caso de que se acabe el comentario sin cerrar mandamos error
            elif c == "$":
                _, _ = ErrorSintactico(position,2)
                estado = Estados.FINALIZADO
                currentToken = TokenType.ERROR
                if position <= programLength:
                    position -= 1
                      

        elif estado == Estados.EN_FINALCOMENTARIO:
            #si es el final del programa y no se cerro el comentario
            #mandamos error
            guardado = False
            if c == "$":
                print("Error: comentario no cerrado")
                _, _ = ErrorSintactico(position,2)
                c = program[position-2]
                estado = Estados.FINALIZADO
                currentToken = TokenType.ERROR
                
                            
            #si el siguiente caracter es un / entonces es el final del comentario
            #Se vuelve al estado inicial
            #en caso contrario se vuelve al estado medio de comentario
            if c == "/":
                estado = Estados.INICIO
                guardado = False
            elif c == Espacios:
                if c == "\n":
                    lineno += 1
            else:
                estado = Estados.EN_MEDIOCOMENTARIO
                guardado = False
        #endregion

        #region finalizado
        #En caso de el estado sea finalizado
        elif estado == Estados.FINALIZADO:
            None

        if guardado:
            tokenString = tokenString + c
        #si el estado es finalizado
        if estado == Estados.FINALIZADO:
            #si el token es un identificador
            if currentToken == TokenType.ID:
                #verifica si es una palabra reservada
                currentToken = PalabrasReservadasComparacion(tokenString)
            #si el token es un numero
        position += 1
    if imprime:
        print(lineno, currentToken," = ", tokenString)

    columna = position - program.rfind("\n",0,position) - 1
    return currentToken, tokenString, lineno, columna
    
        