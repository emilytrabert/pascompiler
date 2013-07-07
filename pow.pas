PROGRAM POW;
VAR
	A,B: INTEGER;
	I,J,M,N: INTEGER;
BEGIN
	READLN(A);
	READLN(B);
	IF B<0 THEN
	BEGIN
		WRITELN(0);
	END;
	ELSE
	BEGIN
		M:=1;
		J:=0;
		WHILE J<B DO
		BEGIN
			N:=0;
			FOR I:=1 TO A+1 DO
			BEGIN
				N:=N+M;
			END;
			M:=N;
			J:=J+1;
		END;	
		WRITELN(M);
	END;
END.
