# Reglas de tipos de los operadores del pscal reducido

from tablaSimbolos import INTEGER, BOOLEAN

# operador binario (tipo que deben tener los operandos, tipo del resultado)

REGLAS_BINARIAS = {
    "+": (INTEGER, INTEGER),
    "-": (INTEGER, INTEGER),
    "*": (INTEGER, INTEGER),
    "/": (INTEGER, INTEGER),
    "and": (BOOLEAN, BOOLEAN),
    "or": (BOOLEAN, BOOLEAN),
    "<": (INTEGER, BOOLEAN),
    ">": (INTEGER, BOOLEAN),
    "<=": (INTEGER, BOOLEAN),
    ">=": (INTEGER, BOOLEAN),
    "=": (None, BOOLEAN),
    "<>": (None, BOOLEAN),
}

# operador unario (tipo que debe tener el operando, tipo del resultado)
REGLAS_UNARIAS = {
    "not": (BOOLEAN, BOOLEAN),
    "+": (INTEGER, INTEGER),
    "-": (INTEGER, INTEGER),
}

def mensaje_tipo(esperado, obtenido, contexto):
    # None es un tipo desconocido por un error ya informado
    if esperado is None or obtenido is None or esperado == obtenido:
        return None
    return f"{contexto} debe ser {esperado} y es {obtenido}."

def tipo_binario(op, izq, der):
    """Devuelve (tipo del resultado, [mensajes de error])."""
    tipo_operandos, tipo_resultado = REGLAS_BINARIAS[op]
    if tipo_operandos is None:
        if izq is not None and der is not None and izq != der:
            return tipo_resultado, [f"No se puede comparar {izq} con {der} usando '{op}'."]
        return tipo_resultado, []
    errores = [
        mensaje_tipo(tipo_operandos, izq, f"El operando izquierdo de '{op}'"),
        mensaje_tipo(tipo_operandos, der, f"El operando derecho de '{op}'"),
    ]
    return tipo_resultado, [e for e in errores if e is not None]

def tipo_unario(op, operando):
    """Devuelve (tipo del resultado, [mensajes de error])."""
    tipo_operando, tipo_resultado = REGLAS_UNARIAS[op]
    error = mensaje_tipo(tipo_operando, operando, f"El operando de '{op}'")
    return tipo_resultado, [error] if error else []
