# Generador de código intermedio MEPA para el compilador de Pascal reducido.

import os

OPERACIONES_BINARIAS = {
    "+": "SUMA",
    "-": "SUST",
    "*": "MULT",
    "/": "DIVI",
    "and": "CONJ",
    "or": "DISJ",
    "<": "CMME",
    ">": "CMMA",
    "=": "CMIG",
    "<>": "CMDG",
    "<=": "CMNI",
    ">=": "CMYI",
}

OPERACIONES_UNARIAS = {
    "-": "UMEN",
    "not": "NEGA",
    "+": None,
}

VALORES_BOOLEANOS = {"true": 1, "false": 0}

SEPARADOR_ARGUMENTOS = ","

class Instruccion:
    def __init__(self, operacion, argumentos=(), etiqueta=None):
        self.operacion = operacion
        self.argumentos = list(argumentos)
        self.etiqueta = etiqueta

    def __str__(self):
        argumentos = SEPARADOR_ARGUMENTOS.join(str(a) for a in self.argumentos)
        return f"{self.etiqueta or '':<6}{self.operacion:<6}{argumentos}".rstrip()


class GeneradorMEPA:
    def __init__(self):
        self.instrucciones = []
        self.cont_etiquetas = 0

    def nueva_etiqueta(self):
        self.cont_etiquetas += 1
        return f"L{self.cont_etiquetas}"

    def emitir(self, operacion, *argumentos, etiqueta=None):
        instruccion = Instruccion(operacion, argumentos, etiqueta)
        self.instrucciones.append(instruccion)

    # Expresiones ----------------

    def apilar_constante(self, valor):
        # valor: el lexema de un num o true/false
        if isinstance(valor, str) and valor.lower() in VALORES_BOOLEANOS:
            valor = VALORES_BOOLEANOS[valor.lower()]
        self.emitir("APCT", int(valor))

    def operacion_binaria(self, operador):
        print("Operacion binaria recibida: ",operador)
        self.emitir(OPERACIONES_BINARIAS[operador.lower()])

    def operacion_unaria(self, operador):
        instruccion = OPERACIONES_UNARIAS[operador.lower()]
        if instruccion is not None:
            self.emitir(instruccion)

    # Comandos condicionales e iterativos ---------

    def marcar(self, etiqueta):
        self.emitir("NADA", etiqueta=etiqueta)

    def desviar(self):
        etiqueta = self.nueva_etiqueta()
        self.emitir("DSVS", etiqueta)
        return etiqueta

    def desviar_sino(self, etiqueta_falso):
        etiqueta_fin = self.nueva_etiqueta()
        self.emitir("DSVS", etiqueta_fin)
        self.marcar(etiqueta_falso)
        return etiqueta_fin

    def condicion(self):
        etiqueta = self.nueva_etiqueta()
        self.emitir("DSVF", etiqueta)
        return etiqueta

    def inicio_while(self):
        etiqueta = self.nueva_etiqueta()
        self.marcar(etiqueta)
        return etiqueta

    def fin_while(self, etiqueta_inicio, etiqueta_fin):
        self.emitir("DSVS", etiqueta_inicio)
        self.marcar(etiqueta_fin)

    # Comandos de entrada/salida -------

    def leer(self, simbolo):
        self.emitir("LEER")
        self.asignar(simbolo)

    def imprimir(self):
        self.emitir("IMPR")
    
    # Comandos de asignación y recuperación de valores ------

    def apilar_variable(self, simbolo):
        direccion = simbolo.direccion() if simbolo else None
        if direccion is not None:
            self.emitir("APVL", *direccion)

    def asignar(self, simbolo):
        direccion = simbolo.direccion() if simbolo else None
        if direccion is not None:
            self.emitir("ALVL", *direccion)

    # Programas y procedmientos -------------

    def etiqueta_subprograma(self, simbolo):
        if simbolo.etiqueta is None:
            simbolo.etiqueta = self.nueva_etiqueta()
        return simbolo.etiqueta

    def iniciar_programa(self):
        self.emitir("INPP")

    def inicio_programa_principal(self):
        etiqueta = self.nueva_etiqueta()
        self.emitir("DSVS", etiqueta)
        return etiqueta

    def entrar_subprograma(self, simbolo):
        nivel = simbolo.ambito.nivel
        self.emitir("ENPR", nivel, etiqueta=self.etiqueta_subprograma(simbolo))

    def llamar(self, simbolo):
        if simbolo is not None and simbolo.es_subprograma():
            self.emitir("LLPR", self.etiqueta_subprograma(simbolo))

    def reservar_variables(self, scope):
        if scope.cantidad_variables > 0:
            self.emitir("RMEM", scope.cantidad_variables)

    def liberar_variables(self, scope):
        if scope.cantidad_variables > 0:
            self.emitir("LMEM", scope.cantidad_variables)

    def salir_subprograma(self, simbolo):
        scope = simbolo.ambito
        self.emitir("RTPR", scope.nivel, scope.cantidad_parametros())

    def fin_subprogramas(self, etiqueta):
        self.marcar(etiqueta)

    def finalizar_programa(self):
        self.emitir("PARA")

    # Funciones ----------------

    def reservar_resultado(self):
        self.emitir("RMEM", 1)

    # Para guardar codigo intermedio

    def codigo(self):
        return "\n".join(str(i) for i in self.instrucciones) + "\n"

    def guardar_generacion(self, ruta):
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.codigo())

    def __str__(self):
        return self.codigo()