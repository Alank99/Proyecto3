from globalTypes import *
from Parser import *

f = open("test.c-", "r")
program = f.read()
programLong = len(program)
program = program + "$"
posicion = 0

#funciones para pasar los valores iniciales de las variables globales

globales(program, posicion, programLong)

AST = parser(True)