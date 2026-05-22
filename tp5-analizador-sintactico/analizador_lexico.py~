
keyword_table = ["program", "var", "function", "procedure", "integer", "begin", "boolean", "end", "if", "then", "else", "while", "do", "read", "write", "and", "or", "not"]

i = 0
line_number = 1
col = 1

def analyzer(source):
    global i, line_number, col
    n = len(source)
    error = None
    token = None

    while i < n and token is None and error is None:
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

        token_line = line_number
        token_col = col

        # analizar símbolos de un solo caracter o compuestos
        match c:
            case ':':
                if i + 1 < n and source[i + 1] == '=':
                    token = ("ASIGNAR", ":=", token_line, token_col)
                    i += 2;
                    col += 2;
                else:
                    token = ("dos_puntos", "DOS_PUNTOS", token_line, token_col)
                    i += 1;
                    col += 1;
            case '<':
                if i + 1 < n and source[i + 1] == '>':
                    token = ("op_relacional", "NE", token_line, token_col)
                    i += 2;
                    col += 2;
                elif i + 1 < n and source[i + 1] == '=':
                    token = ("op_relacional", "LE", token_line, token_col);
                    i += 2;
                    col += 2;
                else:
                    token = ("op_relacional", "LT", token_line, token_col);
                    i += 1;
                    col += 1;
            case '>':
                if i + 1 < n and source[i + 1] == '=':
                    token = ("op_relacional", "GE", token_line, token_col);
                    i += 2;
                    col += 2;
                else:
                    token = ("op_relacional", "GT", token_line, token_col);
                    i += 1;
                    col += 1;
            case '=':
                token = ("op_relacional", "EQ", token_line, token_col);
                i += 1;
                col += 1;
            case '+':
                token = ("op_aritmetico", "SUMA", token_line, token_col);
                i += 1;
                col += 1;
            case '-':
                token = ("op_aritmetico", "RESTA", token_line, token_col);
                i += 1;
                col += 1;
            case '*':
                token = ("op_aritmetico", "MUL", token_line, token_col);
                i += 1;
                col += 1;
            case '/':
                token = ("op_aritmetico", "DIV", token_line, token_col);
                i += 1;
                col += 1;
            case ';':
                token = ("punto_coma", "PUNTO_COMA", token_line, token_col);
                i += 1;
                col += 1;
            case ',':
                token = ("coma", "COMA", token_line, token_col);
                i += 1;
                col += 1;
            case '.':
                token = ("punto", "PUNTO", token_line, token_col);
                i += 1;
                col += 1;
            case '(':
                token = ("paren_iz", "PAREN_IZ", token_line, token_col);
                i += 1;
                col += 1;
            case ')':
                token = ("paren_der", "PAREN_DER", token_line, token_col);
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
                    error = f"Error léxico: Comentario sin cerrar en línea {line_number}";
                    i = n
            # analizar palabras (identificadores y palabras reservadas) o números
            case _:
                if c.isalpha():
                    start = i
                    while i < n and (source[i].isalnum() or source[i] == '_'):
                        i += 1
                        col += 1

                    word = source[start:i]
                    word_lower = word.lower()
                    if word.lower() in keyword_table:
                        token = (word_lower.upper(), word_lower, token_line, token_col)
                    else:
                        token = ("id", word, token_line, token_col)
                elif c.isdigit():
                    start = i
                    while i < n and source[i].isdigit():
                        i += 1
                        col += 1
                    token = ("num", source[start:i], token_line, token_col)
                else:
                    i += 1;
                    error = f"Error léxico: Caracter no valido en línea {line_number}, col {col}.";
                    break;
    return token, error

def get_siguiente_terminal(archivo):
    return analyzer(archivo)


