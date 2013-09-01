"""
drocta ~ATH parser (may or may not be used in the interpreter later)
version:0.1

TODO:remove some commented out code.
and maybe add support for colored text if you think of a good way.(unlikely)
other than that it seems fairly complete,
but improvements might still happen.

Better variable names maybe?
"""
import tokenizing

def preprocess(s):#this may or may not be added as a thing. Don't count on it.
    """does some preprocessing"""
    pass



"""
list of tokens:
".DIE();"
"~ATH("
"){"
"}EXECUTE{"
");"
"BIFURCATE"
"split"
"import"
"print"
"\""
"\\"
"//"
"/*"
"*/"
";"
" "
"\n"
"\\"


"""

tokenListI=[".DIE(",");","~ATH(","){","}EXECUTE(","\"","\\","//","/*","*/"," ","\n","[",",","]"]

def tokenize(s):
    """turns the preprocessed string into tokens"""
    tokens=tokenizing.tokenizeMultiToken([s],tokenListI)
    tokens=tokenizing.tokenizeSingleToken(tokens,";",");")
    #tokens=removeUnwantedTokens(tokens,['',' '])#should ' ' be removed? is this line neccesary at all?
    #probably add more things
    return tokens

def commentSkip(tokens):
    """skips comments and newlines from a list of tokens"""
    while(True):
        if(len(tokens)==0):
            break
        elif(tokens[0] in [""," ","\n"]):
            tokens.pop(0)
        elif(tokens[0] == "//"):
            while(tokens[0] != "\n"):
                tokens.pop(0)
            tokens.pop(0)#pops off the \n
        elif(tokens[0] == "/*"):
            while(tokens[0] != "*/"):
                tokens.pop(0)
            tokens.pop(0)#pops off the */
        else:
            break
    return None


#####################
"""
"~ATH(THING){STUFF}EXECUTE(STUFF);"
should become
("~ATH","THING",[STUFF1],[STUFF2])

"import a b ... d;"
should become
("import",[a,b,...,d])

"THING1.DIE(THING2);"
should become
("DIE","THING1","THING2")




"""
def read_from(tokens,currentDepth=0):
    """Read an expression from a sequence of tokens."""
    #print "currentDepth is ",currentDepth
    commentSkip(tokens)
    if(len(tokens)==0):
        raise SyntaxError('unexpected EOF while reading')
    commentSkip(tokens)
    token=tokens.pop(0)
    if(token=="~ATH("):
        T=["~ATH"]
        token=tokens.pop(0)
        if(not isalnum2(token)):
            raise SyntaxError('variable name"'+token+'"should be alphanumeric')
        T.append(token)
        token=tokens.pop(0)
        if(token != "){"):#possibly in the future allow )\n{ ???
            raise SyntaxError('expected "~ATH('+T[1]+'){", recieved "~ATH('+T[1]+token+'" instead.')        
        L=[]
        commentSkip(tokens)
        while(tokens[0] != "}EXECUTE("):
            #print "tokens0 is "
            #print tokens[0]
            #print "tokens is "
            #print tokens
##                if(tokens[0] =="\n"):
##                    tokens.pop(0)
##                    continue
##                elif(token == "//"):
##                    while(tokens[0] != "\n"):
##                        tokens.pop(0)
##                    tokens.pop(0)#pops off the \n
##                    continue
##                elif(token == "/*"):
##                    while(tokens[0] != "*/"):
##                        tokens.pop(0)
##                    tokens.pop(0)
##                    continue
            L.append(read_from(tokens,currentDepth+1))
            deathParser(L)
            commentSkip(tokens)
            deathParser(L)
        tokens.pop(0) # pop off "}EXECUTE("
        #print "finished first block of ~ATH command"
        #print T
        T.append(L)
        L=[]
        commentSkip(tokens)
        while(tokens[0] != ");"):
            #print "debug: token0 for ); is ",tokens[0]
            #print "debug: tokens for ); are "
            #print tokens
            L.append(read_from(tokens,currentDepth+1))
            deathParser(L)
            #print "debug: token0 for ); 2 is ",tokens[0]
            #print "debug: tokens for ); 2 are "
            #print tokens
            commentSkip(tokens)
        tokens.pop(0)
        commentSkip(tokens)
        T.append(L)
        return T
    elif(token=="import"):
        T=["import"]
        L=[]
        while(tokens[0] != ";"):
            #maybe raise a syntax error if the things in the import aren't alphanumeric.
            token=tokens.pop(0)
            if(token !=" "):
                L.append(token)#the L for the import should probably not have nesting, thats why this is token instead of read_from
        tokens.pop(0)
        T.append(L)
        return T
    elif(token=='"'):
        L=[]
        while(tokens[0] != '"'):
            token=tokens.pop(0)
            if(token=="\\"):
                token=tokens.pop(0)
            L.append(token)
        tokens.pop(0)
        #print "dubug:got to the string"
        return ["literal string",''.join(L)]
    elif(token=="print"):
        T=["print"]
        L=[]
        while(tokens[0] != ";"):
            L.append(read_from(tokens,currentDepth+1))
        tokens.pop(0)
        T.append(L)
        return T
    elif(token in ["BIFURCATE","split"]):
        T=["BIFURCATE"]
        T.append(read_from(tokens,currentDepth+1))
        T.append(read_from(tokens,currentDepth+1))
        for a in T[1:]:
            if(a[0] not in ["literal string","var","pair/tuple"]):#change name of pair/tuple
                raise SyntaxError('wrong thing passed to BIFURCATE/split')
        return T
##        elif(token == "//"):
##            while(tokens[0] != "\n"):
##                tokens.pop(0)
##            tokens.pop(0)#pops off the \n
##            continue
##        elif(token == "/*"):
##            while(tokens[0] != "*/"):
##                tokens.pop(0)
##            tokens.pop(0)
##            continue
    elif(token == "["):
        T=["pair/tuple"]
        L=[]
        commentSkip(tokens)
        while(tokens[0] !="]"):
            L.append(read_from(tokens,currentDepth+1))
            commentSkip(tokens)
            if(tokens[0] != ","):
                if(tokens[0] =="]"):
                    continue
                raise SyntaxError('expected "," instead found '+tokens[0])
            tokens.pop(0)
            commentSkip(tokens)
        T.append(L)
        return T
    elif(token == ".DIE("):
        L=[]
        commentSkip(tokens)
        while(tokens[0] != ");"):
            L.append(read_from(tokens,currentDepth+1))
            commentSkip(tokens)
        tokens.pop(0)
        return [".DIE",L]#maybe change this to allow .DIE(THING); as well.
    elif(isalnum2(token)):
        #print "debug: got to var ",token
        return ['var',token]
    else:
        return ["err",token]
    return None

def read_all_from(tokens):
    """does the read_from until its exhausted all the tokens"""
    parsedCode=[]
    prevThingy=None
    while(tokens):
        #commentSkip(tokens)
        nextThingy=read_from(tokens)#TODO: change that variable name.
        if((prevThingy != None)):
            if((prevThingy[0] in ["var","literal string","pair/tuple",".DIE"]) and (nextThingy[0]==".DIE")):
                nextThingy.insert(1,prevThingy)
            else:
                parsedCode.append(prevThingy)
        prevThingy=nextThingy
        commentSkip(tokens)
    parsedCode.append(prevThingy)
    return parsedCode

def deathParser(thingysList=None):
    if(thingysList[-1][0]==".DIE"):
        nextThingy=thingysList.pop()
        if((thingysList!=None) and varLike(thingysList[-1])):
            prevThingy=thingysList.pop()
            nextThingy.insert(1,prevThingy)
        else:
            pass#nextThingy.insert(1,["err","no variable for .die"])
        thingysList.append(nextThingy)

def varLike(thingy):
    if(thingy[0] in ["var","literal string","pair/tuple",".DIE"]):
        return True
    else:
        return False


def isalnum2(string):
    if(string=="" or string.isalnum()):
        return True
    return False
