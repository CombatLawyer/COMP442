# COMP 442 compiler design assignment 1 lexical analyzer

# This contains every reserved symbol that is expected to only be a single character, the ones with 2 characters are seperate entities in the dfa
reservedSymbols = ["|", "&", "!", "(", ")", "{", "}", "[", "]", ";", ",", ":"]

# This is a dictionary containing the names of the reserved symbols
reservedSymbolsNames = {"==":"eq", "+":"plus", "|":"or", "(":"lpar", ";":"semi", "<>":"neq", "-":"minus", "&":"and", ")":"rpar", ",":"comma", "<":"lt", "*":"mult", "!":"not", "{":"lcurbr", ".":"dot", ">":"gt", "/":"div", "}":"rcurbr", ":":"colon", "<=":"leq", "=":"equal", "[":"lsqbr", ">=":"geq", "]":"rsqbr", "->":"arrow"}

# Reserved words that have a specified meaning outside of just a normal lexeme
reservedWords = ["if", "then", "else", "integer", "float", "void", "public", "private", "func", "var", "struct", "while", "read", "write", "return", "self", "inherits", "let", "impl"]

# Non zero digits, zero is not included as it is its own letter in the dfa's alphabet
digit = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

# letters, e is not included as it is its own letter in the dfa's alphabet
letter = ["a", "b", "c", "d", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
dfa = {0:{"*":27, "+":29, "-":22, ".":30, "/":24, "0":1, "<":20, "=":15, ">":17, "_":"trap", "d":2, "e":3, "l":3, "s":14, "state":"id"},
       1:{"*":"trap", "+":"trap", "-":"trap", ".":4, "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"intlit"},
       2:{"*":"trap", "+":"trap", "-":"trap", ".":4, "/":"trap", "0":2, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":2, "e":"trap", "l":"trap", "s":"trap", "state":"intlit"},
       3:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":6, "<":"trap", "=":"trap", ">":"trap", "_":6, "d":6, "e":6, "l":6, "s":"trap", "state":"id"},
       4:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":7, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":7, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       6:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":6, "<":"trap", "=":"trap", ">":"trap", "_":6, "d":6, "e":6, "l":6, "s":"trap", "state":"id"},
       7:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":8, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":7, "e":9, "l":"trap", "s":"trap", "state":"floatlit"},
       8:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":8, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":7, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       9:{"*":"trap", "+":12, "-":12, ".":"trap", "/":"trap", "0":10, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":11, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       10:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       11:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":13, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":13, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       12:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":10, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":11, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       13:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":13, "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":13, "e":"trap", "l":"trap", "s":"trap", "state":"floatlit"},
       14:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       15:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":16, ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       16:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       17:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":18, ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       18:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       19:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       20:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":19, ">":21, "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       21:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       22:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":23, "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       23:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       24:{"*":26, "+":"trap", "-":"trap", ".":"trap", "/":25, "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       25:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       26:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       27:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":28, "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       28:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       29:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"},
       30:{"*":"trap", "+":"trap", "-":"trap", ".":"trap", "/":"trap", "0":"trap", "<":"trap", "=":"trap", ">":"trap", "_":"trap", "d":"trap", "e":"trap", "l":"trap", "s":"trap", "state":"symbol"}}

# Initial states of the dfa
initialState = [0]

# Acceptable end stated in the dfa
finalStates = {1:"intlit", 2:"intlit", 3:"id", 6:"id", 7:"floatlit", 10:"floatlit", 11:"floatlit", 13:"floatlit", 14:"symbol", 15:"symbol", 16:"symbol", 17:"symbol", 18:"symbol", 19:"symbol", 20:"symbol", 21:"symbol", 22:"symbol", 23:"symbol", 24:"symbol", 25:"//", 26:"/*", 27:"symbol", 28:"*/", 29:"symbol", 30:"symbol"}

comments = ["/*", "//"]

# Will keep track of the position of read() in the file
line = 1
col = 1 

def nextToken(filename):
    global file
    global line
    global col
    global terminating
    file = filename
    terminating = False
    state = initialState[0]
    token = ""
    lookUp = file.read(1).lower()
    colstart = col
    linestart = line
    
    # While there is still text to read in the file    
    while lookUp:
        
        # These symbols are spacers in the file, upon encountering them need evaluate the token
        if (lookUp in ["\n", " ", "\t"]) or terminating:
            
            terminating = False
            
            # Used to locate errors if they end in an invalid state
            tokenLastPos = col - 1
            
            # If the end of a line is reached, increment the position of the reader accordingly
            if lookUp == "\n":
                line += 1
                col = 1
            
            # If just a space is encountered, increment the position in the column by 1
            elif lookUp == " ":
                col += 1
                
            # If a tab is encountered, increment the position in the column by 4
            elif lookUp == "\t":
                col += 4
                
            # If the token is still empty, that means the previous lexeme was finished and we can skip the spacer and move on to the next valid character
            if token == "":
                lookUp = file.read(1).lower()
                colstart = col
                linestart = line
            
            # If the token is reserved, ensure that the output indicates that a reserve word was found and not a normal id
            elif token in reservedWords:
                return token, token, linestart, colstart
            
            # This is if the start of a comment is found
            elif token in comments:
                
                # This means the comment is a line commment
                if token == "//":
                    
                    # Read until either end of the line or 
                    while lookUp not in ["\n", ""]:
                        token = token + lookUp
                        lookUp = file.read(1).lower()
                    line += 1
                    col = 1
                    return token, "cmt", linestart, colstart 
                
                # This means the comment is a nested comment
                else:
                    nestedCount = 1
                    
                    # While there is still text available
                    while lookUp != [""]:
                        token = token + lookUp
                        col += 1
                        lookUp = file.read(1).lower()
                        
                        # Only these two symbols are relevant during the scan, one indicates another nested block, the other will close a block
                        if lookUp in ["/", "*"]:
                            symbol = lookUp + file.read(1).lower()
                            
                            # Indicated that another block comment is present in the block comment, increases the nested count number to accommodate the extra block
                            if symbol == "/*":
                                token = token + symbol
                                nestedCount += 1
                            
                            # This indicated the end of a block comment is found, will continue unless it closes the outer most block
                            elif symbol == "*/":
                                token = token + symbol
                                nestedCount -= 1
                                if nestedCount == 0:
                                    return token, "blockcmt", linestart, colstart
                                
                            # This is specifically for really weird comments, since its taken two at a time if **/ or //* is used itll skip over the correct sequence of symbols
                            elif symbol in ["**", "//"]:
                                # Only use the first symbol and begin the process again on the second symbol
                                token = token + symbol[0]
                                file.seek(file.tell()-1, 0)
                                col -= 1
                                
                        # Keep incrementing the line count
                        elif lookUp == "\n":
                            line += 1
                            col = 1
                    
                    # Indicates the file ended before closing the block, hence invalid comment block            
                    return token, {"error":"blockcmt"}, linestart, colstart
            
            # Properly send back the completed token and its state/position in the file, check if state is a final position, if not classify it an error
            else:
                if state not in finalStates.keys():
                    return token, {"error":dfa[state]["state"]}, linestart, tokenLastPos
                else:
                    if finalStates[state] == "symbol":
                        return token, reservedSymbolsNames[token], linestart, colstart
                    else:
                        return token, finalStates[state], linestart, colstart
            
        # If none of the spacer characters are found it means we have a text character
        else:
            
            # Store the position of the error
            errorPos = col
            
            # Store the current working character in the growing token
            token = token + lookUp
            col += 1
            
            # Translate token if its a letter or digit, keep in mind that zero is its own entity and is not included in digits and that e is its own symbol and not in letters
            if (lookUp in digit):
                lookUp = "d"
            elif (lookUp in letter):
                lookUp = "l"
            elif (lookUp in reservedSymbols):
                lookUp = "s"
            
            # If the symbol is not recognizable in the dfa then return this error
            if lookUp not in dfa[0].keys():
                return token, {"error":"character"}, linestart, colstart
            
            # Keep the previous state
            prevstate = state
        
            # Using the current symbol look up at what position the next character will result in the dfa
            state = dfa[state][lookUp]
            
            # If the move leads to entering a trap state then the string is invalid and we can stop evalutaiton here
            if state == 'trap':
                
                # Finish the rest of the token
                lookUp = file.read(1).lower()
                col += 1
                while lookUp not in ["\n", " ", "", "\t"]:
                    token = token + lookUp
                    lookUp = file.read(1).lower()
                    col += 1
                    
                # Increment the line if it was the last token on the current line
                if lookUp == "\n":
                    line += 1
                    col = 1
                    
                # Return the erroneous token
                return token, {"error":dfa[prevstate]["state"]}, linestart, errorPos
          
            # These are to evaluate lexemes without spaces between them
            # First if we have a number      
            if state in [1, 2, 7, 10, 11, 13]:
                
                # Continue with the next character in the file
                lookUp = file.read(1).lower()
                
                # If we swap to symbols, immedaitely flag the letter as done        
                if lookUp in (reservedSymbols + ["*", "+", "-", "/", "<", "=", ">"]):
                    file.seek(file.tell()-1, 0)
                    terminating = True
            
            # Next if we have an id     
            elif state in [3, 6]:
                
                # Continue with the next character in the file
                lookUp = file.read(1).lower()
                
                # If we swap to symbols, immedaitely flag the letter as done        
                if lookUp in (reservedSymbols + ["*", "+", "-", "/", "<", "=", ">", "."]):
                    file.seek(file.tell()-1, 0)
                    terminating = True

            # Else if we have a symbol
            elif state in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]:
                
                # Continue with the next character in the file
                lookUp = file.read(1).lower()

                if lookUp not in ["", "\n", " ", "\t"]:
                    # if we swap to letters or digits or if the next symbol does not lead to a two character symbol,
                    # immediately flag the symbol as done       
                    if (lookUp in (digit + letter + ["e", "0"])) | (token + lookUp not in ["==", "<>", "<=", ">=", "->", "//", "/*"]):
                        file.seek(file.tell()-1, 0)
                        terminating = True
            
            else:
                lookUp = file.read(1).lower()

    # This is to deal specifically with the last token of the file, as the loop above is broken, if there is a token that is being built it needs to sent out
    if token != "":
        
        # Used to locate errors if they end in an invalid state
        tokenLastPos = col - 1
        
        # Ensures that a reserved word is still recognized
        if token in reservedWords:
            return token, token, linestart, colstart
        
        # Otherwise the output is a normal token, check if state is a final position, if not classify it an error
        if state not in finalStates.keys():
            return token, {"error":dfa[state]["state"]}, linestart, tokenLastPos
        else:
            if finalStates[state] == "symbol":
                return token, reservedSymbolsNames[token], linestart, colstart
            else:
                return token, finalStates[state], linestart, colstart
    
    # Indicates that the end of the file is reached    
    else:
        return -1