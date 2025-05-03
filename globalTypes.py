#Programa que almacena todos los tokens coorrespodientes en una enum 
from enum import Enum, auto

# Definición de la clase TokenType que hereda de Enum
class TokenType(Enum):
    # Definición de los tokens externos al lenguaje
    ENDFILE = "EOF"
    ERROR = "ERROR"

    # Definición de los tipos de tokens
    ID = "IDENTIFICADOR"
    NUM = "NUMERO"
    COMENTARIO = "COMENTARIO"
    COMA = "COMA"
    PUNTO_Y_COMA = "PUNTO_Y_COMA"
    ASIGNACION = "ASIGNACION"
    SUMA = "SUMA"
    RESTA = "RESTA"
    MULTIPLICACION = "MULTIPLICACION"
    DIVISION = "DIVISION"
    PARENTESIS_IZQ = "PARENTESIS_IZQ"
    PARENTESIS_DER = "PARENTESIS_DER"
    LLAVE_IZQ = "LLAVE_IZQ"
    LLAVE_DER = "LLAVE_DER"
    CORCHETE_IZQ = "CORCHETE_IZQ"
    CORCHETE_DER = "CORCHETE_DER"
    MENOR = "MENOR"
    MAYOR = "MAYOR"
    MENOR_IGUAL = "MENOR_IGUAL"
    MAYOR_IGUAL = "MAYOR_IGUAL"
    IGUAL = "IGUAL"
    DISTINTO = "DISTINTO"
    #palabras reservadas
    ELSE = "else"
    IF = "if"
    WHILE = "while"
    INT = "int"
    VOID = "void"
    RETURN = "return" 

#Definicion de las palabras reservadas
class PalabrasReservadas(Enum):
    # Definición de las palabras reservadas
    ELSE = "else"
    IF = "if"
    WHILE = "while"
    INT = "int"
    VOID = "void"
    RETURN = "return"   

# Definición de los operadores 
class Estados(Enum):
    # Definición de los estados del analizador léxico
    INICIO = 0
    EN_INICIOCOMENTARIO = 1
    EN_ASIGNACION = 2
    EN_NUMERO = 3
    EN_ID = 4
    EN_MENOR = 5
    EN_MAYOR = 6
    EN_DISTINTO = 7
    EN_MEDIOCOMENTARIO = 8
    EN_FINALCOMENTARIO = 9
    FINALIZADO = 10
    EN_SUMA = 11
    EN_RESTA = 12
    EN_MULTIPLICACION = 13
    EN_DIVISION = 14

    #---------- Para el AST o parser ----------

    # Definimos los tipos de nodos del árbol´

class TipoExpresion(Enum):
    Const = auto()
    Var = auto()
    Call = auto()
    VarDec = auto()
    FunDec = auto()
    ExpreStmt = auto()
    Op = auto()
    Return = auto()
    If = auto()
    While = auto()
    compoundStmt = auto()
       


#Definimos el arbol de sintaxis abstracto

class NodoArbol:
    def __init__(self):
        self.hijoDerecho = None
        self.hijoIzquierdo = None
        self.nombre = None
        self.tipo = None
        self.valor = None
        self.operador = None
        self.sentencias = []
        self.indice = None
        self.longitud = None #Almacena el tamaño de la variable
        self.tipoNodo = None #Almacena el enum del tipoExpresion , donde te dice que tipo de nodo es
        self.sino = None #Es la parte else del if 
        self.expresion = None #expresion es igual a la expresion que se va a evaluar
        self.argumentos = [] #argumentos es igual a los argumentos que se le pasan a la funcion
        self.entonces = None #entonces es igual a la sentencia que se va a ejecutar si la expresion es verdadera
        self.parametros = [] #parametros es igual a los parametros que se le pasan a la funcion
        self.parteInterna = None #parteInterna es igual a la parte interna de la funcion
        self.condicion = None #condicion es igual a la condicion que se va a evaluar
