import re

# Op relacional = <, >, =, !, <=, >=, ==, !=,
# Op lógicos = &, &&, |, ||, !
# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|while|for|return|int|float|void|class|def|print)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+\b',
    "OPERATOR": r'<=|>=|==|!=|&&|"|[\+\-\*/=<>\!\||\|\']',
    "DELIMITER": r'[(),;{}]',  # Paréntesis, llaves, punto y coma
    "WHITESPACE": r'\s+'  # Espacios en blanco
}


def tokenize(text):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)

    tokens_encontrados = []

    for match in patron_regex.finditer(text):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados


class NodoAST:
    # Clase base para todos los nodos del AST
    def traducir(self):
        raise NotImplementedError("Método traducir no implementado en este nodo")
    
    def generar_codigo(self):
        raise NotImplementedError("Método generar_codigo no implementado en este nodo")

class NodoPrograma(NodoAST):
    # Nodo que representa el programa como un conjunto de funciones
    def __init__(self, funciones):
        self.funciones = funciones

    def traducir(self):
        return "\n\n".join(f.traducir() for f in self.funciones)

    def generar_codigo(self):
        return "\n\n".join(f.generar_codigo() for f in self.funciones)

class NodoFuncion(NodoAST):
    # Nodo que representa una función
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

    def traducir(self):
        params = ", ".join(p.traducir() for p in self.parametros)
        cuerpo = "\n   ".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre[1]}({params}):\n   {cuerpo}"
    
    def generar_codigo(self):
        codigo  = f'{self.nombre[1]}:\n'
        codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
        return codigo


class NodoParametro(NodoAST):
    # Nodo que representa un parámetro de función
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

    def traducir(self):
        return f"{self.nombre[1]}"


class NodoAsignacion(NodoAST):
    # Nodo que representa una asignación de variable
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

    def traducir(self):
        return f"{self.nombre[1]} = {self.expresion.traducir()}"

    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
        codigo += f'\n   mov [{self.nombre[1]}], eax; Guardar resultado en {self.nombre[1]}'
        return codigo


class NodoOperacion(NodoAST):
    # Nodo que representa una operación aritmética
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def optimizar(self):
        if isinstance(self.izquierda, NodoOperacion):
            self.izquierda = self.izquierda.optimizar()
        else:
            izquierda = self.izquierda
        if isinstance(self.derecha, NodoOperacion):
            self.derecha = self.derecha.optimizar()
        else:
            derecha = self.derecha

        # Si ambos operandos son números, evaluamos la operación
        if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
            if self.operador == "+":
                return NodoNumero(izquierda.valor + derecha.valor)
            elif self.operador == "-":
                return NodoNumero(izquierda.valor - derecha.valor)
            elif self.operador == "*":
                return NodoNumero(izquierda.valor * derecha.valor)
            elif self.operador == "/" and derecha.valor != 0:
                return NodoNumero(izquierda.valor / derecha.valor)
        # Simplificación algebraica
        if self.operador == '*' and isinstance(derecha, NodoNumero) and derecha.valor == 1:
            return izquierda
        if self.operador == '*' and isinstance(izquierda, NodoNumero) and izquierda.valor == 1:
            return derecha
        if self.operador == '+' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
            return izquierda
        if self.operador == '+' and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
            return derecha

        return NodoOperacion(izquierda, self.operador, derecha)
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador[1]} {self.derecha.traducir()}"
        
    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo()) # Cargar el operando izquierdo
        codigo.append('   push eax; guardar en la pila') # Guardar en la pila
        codigo.append(self.derecha.generar_codigo()) # Cargar el operando derecho
        codigo.append('   pop ebx; recuperar el primer operando') # Sacar de la pila
        # ebx = op1 y eax = op2
        if self.operador[1] == '+':
            codigo.append('   add eax, ebx; eax = eax + ebx')
        elif self.operador[1] == '-':
            codigo.append('   sub ebx, eax; ebx = ebx - eax')
            codigo.append('   mov eax, ebx; eax = ebx')
        elif self.operador[1] == '*':
            codigo.append('   imul ebx; eax = eax * ebx')
        elif self.operador[1] == '/':
            codigo.append('   mov edx, 0; limpiar edx')
            codigo.append('   idiv ebx; eax = eax / ebx')
        return '\n'.join(codigo)


class NodoRetorno(NodoAST):
    # Nodo que representa a la sentencia return
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"return {self.expresion.traducir()}"

    def generar_codigo(self):
        return self.expresion.generar_codigo() + '\n   ret ; Retornar desde la subrutina'


class NodoIdentificador(NodoAST):
    # Nodo que representa a un identificador
    def __init__(self, nombre):
        self.nombre = nombre

    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        return f'   mov eax, {self.nombre[1]} ; Cargar variable {self.nombre[1]} en eax'

class NodoNumero(NodoAST):
    # Nodo que representa un número
    def __init__(self, valor):
        self.valor = valor

    def traducir(self):
        return str(self.valor[1])
    
    def generar_codigo(self):
        return f'   mov eax, {self.valor[1]} ; Cargar número {self.valor[1]} en eax'

class NodoWhile(NodoAST):
    # Nodo que representa a un ciclo while
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

class NodoIf(NodoAST):
    # Nodo que representa una sentencia if
    def __init__(self, condicion, cuerpo, sino=None):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.sino = sino

    def generar_codigo(self):
        etiqueta_else = f'etiqueta_else_{id(self)}'
        etiqueta_fin = f'etiqueta_fin_{id(self)}'

        codigo = []
        # Generar código para evaluar la condición
        codigo.append(self.condicion.generar_codigo())
        codigo.append('   cmp eax, 0 ; Comparar resultado con 0')

        if self.sino:
            codigo.append(f'   je {etiqueta_else} ; Saltar a else si la condición es falsa')
        else:
            codigo.append(f'   je {etiqueta_fin} ; Saltar al final si la condición es falsa')

        # Código del cuerpo del if
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())

        if self.sino:
            codigo.append(f'   jmp {etiqueta_fin} ; Saltar al final del if')
            codigo.append(f'{etiqueta_else}:')
            for instruccion in self.sino:
                codigo.append(instruccion.generar_codigo())

        codigo.append(f'{etiqueta_fin}:')
        return '\n'.join(codigo)
    
    
class NodoFor(NodoAST):
    # Nodo que representa a un ciclo for
    def __init__(self, inicializacion, condicion, actualizacion, cuerpo):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.actualizacion = actualizacion
        self.cuerpo = cuerpo

class NodoPrint(NodoAST):
    # Nodo que representa a la función print
    def __init__(self, expresion):
        self.expresion = expresion

class NodoTexto(NodoAST):
    # Nodo que representa un texto
    def __init__(self, valor):
        self.valor = valor
    
def generar_codigo_if_else(nodo_if):
    """
    Genera código ensamblador para una estructura if-else con nombres más claros.
    """
    codigo_asm = ""
    etiqueta_salto_else = f"salto_else_{id(nodo_if)}"
    etiqueta_salto_fin = f"salto_fin_{id(nodo_if)}"

    # Evaluar condición
    codigo_asm += f"; Evaluar la condición\n"
    codigo_asm += nodo_if.condicion.generar_codigo() + "\n"  # Generar código para evaluar la condición
    codigo_asm += f"CMP AX, 0\n"  # Comparar el resultado con 0
    codigo_asm += f"JE {etiqueta_salto_else}\n"  # Si es falso, saltar al ELSE

    # Código del bloque IF
    codigo_asm += f"; Código del bloque IF\n"
    codigo_asm += nodo_if.bloque_if.generar_codigo() + "\n"
    codigo_asm += f"JMP {etiqueta_salto_fin}\n"  # Saltar al final después del IF

    # Código del bloque ELSE (si existe)
    codigo_asm += f"{etiqueta_salto_else}:\n"
    if nodo_if.bloque_else:
        codigo_asm += f"; Código del bloque ELSE\n"
        codigo_asm += nodo_if.bloque_else.generar_codigo() + "\n"

    # Fin de la estructura
    codigo_asm += f"{etiqueta_salto_fin}:\n"

    return codigo_asm

from analizador import tokenize, Parser

texto = """
int suma(int a, int b) {
    int c = a + b;
    if (c > 10) {
        return c;
    } else {
        return 0;
    }
}

void main() { 
    int x = 0;
    while (x < 8) {
        x = x + 1;
    }
    int s = suma(3, 4);
    print(s);
} 
"""

# Tokenización
tokens = tokenize(texto)
print("Tokens encontrados:")
for token in tokens:
    print(token)

# Análisis sintáctico
parser = Parser(tokens)
arbol_ast = parser.parsear()

# Traducción e interpretación del código
print("\nCódigo traducido a Python:")
print(arbol_ast.traducir())

print("\nGeneración de código ensamblador:")
print(arbol_ast.generar_codigo())