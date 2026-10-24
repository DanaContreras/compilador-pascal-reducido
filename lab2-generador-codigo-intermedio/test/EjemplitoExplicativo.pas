program EjemplitoExplicativo;          { 1 }
var
  x : integer;                         { 3 }
  ok : boolean;                        { 4 }

procedure p(a : integer);              { 6 }
var
  x : boolean;                         { 8 }  { oculta a la x global }
begin 
  x := a > 0                           { 10 }
end;                                   { 11 }

function f(n : integer) : integer;     { 13 }
begin
  f := n + 1                           { 15 }
end;                                   { 16 }

begin
  x := f(x);                           { 19 }
  ok := x > 0;                         { 20 }
  p(x)                                 { 21 }
end.
