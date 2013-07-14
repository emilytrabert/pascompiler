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
            asm += """
"""
            #print asm
            pointer = moveToNext(pointer)

        if getSymbol(pointer, postlexarray) == ",":
            pointer = moveToNext(pointer)
        elif getSymbol(pointer, postlexarray) == ":":
            pointer = moveToNext(pointer)
            if not (getReservedWord(pointer, postlexarray) == "INTEGER" or getReservedWord(pointer, postlexarray) == "BOOLEAN"):
                #print getReservedWord(pointer, postlexarray)
                error = True
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

def syntax(postlex):
    postlexarray = postlex.split()
    #print postlexarray
    pointer = 0
    if getReservedWord(pointer, postlexarray) == "":
        if getSymbol(pointer, postlexarray) == "":
            if getNumber(pointer, postlexarray) == -1:
                if getIdentifier(pointer, postlexarray) == -1:
                    syntaxError()
                else:
                    print getIdentifier(pointer, postlexarray)
            else:
                print getNumber(pointer, postlexarray)
        else:
            print getSymbol(pointer, postlexarray)
    else:
        print getReservedWord(pointer, postlexarray)
    pointer += 1
    return 0

def bettersyntax(postlex):
    postlexarray = postlex.split()
    asm = ""
    #print postlexarray
    pointer = 0
    # if first token not program,error
    if getReservedWord(pointer, postlexarray) != "PROGRAM":
        syntaxError("PROGRAM", getReservedWord(pointer, postlexarray))
        return

    pointer = moveToNext(pointer)
    
    # second idenifier, third ;
    if getIdentifier(pointer, postlexarray) == -1:
        syntaxError("indentifier", getIndentifier(pointer, postlexarray))
        return

    pointer = moveToNext(pointer)

    if getSymbol(pointer, postlexarray) != ';':
        syntaxError(";", getSymbol(pointer, postlexarray))
        return

    pointer = moveToNext(pointer)

    asm += """.cseg
.org 0
"""

    # fourth var or begin
    if getReservedWord(pointer, postlexarray) == "VAR":
        pointer = moveToNext(pointer)
        pointer, asm, error = assignVariables(pointer, postlexarray, asm)
        if error:
            return

    if getReservedWord(pointer, postlexarray) == "BEGIN":
        asm += "start: "
        pointer = moveToNext(pointer)

    else:
        syntaxError("BEGIN or VAR", getReservedWord(pointer, postlexarray))
        return

    # finally, end
    if getReservedWord(pointer, postlexarray) != "END.":
        syntaxError("END.", getReservedWord(pointer, postlexarray))
        return

    return asm

def main():
    pasfile = raw_input("File? ")
    postlex = lex(pasfile)
    print "Postlex:", postlex
    print "Symboltable:", symboltable
    print ""
    #syntax(postlex)
    print "ASM:"
    print bettersyntax(postlex)

main()
