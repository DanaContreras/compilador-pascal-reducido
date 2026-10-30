program ejemplo;

var k: integer;

procedure p(n: integer; g: integer);
  var h: integer;
  begin
    if n<2 then begin h:=g+n; end
    else begin
      h:=g;
      p(n-1, h);
      k:=h;
      p(n-2, g);
      end;
    write(n);
    write(g);
  end;


begin
  k:=0; p(3,k)
end.
