
# Analizador Sintáctico para el compilador de Pascal Reducido, basado en la gramática proporcionada.

# variables globales para el análisis
tokens = []
errores = []
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
    "MULT": "*",
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
    global token_index, preanalisis, tokens
    if token_index < len(tokens):
        preanalisis = tokens[token_index]
        token_index += 1
    else:
        preanalisis = None # no hay mas tokens.
    return preanalisis

def match_val(terminal):
    # se usa para palabras reservadas y simbolos, que se identifican por su valor
    global preanalisis, errores
    if preanalisis is not None and preanalisis[1] == terminal:
        get_next_terminal()
    else:
        error_msg = f"Error de sintaxis: Se esperaba el valor '{terminal}', se encontró '{preanalisis[1]}'."
        print(error_msg)
        errores.append(error_msg)
        raise SyntaxError(error_msg)

def match_type(tipo_esperado):
    # se usa para tokens identificados por su tipo, como id, num, etc.
    global preanalisis, errores
    if preanalisis is not None and preanalisis[0] == tipo_esperado:
        get_next_terminal()
    else:
        error_msg = f"Error de sintaxis: Se esperaba el tipo '{tipo_esperado}', se encontró '{preanalisis[0]}'."
        print(error_msg)
        errores.append(error_msg)
        raise SyntaxError(error_msg)

def programa():
    match_val("program")
    match_type("id")
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
        raise SyntaxError(f"Error: Bloque inválido. Encontrado: {preanalisis[1]}")

def bloque_prima():
    if preanalisis[1] in ["procedure", "function"]:
        declaracion_subrutinas()
        sentencia_compuesta()
    elif preanalisis[1] == "begin":
        sentencia_compuesta()
    else:
        raise SyntaxError("Error: Se esperaba 'procedure', 'function' o 'begin'")

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
    match_type("id")
    procedimiento_prima()

def procedimiento_prima():
    if preanalisis[1] == "(":
        parametros_formales()
        match_val(";")
        bloque()
        match_val(";")
    else:
        match_val(";")
        bloque()
        match_val(";")

def funcion():
    match_val("function")
    match_type("id")
    funcion_prima()

def funcion_prima():
    if preanalisis[1] == "(":
        parametros_formales()
        match_val(":")
        tipo()
        match_val(";")
        bloque()
        match_val(";")
    else:
        match_val(":")
        tipo()
        match_val(";")
        bloque()
        match_val(";")

def parametros_formales():
    match_val("(")
    parametros()
    mas_parametros()
    match_val(")")

def mas_parametros():
    if preanalisis[1] == ";":
        match_val(";")
        parametros()
        mas_parametros()

def parametros():
    match_type("id")
    mas_ids()
    match_val(":")
    tipo()

def mas_ids():
    if preanalisis[1] == ",":
        match_val(",")
        match_type("id")
        mas_ids()

def sentencia_compuesta():
    match_val("begin")
    sentencia_compuesta_prima()

def sentencia_compuesta_prima():
    if preanalisis[1] in ["id", "if", "while", "begin", "read", "write"]:
        lista_sentencias()
        lista_sentencias_cont()
    elif preanalisis[1] == ";":
        match_val(";")
        match_val("end")
    elif preanalisis[1] == "end":
        match_val("end")

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
    global token_index, preanalisis
    
    if preanalisis[1] in ["id", "while", "begin", "read", "write"]:
        sentencia_cerrada()
    elif preanalisis[1] == "if":
        sentencia_abierta()

def sentencia_cerrada():
    match preanalisis[1]:
        case "id":
            match_type("id")
            sentencia_id()
        case "while":
            while_loop()
        case "begin":
            sentencia_compuesta()
        case "read" | "write":
            entrada_salida()
        case "if":
            match_val("if")
            expresion()
            match_val("then")
            sentencia_cerrada()
            match_val("else")
            match_val("then")
            sentencia_cerrada()

def sentencia_abierta():
    global preanalisis
    match_val("if")
    expresion()
    match_val("then")
    sentencia()
    
    if preanalisis is not None and preanalisis[1] == "else":
        match_val("else")
        sentencia_abierta()

def sentencia_id():
    if preanalisis[1] == ":=":
        match_val(":=")
        expresion()
    elif preanalisis[1] == "(":
        match_val("(")
        lista_expresiones()
        match_val(")")

def while_loop():
    match_val("while")
    expresion()
    match_val("do")
    sentencia()

def entrada_salida():
    if preanalisis[1] == "read":
        entrada()
    else:
        salida()

def entrada():
    match_val("read")
    match_val("(")
    match_type("id")
    match_val(")")

def salida():
    match_val("write")
    match_val("(")
    expresion()
    match_val(")")

def lista_expresiones():
    expresion()
    mas_expresiones()

def mas_expresiones():
    if preanalisis[1] == ",":
        match_val(",")
        expresion()
        mas_expresiones()

def expresion():
    expresion_simple()
    expresion_prima()

def expresion_prima():
    if preanalisis[1] in [">", "<", "=", "<=", ">=", "<>"]:
        op_comparacion()
        expresion_simple()

def op_comparacion():
    if preanalisis[1] in [">", "<", "=", "<=", ">=", "<>"]:
        get_next_terminal()
    else:
        raise SyntaxError("Error: Se esperaba operador de comparación")

def expresion_simple():
    if preanalisis[1] in ["+", "-"]:
        signo()
        termino()
        mas_terminos()
    elif preanalisis[1] in ["num", "id", "(", "true", "false", "not"]:
        termino()
        mas_terminos()

def mas_terminos():
    if preanalisis[1] in ["+", "-", "or"]:
        op_suma()
        termino()
        mas_terminos()

def op_suma():
    if preanalisis[1] in ["+", "-", "or"]:
        get_next_terminal()
    else:
        raise SyntaxError("Error: Se esperaba operador de suma")

def signo():
    if preanalisis[1] in ["+", "-"]:
        get_next_terminal()

def termino():
    factor()
    mas_factores()

def mas_factores():
    if preanalisis[1] in ["*", "/", "and"]:
        op_mult()
        factor()
        mas_factores()

def op_mult():
    if preanalisis[1] in ["*", "/", "and"]:
        get_next_terminal()

def factor():
    if preanalisis[0] in ["num"]:
        get_next_terminal()
    elif preanalisis[0] == "id":
        match_type("id")
        factor_prima()
    elif preanalisis[1] == "(":
        match_val("(")
        expresion()
        match_val(")")
    elif preanalisis[1] in ["true", "false"]:
        get_next_terminal()
    elif preanalisis[1] == "not":
        match_val("not")
        factor()
    else:
        raise SyntaxError(f"Error: Factor inválido. Encontrado: {preanalisis[1]}")

def factor_prima():
    if preanalisis[1] == "(":
        match_val("(")
        lista_expresiones()
        match_val(")")

def def_variable():
    lista_variables()
    match_val(":")
    tipo()
    match_val(";")

def lista_variables():
    match_type("id")
    mas_ids()

def llamadaProcedimiento():
    match_type("id")
    if preanalisis[1] == "(":
        match_val("(")
        lista_expresiones()
        match_val(")")

def tipo():
    if preanalisis[1] in ["integer", "boolean"]:
        get_next_terminal()
    else:
        raise SyntaxError("Error: Se esperaba tipo 'integer' o 'boolean'")

def read_source(fileName):
    global tokens, errores
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',', 1)
                if len(parts) == 2:
                    type_token = parts[0].strip().lower()
                    value_token = parts[1].strip()
                    
                    if value_token in SYM:
                        value_token = SYM[value_token]
                    elif type_token not in ['id', 'num', 'constante_numerica']:
                        value_token = value_token.lower()
                        
                    tokens.append((type_token, value_token))
                else:
                    msg = f"Error léxico: La línea '{line}' no tiene el formato esperado."
                    errores.append(msg)
                    print(msg)

        get_next_terminal()
        
        try:
            programa()
            print("\n>> Análisis sintáctico completado con éxito.")
        except SyntaxError:
            print("\n>> El análisis falló debido a errores sintácticos.")

        try:
            with open("outputSintactico.txt", 'w', encoding='utf-8') as output:
                output.write("**** TOKENS PROCESADOS ****\n")
                for token in tokens:
                    output.write(f"{token[0]}, {token[1]}\n")
                
                output.write("\n**** ERRORES ****\n")
                if not errores:
                    output.write("No se encontraron errores.\n")
                else:
                    for error in errores:
                        output.write(f"{error}\n")
                        
            print("Resultados guardados correctamente en 'outputSintactico.txt'.")
            
        except IOError:
            print("Error: No se pudo escribir en el archivo 'output.txt'.")

    except FileNotFoundError:
        print(f"Error: El archivo '{fileName}' no existe.")
