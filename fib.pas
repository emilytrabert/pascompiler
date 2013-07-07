PROGRAM FIBONACCI;
VAR
	N,RESULT: INTEGER;
PROCEDURE FIB_ITR(N: INTEGER);
VAR
	I1,I2: INTEGER;
	I,TEMP: INTEGER;
BEGIN
	I1:=0;
	I2:=1;
	I:=2;
	WHILE I<N+1 DO
	BEGIN
		TEMP:=I1+I2;
		I1:=I2;
		I2:=TEMP;
		I:=I+1;
	END;
	RESULT:=I2;
END;
PROCEDURE FIB_REC(N: INTEGER);
VAR
	I1,I2: INTEGER;
BEGIN
	IF N=0 THEN
	BEGIN
		RESULT:=0;
	END;
	ELSE
	BEGIN
		IF N=1 THEN
		BEGIN
			RESULT:=1;
		END;
		ELSE
		BEGIN
			I1:=N-1;
			FIB_REC(I1);
			I1:=RESULT;
			I2:=N-2;
			FIB_REC(I2);
			RESULT:=RESULT+I1;
		END;
	END;
END;

BEGIN
	READLN(N);
	FIB_ITR(N);
	WRITELN(RESULT);
	FIB_REC(N);
	WRITELN(RESULT);
END.