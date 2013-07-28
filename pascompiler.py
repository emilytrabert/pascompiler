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
    #print(sourcecode)
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
    registerCount = 16
    moreVars = True
    asm += ".def temp = R15\n"
    
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
            #print asm
            pointer = moveToNext(pointer)

        if getSymbol(pointer, postlexarray) == ",":
            pointer = moveToNext(pointer)
        elif getSymbol(pointer, postlexarray) == ":":
            pointer = moveToNext(pointer)
            if not (getReservedWord(pointer, postlexarray) == "INTEGER" or getReservedWord(pointer, postlexarray) == "BOOLEAN"):
                #print getReservedWord(pointer, postlexarray)
                error = True
                syntaxError("INTEGER or BOOLEAN", syntax(postlexarray[pointer]))
                return pointer, asm, error
            pointer = moveToNext(pointer)
            pointer = moveToNext(pointer)
            #print "r", getReservedWord(pointer, postlexarray), pointer

            if getReservedWord(pointer, postlexarray) == "BEGIN":
                #print getReservedWord(pointer, postlexarray)
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
    
    # get variable
    var = getIdentifier(pointer, postlexarray)
    pointer = moveToNext(pointer)
    print "MAIN VAR", var

    # make sure it's getting assigned
    if getSymbol(pointer, postlexarray) != ":=":
        syntaxError(":=", syntax(postlexarray[pointer]))
        error = True
        return pointer, asm, error
    pointer = moveToNext(pointer)

    # see if a number
    try:
        val = str(int(postlexarray[pointer]))
    except ValueError:
    # or a variable
        if getIdentifier(pointer, postlexarray) == -1:
            error = True
            syntaxError("Identifier or integer", syntax(postlexarray[pointer]))
            return pointer, asm, error
        val = getIdentifier(pointer, postlexarray)
    pointer += 1

    asm += "LDI "
    asm += "temp"
    asm += ", "
    asm += val
    asm += "\n"
    
    more = True
    
    while more:
        if getSymbol(pointer, postlexarray) == ";":
            asm += "LDI "
            asm += var
            asm += ", "
            asm += "temp"
            asm += "\n"
            print asm
            pointer += 1
            return pointer, asm, error
        elif getSymbol(pointer, postlexarray) == "+":
            asm += "ADD "
            asm += "temp"
            asm += ", "
            print asm
            pointer += 1
        elif getSymbol(pointer, postlexarray) == "-":
            asm += "SUB "
            asm += "temp"
            asm += ", "
            
            print asm
            pointer += 1
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
        pointer += 1
        print val

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
    #print postlexarray
    pointer = 0
    # if first token not program,error
    if getReservedWord(pointer, postlexarray) != "PROGRAM":
        syntaxError("PROGRAM", syntax(postlexarray[pointer]))
        return

    pointer = moveToNext(pointer)
    
    # second idenifier, third ;
    if getIdentifier(pointer, postlexarray) == -1:
        syntaxError("indentifier", syntax(postlexarray[pointer]))
        return

    pointer = moveToNext(pointer)

    if getSymbol(pointer, postlexarray) != ';':
        syntaxError(";", syntax(postlexarray[pointer]))
        return

    pointer = moveToNext(pointer)

    asm += ".cseg\n.org 0\n\n"

    # fourth var or begin
    if getReservedWord(pointer, postlexarray) == "VAR":
        pointer = moveToNext(pointer)
        pointer, asm, error = assignVariables(pointer, postlexarray, asm)
        if error:
            return

    if getReservedWord(pointer, postlexarray) == "BEGIN":
        asm += "\nstart:\n"
        pointer = moveToNext(pointer)
    else:
        syntaxError("BEGIN or VAR", syntax(postlexarray[pointer]))
        return

    print "thus far"

    # assign variables
    while getIdentifier(pointer, postlexarray) != -1:
        pointer, asm, error = parseAssignment(pointer, postlexarray, asm)
        print "loop"
        if error:
            return

    print "no errors"

    # finally, end
    if getReservedWord(pointer, postlexarray) != "END.":
        syntaxError("END.", syntax(postlexarray[pointer]))
        return

    return asm

def main():
    while True:
        pasfile = raw_input("File? ")
        postlex = lex(pasfile)
        print "Postlex:", postlex
        print "Symboltable:", symboltable
        print ""
        print "ASM:"
        print bettersyntax(postlex)

main()
