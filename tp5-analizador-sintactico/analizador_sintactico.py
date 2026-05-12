
source = "";
preanalisis = "";

def match(terminal):
    if (preanalisis == terminal)
        preanalisis = get_next_terminal();
    else:
        print("Error de sintaxis: Se esperaba '",terminal,"', se encontro '",preanalisis,"'."));

def get_next_terminal():

    result = None;
    if source:
        line = source.readline();
        
        if line:
            line = line.strip();
            parts = line.split(',');
            
            if len(partes) == 2:
                type_token = parts[0].strip();
                value_token = parts[1].strip();
                result = (type_token, value_token);
                
            else:
                print(f"Error: La línea '{line}' no tiene el formato esperado (token, valor).")
                return None
    
    return result;


def read_source(fileName):
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            source = file.read();
        
        get_next_terminal();
        program();

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
