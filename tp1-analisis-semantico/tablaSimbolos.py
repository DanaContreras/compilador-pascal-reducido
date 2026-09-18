class Lexema:
    def __init__(self,nombre,categoria,tipo,numLinea,parametros,tipoRetorno):
        self.nombre = nombre
        self.categoria = categoria
        self.tipo = tipo
        self.numLinea = numLinea
        self.parametros = parametros
        self.tipoRetorno = tipoRetorno

    def __str__(self):
        return f"{self.nombre}\t{self.categoria}\t{self.tipo}\t{self.numLinea}\t{self.parametros}\t\t{self.tipoRetorno}"


class TablaSimbolos:
    ENCABEZADOS = ["Nombre", "Categoría", "Tipo", "Línea", "Parámetros", "Retorno"]


    def __init__(self):
        self.tabla = {}

    def insertar(self, lexema):
        if lexema.nombre in self.tabla:
            raise ValueError(f"El lexema '{lexema.nombre}' ya existe en la tabla de símbolos.")
        self.tabla[lexema.nombre] = lexema

    def eliminar(self, nombre):
        if nombre not in self.tabla:
            raise ValueError(f"El lexema '{nombre}' no existe en la tabla de símbolos.")
        del self.tabla[nombre]

    def buscar(self, nombre):
        return self.tabla.get(nombre, None)

    def __str__(self):
        return "NOMBRE\tCATEGORÍA\tTIPO\tLÍNEA\tPARÁMETROS\tRETORNO\n" + "\n".join([str(lexema) for lexema in self.tabla.values()])


class Scope:
    def __init__(self, nivel, nombre, padre):
        self.nivel = nivel
        self.nombre = nombre
        self.padre = padre
        self.tabla = TablaSimbolos()

    def push(self, scope):
        self.pila.append(scope)

    def pop(self):
        return self.pila.pop()

    def actual(self):
        return self.pila[-1]

    def insertar(self, simbolo):
        self.tabla.insertar(simbolo)

    def buscar(self, nombre):
        simbolo = self.tabla.buscar(nombre)
        if simbolo is not None:
            return simbolo

        if self.padre is not None:
            return self.padre.buscar(nombre)

        return None

    def __str__(self):
        return (
            f"\n -----------------------------------------------------------------\n"
            f"Scope: {self.nombre}, Nivel: {self.nivel}, Padre: {self.padre.nombre if self.padre else None}\n"
            + str(self.tabla)
        )


class Pila:
    def __init__(self):
        self.pila = [Scope(0, "global", None)]  # Inicializa con un scope global

    def push(self, scope):
        self.pila.append(scope)

    def pop(self):
        if not self.is_empty():
            return self.pila.pop()
        else:
            raise IndexError("La pila está vacía")

    def top(self):
        if not self.is_empty():
            return self.pila[-1]
        else:
            raise IndexError("La pila está vacía")

    def insertar(self, simbolo):
        # Se inserta en la TS actual
        self.top().insertar(simbolo)

    def buscar(self, nombre):
        return self.top().buscar(nombre)

    def is_empty(self):
        return len(self.pila) == 0

    def __str__(self):
        return "\n".join([str(scope) for scope in self.pila])