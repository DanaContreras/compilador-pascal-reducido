program test;

var x: integer;

function doble(x : integer; y : boolean):integer;
begin
  if y then
    doble := x*2                   
end;
 
begin
  x := doble(5,true);
end.