def analyzer(source):
    keyword_table = ["program", "var", "function", "procedure", "integer", "begin", "boolean", "end", "if", "then", "else", "while", "do", "read", "write", "and", "or", "not"]
    tokens = []
    errores = []
    i = 0
    n = len(source)
    line_number = 1
    col = 1

    while i < n:
        c = source[i]

        # ignorar espacios en blanco, tabulaciones y saltos de línea
        if c in ' \t\n\r':
            i += 1
            if(c == '\n'):
                line_number += 1
                col = 1
            else:
                col += 1
            continue

        # analizar símbolos de un solo caracter o compuestos
        match c:
            case ':':
                if i + 1 < n and source[i + 1] == '=':
                    tokens.append(("ASIGNAR", ":="));
                    i += 2;
                    col += 2;
                else:
                    tokens.append(("dos_puntos", "DOS_PUNTOS"));
                    i += 1;
                    col += 1;
            case '<':
                if i + 1 < n and source[i + 1] == '>':
                    tokens.append(("op_relacional", "NE"));
                    i += 2;
                    col += 2;
                elif i + 1 < n and source[i + 1] == '=':
                    tokens.append(("op_relacional", "LE"));
                    i += 2;
                    col += 2;
                else:
                    tokens.append(("op_relacional", "LT"));
                    i += 1;
                    col += 1;
            case '>':
                if i + 1 < n and source[i + 1] == '=':
                    tokens.append(("op_relacional", "GE"));
                    i += 2;
                    col += 2;
                else:
                    tokens.append(("op_relacional", "GT"));
                    i += 1;
                    col += 1;
            case '=':
                tokens.append(("op_relacional", "EQ"));
                i += 1;
                col += 1;
            case '+':
                tokens.append(("op_aritmetico", "SUMA"));
                i += 1;
                col += 1;
            case '-':
                tokens.append(("op_aritmetico", "RESTA"));
                i += 1;
                col += 1;
            case '*':
                tokens.append(("op_aritmetico", "MUL"));
                i += 1;
                col += 1;
            case '/':
                tokens.append(("op_aritmetico", "DIV"));
                i += 1;
                col += 1;
            case ';':
                tokens.append(("punto_coma", "PUNTO_COMA"));
                i += 1;
                col += 1;
            case ',':
                tokens.append(("coma", "COMA"));
                i += 1;
                col += 1;
            case '.':
                tokens.append(("punto", "PUNTO"));
                i += 1;
                col += 1;
            case '(':
                tokens.append(("paren_iz", "PAREN_IZ"));
                i += 1;
                col += 1;
            case ')':
                tokens.append(("paren_der", "PAREN_DER"));
                i += 1;
                col += 1;
            case '{':
                end = i + 1;
                while end < n and source[end] != '}':
                    end += 1;
                    col += 1;
                if end < n:
                    i = end + 1;
                else:
                    errores.append(f"Error léxico en línea {line_number}, comentario sin cerrar");
                    i = n
            # analizar palabras (identificadores y palabras reservadas) o números
            case _:
                if c.isalpha():
                    start = i
                    while i < n and (source[i].isalnum() or source[i] == '_'):
                        i += 1
                        col += 1

                    word = source[start:i]
                    if word.lower() in keyword_table:
                        tokens.append((word.upper(), word))
                    else:
                        tokens.append(("id", word))
                elif c.isdigit():
                    start = i
                    while i < n and source[i].isdigit():
                        i += 1
                        col += 1
                    tokens.append(("num", source[start:i]))
                else:
                    i += 1;
                    errores.append(f"Error léxico en línea {line_number}, col {col}, caracter no válido: {c}")
                    col += 1;
    return tokens, errores

def read_source(fileName):
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            source = file.read();
        
        tokens, errores = analyzer(source);

        try:
            with open("output.txt", 'w', encoding='utf-8') as output:
                for token in tokens:
                    output.write(f"{token[0]}, {token[1] if token[1] is not None else ''}\n");
                for error in errores:
                    output.write(f"{error}\n");
            print("Análisis léxico completado. Resultados guardados en 'output.txt'.");
            
        except IOError:
            print("Error: No se pudo escribir en el archivo 'output.txt'.");

    except FileNotFoundError:
        print(f"Error: El archivo '{fileName}' no existe.");
