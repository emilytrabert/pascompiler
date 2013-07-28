# Mini Pascal Compiler
# Emily Trabert

import re

reservedwords = {'PROGRAM': '@A',
                 'BEGIN': '@B',
                 'END;': '@C',
                 'END.': '@D',
                 'VAR': '@E',
                 'BOOLEAN': '@F',
                 'INTEGER': '@G',
                 'PROCEDURE': '@H',
                 'IF': '@I',
                 'THEN': '@J',
                 'ELSE': '@K',
                 'FOR': '@L',
                 'TO': '@M',
                 'DO': '@N',
                 'WHILE': '@O',
                 'TRUE': '@P',
                 'FALSE': '@Q',
                 'WRITELN': '@R',
                 'READLN': '@S'}

symbols = ['+', '-', '=', '<', '>', '(', ')', ',', ':', ';']

compsymbols = {'<>': '!', ':=': '|'}

symboltable = {}

def openfile(pasfile):
    psfl = open(pasfile, 'r')
    linelist = supersplit(psfl.read().split())
    psfl.close()

    return linelist

def supersplit(words):
    for symbol in symbols:
        newwords = []
        regsym = '(\\'+symbol+')'
        for word in words:
            newwords.extend(re.split(regsym, word))
        words = newwords
    return filter(None, words)

def lex(pasfile):
    sourcecode = openfile(pasfile)
    postlex = ""
    symcount = 0
    combo = False

    for i in range(len(sourcecode)):
        token = sourcecode[i]
        if not combo:
            if token in symbols:
                if sourcecode[i+1] in symbols:
                    combosym = token + sourcecode[i+1]
                    if combosym in compsymbols:
                        postlex += compsymbols[combosym]
                        combo = True
                    else:
                        postlex += token
                else:
                    postlex += token
            elif token.upper() in reservedwords:
                postlex += reservedwords[token.upper()]
            elif (token.upper() + sourcecode[i+1]) in reservedwords:
                postlex += reservedwords[(token.upper() + sourcecode[i+1])]
                combo = True
            elif re.match('\w', token):
                try:
                    postlex += str(int(token))
                except ValueError:
                    if token not in symboltable:
                        symboltable[token] = '$'+str(symcount)
                        symcount += 1
                    postlex += symboltable[token]
            else:
                postlex = "Lex error at token "+str(i)
                break
            postlex += " "
        else:
            combo = False

    return postlex

def moveToNext(p):
    return p + 1

def getReservedWord(pointer, postlexarray):
    for key in reservedwords:
        if reservedwords[key] == postlexarray[pointer]:
            return key
    return ""

def getSymbol(pointer, postlexarray):
    for sym in symbols:
        if sym == postlexarray[pointer]:
            return sym
    for key in compsymbols:
        if compsymbols[key] == postlexarray[pointer]:
            return key
    return ""

def getNumber(pointer, postlexarray):
    try:
        return int(postlexarray[pointer])
    except ValueError:
        return -1

def getIdentifier(pointer, postlexarray):
    for key in symboltable:
        if symboltable[key] == postlexarray[pointer]:
            return key
    return -1

def syntaxError(expected, got):
    print "Expected:", expected
    print "Encountered:", got

def assignVariables(pointer, postlexarray, asm):
    error = False
    registerCount = 17
    moreVars = True
    
    while moreVars:
        if getIdentifier(pointer, postlexarray) == -1:
            error = True
            return pointer, asm, error
        else:
            asm += ".def "
            asm += getIdentifier(pointer, postlexarray)
            asm += " = R"
            asm += str(registerCount)
            registerCount += 1
            asm += "\n"
            pointer = moveToNext(pointer)

        if getSymbol(pointer, postlexarray) == ",":
            pointer = moveToNext(pointer)
        elif getSymbol(pointer, postlexarray) == ":":
            pointer = moveToNext(pointer)
            if not (getReservedWord(pointer, postlexarray) == "INTEGER" or getReservedWord(pointer, postlexarray) == "BOOLEAN"):
                error = True
                syntaxError("INTEGER or BOOLEAN", syntax(postlexarray[pointer]))
                return pointer, asm, error
            
            pointer = moveToNext(pointer)
            pointer = moveToNext(pointer)

            if getReservedWord(pointer, postlexarray) == "BEGIN":
                return pointer, asm, error
            elif getIdentifier(pointer, postlexarray) == "":
                error = True
                syntaxError("BEGIN or Identifier", syntax(postlexarray[pointer]))
                return pointer, asm, error
        else:
            error = True
            return pointer, asm, error

def parseAssignment(pointer, postlexarray, asm):
    error = False
    
    # get variable for assigning
    var = getIdentifier(pointer, postlexarray)
    pointer = moveToNext(pointer)

    # make sure it's getting assigned
    if getSymbol(pointer, postlexarray) != ":=":
        syntaxError(":=", syntax(postlexarray[pointer]))
        error = True
        return pointer, asm, error
    pointer = moveToNext(pointer)

    # see if a number
    try:
        val = str(int(postlexarray[pointer]))
        asm += "LDI temp, "
        asm += val
        asm += "\n"
    except ValueError:
    # or a variable
        if getIdentifier(pointer, postlexarray) == -1:
            error = True
            syntaxError("Identifier or integer", syntax(postlexarray[pointer]))
            return pointer, asm, error
        val = getIdentifier(pointer, postlexarray)
        asm += "MOV temp, "
        asm += val
        asm += "\n"
    pointer = moveToNext(pointer)
    
    more = True
    
    while more:
        # get the next symbol
        if getSymbol(pointer, postlexarray) == ";":
            asm += "MOV "
            asm += var
            asm += ", temp\n"
            pointer = moveToNext(pointer)
            return pointer, asm, error
        elif getSymbol(pointer, postlexarray) == "+":
            asm += "ADD temp, "
            #print asm
            pointer = moveToNext(pointer)
        elif getSymbol(pointer, postlexarray) == "-":
            asm += "SUB temp, "
            pointer = moveToNext(pointer)
        else:
            error = True
            syntaxError("+, - or ;", syntax(postlexarray[pointer]))
            return pointer, asm, error
        
        # see if a number
        try:
            val = str(int(postlexarray[pointer]))
            asm += val
            asm += "\n"
        except ValueError:
        # or a variable
            if getIdentifier(pointer, postlexarray) == -1:
                error = True
                syntaxError("Identifier or integer", syntax(postlexarray[pointer]))
                return pointer, asm, error
            val = getIdentifier(pointer, postlexarray)
            asm += val
            asm += "\n"
        pointer = moveToNext(pointer)

def syntax(postlex):
    postlexarray = postlex.split()
    pointer = 0
    if getReservedWord(pointer, postlexarray) != "":
        return getReservedWord(pointer, postlexarray)
    
    if getSymbol(pointer, postlexarray) != "":
        return getSymbol(pointer, postlexarray)
    
    if getNumber(pointer, postlexarray) != -1:
        return getNumber(pointer, postlexarray)

    if getIdentifier(pointer, postlexarray) != -1:
        return getIdentifier(pointer, postlexarray)

    return "Not found"


def bettersyntax(postlex):
    postlexarray = postlex.split()
    asm = ""
    pointer = 0
    
    # if first token not program,error
    if getReservedWord(pointer, postlexarray) != "PROGRAM":
        syntaxError("PROGRAM", syntax(postlexarray[pointer]))
        return ""

    pointer = moveToNext(pointer)
    
    # second idenifier, third ;
    if getIdentifier(pointer, postlexarray) == -1:
        syntaxError("indentifier", syntax(postlexarray[pointer]))
        return ""

    pointer = moveToNext(pointer)

    if getSymbol(pointer, postlexarray) != ';':
        syntaxError(";", syntax(postlexarray[pointer]))
        return ""

    pointer = moveToNext(pointer)

    asm += ".cseg\n.org 0\n\n.def temp = R16\n"

    # check for variables
    if getReservedWord(pointer, postlexarray) == "VAR":
        pointer = moveToNext(pointer)
        pointer, asm, error = assignVariables(pointer, postlexarray, asm)
        if error:
            return ""

    asm += "\nconfig:\nLDI temp, 0b11111111\nOUT DDRD, temp\n"

    if getReservedWord(pointer, postlexarray) == "BEGIN":
        asm += "\nstart:\n"
        pointer = moveToNext(pointer)
    else:
        syntaxError("BEGIN or VAR", syntax(postlexarray[pointer]))
        return ""

    # while not at the end of postlex
    while pointer < len(postlexarray)-1:
        # assign variables
        if getIdentifier(pointer, postlexarray) != -1:
            pointer, asm, error = parseAssignment(pointer, postlexarray, asm)
            if error:
                return ""
        elif getReservedWord(pointer, postlexarray) == "WRITELN":
            pointer = moveToNext(pointer)
            if getSymbol(pointer, postlexarray) == "(":
                pointer = moveToNext(pointer)

                try:
                    val = str(int(postlexarray[pointer]))
                except ValueError:
                    if getIdentifier(pointer, postlexarray) == -1:
                        error = True
                        syntaxError("Identifier or integer", syntax(postlexarray[pointer]))
                        return pointer, asm, error
                    val = getIdentifier(pointer, postlexarray)
                    
                pointer = moveToNext(pointer)
                if getSymbol(pointer, postlexarray) == ")":
                    pointer = moveToNext(pointer)
                    if getSymbol(pointer, postlexarray) == ";":
                        pointer = moveToNext(pointer)
                        asm += "OUT PORTD, "
                        asm += val
                        asm += "\n"
                    else:
                        syntaxError(";", syntax(postlexarray[pointer]))
                        return ""
                else:
                    syntaxError(")", syntax(postlexarray[pointer]))
                    return ""
            else:
                syntaxError("(", syntax(postlexarray[pointer]))
                return ""
        else:
            syntaxError("Identifier or WRITELN", syntax(postlexarray[pointer]))
            return ""

    # finally, end
    if getReservedWord(pointer, postlexarray) != "END.":
        syntaxError("END.", syntax(postlexarray[pointer]))
        return ""

    return asm

def main():
    while True:
        pasfile = raw_input("File? ")
        postlex = lex(pasfile)
        print "Postlex:", postlex
        print "Symboltable:", symboltable
        print "\nASM:"
        print bettersyntax(postlex)

main()
