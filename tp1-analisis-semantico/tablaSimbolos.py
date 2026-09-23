# Tabla de símbolos para el compilador de Pascal reducido.

class ErrorTablaSimbolos(Exception):
    """Nombre declarado dos veces en un mismo ámbito, o eliminado sin existir.

    El analizador semántico la captura, informa el error y continúa."""


# categorías posibles de un lexema
PROGRAMA = "programa"
VARIABLE = "variable"
PARAMETRO = "parametro"
PROCEDIMIENTO = "procedimiento"
FUNCION = "funcion"

# tipos del subconjunto del lenguaje
INTEGER = "integer"
BOOLEAN = "boolean"

class Lexema:
    def __init__(self, nombre, categoria, tipo=None, num_linea=None,
                 parametros=None, ambito=None):
        self.nombre = nombre
        self.clave = nombre.lower()
        self.categoria = categoria   # PROGRAMA | VARIABLE | PARAMETRO | PROCEDIMIENTO | FUNCION
        self.tipo = tipo             # INTEGER | BOOLEAN en una función es su tipo de retorno
        self.num_linea = num_linea 
        self.parametros = list(parametros) if parametros else []  # [(nombre, tipo), ...] en orden
        self.ambito = ambito         # Scope propio solo en subprogramas

    def es_subprograma(self):
        return self.categoria in (PROCEDIMIENTO, FUNCION)

    def cantidad_parametros(self):
        return len(self.parametros)

    def agregar_parametro(self, nombre, tipo):
        self.parametros.append((nombre, tipo))

    def tipos_parametros(self):
        return [tipo for _, tipo in self.parametros]

    def parametros_str(self):
        if not self.es_subprograma():
            return "-"
        return "(" + ", ".join(f"{n}: {t}" for n, t in self.parametros) + ")"

    def __str__(self):
        return TablaSimbolos.fila([
            self.nombre,
            self.categoria,
            self.tipo if self.tipo is not None else "-",
            self.num_linea if self.num_linea is not None else "-",
            self.parametros_str(),
        ])


class TablaSimbolos:
    ENCABEZADOS = ("NOMBRE", "CATEGORÍA", "TIPO", "LÍNEA", "PARÁMETROS")
    ANCHOS = (18, 15, 9, 7)

    @classmethod
    def fila(cls, valores):
        celdas = [f"{str(v):<{a}}" for v, a in zip(valores, cls.ANCHOS)]
        celdas.append(str(valores[-1]))
        return "".join(celdas)

    def __init__(self):
        self.tabla = {}

    def insertar(self, lexema):
        previo = self.tabla.get(lexema.clave)
        if previo is not None:
            raise ErrorTablaSimbolos(
                f"El nombre '{lexema.nombre}' ya fue declarado en este ámbito "
                f"(línea {previo.num_linea})."
            )
        self.tabla[lexema.clave] = lexema
        return lexema

    def eliminar(self, nombre):
        clave = nombre.lower()
        if clave not in self.tabla:
            raise ErrorTablaSimbolos(
                f"El nombre '{nombre}' no existe en la tabla de símbolos."
            )
        return self.tabla.pop(clave)

    def buscar(self, nombre):
        return self.tabla.get(nombre.lower())

    def simbolos(self):
        return list(self.tabla.values())

    def __str__(self):
        lineas = [self.fila(self.ENCABEZADOS)]
        if not self.tabla:
            lineas.append("(vacía)")
        else:
            lineas.extend(str(lexema) for lexema in self.tabla.values())
        return "\n".join(lineas)


class Scope:
    def __init__(self, nivel, nombre, padre):
        self.nivel = nivel
        self.nombre = nombre
        self.padre = padre
        self.tabla = TablaSimbolos()

    def insertar(self, simbolo):
        return self.tabla.insertar(simbolo)

    def buscar(self, nombre):
        simbolo = self.tabla.buscar(nombre)
        if simbolo is not None:
            return simbolo

        if self.padre is not None:
            return self.padre.buscar(nombre)

        return None

    def __str__(self):
        return (
            "\n -----------------------------------------------------------------\n"
            f"Ámbito: {self.nombre}, Nivel: {self.nivel}, "
            f"Padre: {self.padre.nombre if self.padre else None}\n"
            + str(self.tabla)
        )


class Pila:
    def __init__(self):
        self.pila = []
        self.registro = []
        self.push(Scope(0, "global", None))

    def abrir_ambito(self, nombre):
        # crea el ámbito hijo del actual, lo apila y lo devuelve
        scope = Scope(self.top().nivel + 1, nombre, self.top())
        self.push(scope)
        return scope

    def cerrar_ambito(self):
        # se llama al terminar el cuerpo de un subprograma
        if len(self.pila) <= 1:
            raise ErrorTablaSimbolos("No se puede cerrar el ámbito global.")
        scope = self.pila.pop()
        self.registro.append(
            f"DESAPILA ámbito '{scope.nombre}' (nivel {scope.nivel})\n{scope.tabla}"
        )
        return scope

    def push(self, scope):
        self.pila.append(scope)
        padre = scope.padre.nombre if scope.padre else "-"
        self.registro.append(
            f"APILA ámbito '{scope.nombre}' (nivel {scope.nivel}, padre {padre})"
        )

    def pop(self):
        return self.cerrar_ambito()

    def top(self):
        if self.is_empty():
            raise IndexError("La pila está vacía")
        return self.pila[-1]

    def insertar(self, simbolo):
        return self.top().insertar(simbolo)

    def buscar(self, nombre):
        return self.top().buscar(nombre)

    def is_empty(self):
        return len(self.pila) == 0

    def __str__(self):
        return "\n\n".join(self.registro)
