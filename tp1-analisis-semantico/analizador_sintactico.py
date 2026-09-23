
# Analizador Sintáctico para el compilador de Pascal Reducido, basado en la gramática proporcionada.

from analizador_lexico import get_siguiente_terminal
from tablaSimbolos import Lexema, Pila, Scope, ErrorTablaSimbolos, PROGRAMA, VARIABLE, PARAMETRO, PROCEDIMIENTO, FUNCION, INTEGER, BOOLEAN
from reglas_tipos import mensaje_tipo, tipo_binario, tipo_unario

# variables globales para el análisis
source_code = ""
tokens = []
errores = []
errores_semanticos = []
pila = None
token_index = 0
preanalisis = None

# diccionario con simbolos a mapear
SYM = {
    "ASIGNAR": ":=",
    "LT": "<",
    "GT": ">",
    "EQ": "=",
    "LE": "<=",
    "GE": ">=",
    "NE": "<>",
    "SUMA": "+",
    "RESTA": "-",
    "MUL": "*",
    "DIV": "/",
    "PAREN_IZ": "(",
    "PAREN_DR": ")",
    "PUNTO_COMA": ";",
    "DOS_PUNTOS": ":",
    "COMA": ",",
    "PUNTO": ".",
    "LLAVE_IZ": "{",
    "LLAVE_DR": "}"
}


def get_next_terminal():
    global preanalisis, source_code
    
    token, error = get_siguiente_terminal(source_code)

    if error:
        preanalisis = None
        raise SyntaxError(error)
        
    if token is not None:
        tipo, valor, linea, col = token

        if valor in SYM:
            valor = SYM[valor]
            
        preanalisis = (tipo, valor, linea, col)
        escribir_output(f"{token[0]}, {token[1]}")
    else:
        preanalisis = None
        
    return preanalisis

def match_val(terminal):
    # se usa para palabras reservadas y simbolos, que se identifican por su valor
    global preanalisis, errores
    if preanalisis is not None and preanalisis[1] == terminal:
        get_next_terminal()
    else:
        linea = preanalisis[2] if preanalisis else "Fin de archivo"
        columna = preanalisis[3] if preanalisis else ""
        encontrado = preanalisis[1] if preanalisis else " "
        error_msg = f"Error de sintaxis en línea {linea}, col {columna}: Se esperaba el valor '{terminal}', se encontró '{encontrado}'."
        print(error_msg)
        errores.append(error_msg)
        raise SyntaxError(error_msg)

def match_type(tipo_esperado):
    # se usa para tokens identificados por su tipo, como id, num, etc.
    global preanalisis, errores
    if preanalisis is not None and preanalisis[0] == tipo_esperado:
        get_next_terminal()
    else:
        linea = preanalisis[2] if preanalisis else "Fin de archivo"
        columna = preanalisis[3] if preanalisis else ""
        encontrado = preanalisis[0] if preanalisis else " "
        error_msg = f"Error de sintaxis en línea {linea}, col {columna}: Se esperaba el tipo '{tipo_esperado}', se encontró '{encontrado}'."
        print(error_msg)
        errores.append(error_msg)
        raise SyntaxError(error_msg)

def programa():
    match_val("program")
    nombre, linea = preanalisis[1], preanalisis[2]
    match_type("id")
    declarar(Lexema(nombre, PROGRAMA, num_linea=linea))
    match_val(";")
    bloque()
    match_val(".")

def bloque():
    if preanalisis[1] == "var":
        declaracion_variables()
        bloque_prima()
    elif preanalisis[1] in ["procedure", "function"]:
        declaracion_subrutinas()
        sentencia_compuesta()
    elif preanalisis[1] == "begin":
        sentencia_compuesta()
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Bloque inválido. Encontrado: {preanalisis[1]}")

def bloque_prima():
    if preanalisis[1] in ["procedure", "function"]:
        declaracion_subrutinas()
        sentencia_compuesta()
    elif preanalisis[1] == "begin":
        sentencia_compuesta()
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Se esperaba 'procedure', 'function' o 'begin'. Encontrado: {preanalisis[1]}")

def declaracion_variables():
    match_val("var")
    def_variable()
    mas_def_variables()

def mas_def_variables():
    if preanalisis[0] == "id":
        def_variable()
        mas_def_variables()

def declaracion_subrutinas():
    subprograma()
    mas_subrutinas()

def mas_subrutinas():
    if preanalisis[1] in ["procedure", "function"]:
        subprograma()
        mas_subrutinas()

def subprograma():
    if preanalisis[1] == "procedure":
        procedimiento()
    else:
        funcion()

def procedimiento():
    match_val("procedure")
    nombre, linea = preanalisis[1], preanalisis[2]
    match_type("id")
    simbolo = abrir_subprograma(nombre, PROCEDIMIENTO, linea)
    procedimiento_prima(simbolo)
    pila.cerrar_ambito()

def procedimiento_prima(simbolo):
    if preanalisis[1] == ";":
        match_val(";")
        bloque()
        match_val(";")
    else:
        declarar_parametros(simbolo, parametros_formales())
        match_val(";")
        bloque()
        match_val(";")

def funcion():
    match_val("function")
    nombre, linea = preanalisis[1], preanalisis[2]
    match_type("id")
    simbolo = abrir_subprograma(nombre, FUNCION, linea)
    funcion_prima(simbolo)
    pila.cerrar_ambito()

def funcion_prima(simbolo):
    if preanalisis[1] == ":":
        match_val(":")
        simbolo.tipo = tipo()
        match_val(";")
        bloque()
        match_val(";")
    else:
        declarar_parametros(simbolo, parametros_formales())
        match_val(":")
        simbolo.tipo = tipo()
        match_val(";")
        bloque()
        match_val(";") 

def abrir_subprograma(nombre, categoria, linea):
    simbolo = Lexema(nombre, categoria, num_linea=linea)
    declarar(simbolo)
    simbolo.ambito = pila.abrir_ambito(nombre)
    return simbolo

def declarar_parametros(simbolo, parametros):
    for nombre, tipo_param, linea in parametros:
        simbolo.agregar_parametro(nombre, tipo_param)
        declarar(Lexema(nombre, PARAMETRO, tipo_param, num_linea=linea))

def parametros_formales():
    match_val("(")
    lista = parametros() + mas_parametros()
    match_val(")")
    return lista

def mas_parametros():
    if preanalisis[1] == ";":
        match_val(";")
        return parametros() + mas_parametros()
    return []

def parametros():
    ids = lista_variables()
    match_val(":")
    tipo_grupo = tipo()
    return [(nombre, tipo_grupo, linea) for nombre, linea in ids]

def mas_ids():
    if preanalisis[1] == ",":
        match_val(",")
        nombre, linea = preanalisis[1], preanalisis[2]
        match_type("id")
        return [(nombre, linea)] + mas_ids()
    return []

def sentencia_compuesta():
    match_val("begin")
    sentencia_compuesta_prima()

def sentencia_compuesta_prima():
    if preanalisis[1] == ";":
        match_val(";")
        match_val("end")
    elif preanalisis[1] == "end":
        match_val("end")
    else:
        lista_sentencias()
        lista_sentencias_cont()

def lista_sentencias_cont():
    if preanalisis[1] == ";":
        match_val(";")
        match_val("end")
    elif preanalisis[1] == "end":
        match_val("end")

def lista_sentencias():
    sentencia()
    mas_sentencias()

def mas_sentencias():
    if preanalisis[1] == ";":
        match_val(";")
        sentencia()
        mas_sentencias()

def sentencia():
    if preanalisis[1] == "if":
        sentencia_abierta()
    else:
        sentencia_cerrada()

def sentencia_cerrada():
    if preanalisis is not None and preanalisis[0] == "id":
        nombre, linea = preanalisis[1], preanalisis[2]
        match_type("id")
        sentencia_id(nombre, linea)
    else:
        match preanalisis[1]:
            case "while":
                linea = preanalisis[2]
                match_val("while")
                controlar_tipo(BOOLEAN, expresion(), linea, "La condición del while")
                match_val("do")
                sentencia_cerrada()
            case "begin":
                sentencia_compuesta()
            case "read" | "write":
                entrada_salida()
            case "if":
                linea = preanalisis[2]
                match_val("if")
                controlar_tipo(BOOLEAN, expresion(), linea, "La condición del if")
                match_val("then")
                sentencia_cerrada()
                match_val("else")
                sentencia_cerrada()

def sentencia_abierta():

    if preanalisis[1] == "if":
        linea = preanalisis[2]
        match_val("if")
        controlar_tipo(BOOLEAN, expresion(), linea, "La condición del if")
        match_val("then")
        sentencia()    
        
        # Asociamos al else al if más cercano
        if preanalisis is not None and preanalisis[1] == "else":
            match_val("else")
            sentencia()
            
    elif preanalisis[1] == "while":
        linea = preanalisis[2]
        match_val("while")
        controlar_tipo(BOOLEAN, expresion(), linea, "La condición del while")
        match_val("do")
        sentencia_abierta()

def sentencia_id(nombre, linea):
    simbolo = buscar_uso(nombre, linea)
    if preanalisis[1] == ":=":
        tipo_destino = controlar_asignacion(simbolo, linea)
        match_val(":=")
        controlar_tipo(tipo_destino, expresion(), linea, f"La asignación a '{nombre}'")
    else:
        # llamada a procedimiento, con o sin argumentos
        argumentos = []
        if preanalisis[1] == "(":
            match_val("(")
            argumentos = lista_expresiones()
            match_val(")")
        controlar_llamada_procedimiento(simbolo, argumentos, linea)

#def while_loop():
#    match_val("while")
#    expresion()
#    match_val("do")
#    sentencia()

def entrada_salida():
    if preanalisis[1] == "read":
        entrada()
    else:
        salida()

def entrada():
    match_val("read")
    match_val("(")
    nombre, linea = preanalisis[1], preanalisis[2]
    match_type("id")
    simbolo = buscar_uso(nombre, linea)
    if simbolo is not None and simbolo.categoria not in (VARIABLE, PARAMETRO):
        error_semantico(linea, f"read necesita una variable y '{nombre}' es {simbolo.categoria}.")
    elif simbolo is not None:
        controlar_tipo(INTEGER, simbolo.tipo, linea, f"La variable '{nombre}' de read")
    match_val(")")

def salida():
    match_val("write")
    match_val("(")
    expresion()
    match_val(")")

def lista_expresiones():
    # devuelve el tipo de cada expresión, en orden
    return [expresion()] + mas_expresiones()

def mas_expresiones():
    if preanalisis[1] == ",":
        match_val(",")
        return [expresion()] + mas_expresiones()
    return []

def expresion():
    return expresion_prima(expresion_simple())

def expresion_prima(tipo_izq):
    if preanalisis[1] in [">", "<", "=", "<=", ">=", "<>"]:
        op, linea = preanalisis[1], preanalisis[2]
        op_comparacion()
        return tipo_operacion(op, tipo_izq, expresion_simple(), linea)
    return tipo_izq

def op_comparacion():
    if preanalisis[1] in [">", "<", "=", "<=", ">=", "<>"]:
        get_next_terminal()
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Se esperaba operador de comparación. Encontrado: {preanalisis[1]}")

def expresion_simple():
    if preanalisis[1] in ["+", "-"]:
        op, linea = preanalisis[1], preanalisis[2]
        signo()
        return mas_terminos(tipo_operacion_unaria(op, termino(), linea))
    else:
        return mas_terminos(termino())

def mas_terminos(tipo_izq):
    if preanalisis[1] in ["+", "-", "or"]:
        op, linea = preanalisis[1], preanalisis[2]
        op_suma()
        tipo_res = tipo_operacion(op, tipo_izq, termino(), linea)
        return mas_terminos(tipo_res)
    return tipo_izq

def op_suma():
    if preanalisis[1] in ["+", "-", "or"]:
        get_next_terminal()
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Se esperaba operador de suma. Encontrado: {preanalisis[1]}")

def signo():
    if preanalisis[1] in ["+", "-"]:
        get_next_terminal()

def termino():
    return mas_factores(factor())

def mas_factores(tipo_izq):
    if preanalisis[1] in ["*", "/", "and"]:
        op, linea = preanalisis[1], preanalisis[2]
        op_mult()
        tipo_res = tipo_operacion(op, tipo_izq, factor(), linea)
        return mas_factores(tipo_res)
    return tipo_izq

def op_mult():
    if preanalisis[1] in ["*", "/", "and"]:
        get_next_terminal()

def factor():
    if preanalisis[0] in ["num"]:
        get_next_terminal()
        return INTEGER
    elif preanalisis[1] in ["true", "false"]:
        get_next_terminal()
        return BOOLEAN
    elif preanalisis[0] == "id":
        nombre, linea = preanalisis[1], preanalisis[2]
        match_type("id")
        simbolo = buscar_uso(nombre, linea)
        argumentos = factor_prima()
        return controlar_uso_en_expresion(simbolo, argumentos, linea)
    elif preanalisis[1] == "(":
        match_val("(")
        tipo_expr = expresion()
        match_val(")")
        return tipo_expr
    elif preanalisis[1] == "not":
        linea = preanalisis[2]
        match_val("not")
        return tipo_operacion_unaria("not", factor(), linea)
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Factor inválido. Encontrado: {preanalisis[1]}")

def factor_prima():
    if preanalisis[1] == "(":
        match_val("(")
        argumentos = lista_expresiones()
        match_val(")")
        return argumentos
    return None

def def_variable():
    ids = lista_variables()
    match_val(":")
    tipo_var = tipo()
    match_val(";")
    for nombre, linea in ids:
        declarar(Lexema(nombre, VARIABLE, tipo_var, num_linea=linea))

def lista_variables():
    nombre, linea = preanalisis[1], preanalisis[2]
    match_type("id")
    return [(nombre, linea)] + mas_ids()

def llamadaProcedimiento():
    match_type("id")
    if preanalisis[1] == "(":
        match_val("(")
        lista_expresiones()
        match_val(")")

def tipo():
    if preanalisis[1] in ["integer", "boolean"]:
        nombre_tipo = preanalisis[1]
        get_next_terminal()
        return nombre_tipo
    else:
        raise SyntaxError(f"Error de sintaxis en línea {preanalisis[2]}, col {preanalisis[3]}: Se esperaba tipo 'integer' o 'boolean'. Encontrado: {preanalisis[1]}")

def escribir_output(texto):
    with open("outputSintactico.txt", "a", encoding='utf-8') as f:
        f.write(texto + "\n")

def escribir_output_semantico(texto):
    with open("outputSemantico.txt", "a", encoding='utf-8') as f:
        f.write(texto + "\n")

def error_semantico(linea, msj):
    # se registra y el análisis sigue
    error_msg = f"Error semántico en línea {linea}: {msj}"
    errores_semanticos.append(error_msg)
    print(error_msg)
    escribir_output_semantico(error_msg)

def declarar(lexema):
    # inserta en el ámbito actual
    try:
        return pila.insertar(lexema)
    except ErrorTablaSimbolos as e:
        error_semantico(lexema.num_linea, str(e))
        return None

def buscar_uso(nombre, linea):
    simbolo = pila.buscar(nombre)
    if simbolo is None:
        error_semantico(linea, f"'{nombre}' no fue declarado.")
    return simbolo

def es_funcion_abierta(simbolo):
    return simbolo.categoria == FUNCION and simbolo.ambito in pila.pila

def controlar_argumentos(simbolo, argumentos, linea):
    esperados = simbolo.cantidad_parametros()
    if len(argumentos) != esperados:
        error_semantico(linea, f"'{simbolo.nombre}' espera {esperados} argumento(s) "
                               f"y recibió {len(argumentos)}.")
        return
    for i, (tipo_param, tipo_arg) in enumerate(zip(simbolo.tipos_parametros(), argumentos), 1):
        controlar_tipo(tipo_param, tipo_arg, linea,
                       f"El argumento {i} de '{simbolo.nombre}'")

def controlar_tipo(esperado, obtenido, linea, contexto):
    msj = mensaje_tipo(esperado, obtenido, contexto)
    if msj:
        error_semantico(linea, msj)

def tipo_operacion(op, izq, der, linea):
    # las reglas de cada operador están en reglas_tipos.py
    tipo_res, errores = tipo_binario(op, izq, der)
    for msj in errores:
        error_semantico(linea, msj)
    return tipo_res

def tipo_operacion_unaria(op, operando, linea):
    tipo_res, errores = tipo_unario(op, operando)
    for msj in errores:
        error_semantico(linea, msj)
    return tipo_res

def controlar_asignacion(simbolo, linea):
    if simbolo is None:
        return None
    if simbolo.categoria in (VARIABLE, PARAMETRO) or es_funcion_abierta(simbolo):
        return simbolo.tipo
    if simbolo.categoria == FUNCION:
        error_semantico(linea, f"Solo se puede asignar el resultado de la función "
                               f"'{simbolo.nombre}' dentro de su cuerpo.")
    else:
        error_semantico(linea, f"No se puede asignar a '{simbolo.nombre}' porque es "
                               f"{simbolo.categoria}.")
    return None

def controlar_llamada_procedimiento(simbolo, argumentos, linea):
    if simbolo is None:
        return
    if simbolo.categoria != PROCEDIMIENTO:
        error_semantico(linea, f"'{simbolo.nombre}' es {simbolo.categoria} y no se "
                               f"puede llamar como procedimiento.")
        return
    controlar_argumentos(simbolo, argumentos, linea)

def controlar_uso_en_expresion(simbolo, argumentos, linea):
    
    if simbolo is None:
        return None
    if simbolo.categoria == FUNCION:
        controlar_argumentos(simbolo, argumentos or [], linea)
        return simbolo.tipo
    if simbolo.categoria in (VARIABLE, PARAMETRO):
        if argumentos is not None:
            error_semantico(linea, f"'{simbolo.nombre}' es {simbolo.categoria}, "
                                   f"no se puede llamar.")
            return None
        return simbolo.tipo
    error_semantico(linea, f"'{simbolo.nombre}' es {simbolo.categoria} y no "
                           f"se puede usar en una expresión.")
    return None

def resumen_semantico():
    cantidad = len(errores_semanticos)
    if cantidad == 0:
        return "No se encontraron errores semánticos."
    if cantidad == 1:
        return "Se encontró 1 error semántico."
    return f"Se encontraron {cantidad} errores semánticos."

def informar_resultado(texto):
    print(texto)
    escribir_output(texto)
    escribir_output_semantico(texto)

def read_source(fileName):
    global errores, errores_semanticos, preanalisis, source_code, pila
    global i, line_number, col

    errores = []
    errores_semanticos = []

    pila = Pila()
    print(">> Iniciando análisis sintáctico...")

    preanalisis = None
    i = 0
    line_number = 1
    col = 1

    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            source_code = file.read()

        with open("outputSintactico.txt", "w", encoding='utf-8') as f:
            f.write("**** TOKENS PROCESADOS ****\n")

        with open("outputSemantico.txt", "w", encoding='utf-8') as f:
            f.write("**** ERRORES SEMÁNTICOS ****\n")

        get_next_terminal()
        
        if preanalisis is not None:
            programa()
            if not errores_semanticos:
                informar_resultado("\n>> Análisis completado con éxito. " + resumen_semantico())
            else:
                informar_resultado("\n>> Análisis sintáctico completo. " + resumen_semantico())
            print("\nRegistro de ámbitos:\n" + str(pila))
        else:
            print("\n>> El archivo está vacío.")

    except SyntaxError as e:
        msg_error = str(e)
        
        errores.append(msg_error)
        
        print(msg_error)
        escribir_output(f"\n[ERROR]: {msg_error}")

        informar_resultado(
            "\n>> El análisis se detuvo por un error sintáctico. "
            "Antes del corte: " + resumen_semantico()
        )
        print("\nRegistro de ámbitos hasta el corte:\n" + str(pila))

    except FileNotFoundError:
        print(f"Error: El archivo '{fileName}' no existe.")
