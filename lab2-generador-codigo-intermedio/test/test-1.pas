program PruebaErrores;
var
  a, b : integer;
  flag : boolean;
  a : boolean;                   {a redeclarada en el mismo ámbito (sigue siendo integer) }

procedure proc(x : integer; y : boolean);
var
  local : integer;
begin
  local := x;
  y := x                         { se asigna integer a boolean }
end;

function suma(x, x : integer) : integer;    { parámetro 'x' duplicado }
begin
  suma := x + 1
end;

function esPar(n : integer) : boolean;
begin
  esPar := n / 2              { la función retorna boolean, se asigna integer }
end;

begin
  c := 1;                        { c no declarada }
  b := c + 2;                    
  a := true;                     { boolean asignado a integer }
  b := flag + 1;                 { operador aritmético con operando boolean }
  flag := a and b;               { operador lógico con operandos integer }
  flag := a = flag;              { comparación integer vs boolean }
  if a then                      { condición del if no es boolean }
    write(a);
  while b + 1 do                 { condición del while no es boolean }
    b := b - 1;
  proc(a);                       { cantidad de parámetros incorrecta }
  proc(flag, a);                 { tipos de parámetros incorrectos (ambos) }
  b := proc(1, true);            { procedimiento usado como función }
  a(3);                          { a no es un subprograma }
  local := 5;                    { localno es visible fuera de proc }
  suma := 4;                     { asignación al nombre de función fuera de su cuerpo }
  b := esPar(a) + suma(1, 2)     { esPar retorna boolean dentro de una suma }
end.