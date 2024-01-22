import re

# Function will determine if the number provided is a proper fraction number
def checkFraction(number):
    # Check after the fraction if it is only numbers present, no second period
    fractionMatch = re.search('^[0-9]+$', number[1:])
    if (fractionMatch != None):
            
        # Checking if a trailing zero is present
        trailingMatch = re.search('^[0]+$', number[-1])
            
        if (trailingMatch != None):
                
            # This indicates the fraction is .0 since it needs to start with a period then end with a 0 and be of length 2
            if len(number) == 2:
                print(f"fraction: {number}")
                
            # Fraction has a trailing zero and is hence refused
            else:
                print(f"invalid fraction: {number}, cannot have a trailing zero")
        else:
            print(f"fraction: {number}")
    else:
        print(f"invalid fraction: {number}, contains invalid characters after the period")
        
def checkInteger(number):
    # Check if the integer is specifically 0
    if (number == "0"):
        print(f"integer: {number}")
    # Otherwise leading zeros are not allowed in an integer
    else:
        if (number[0] == "0"):
            print(f"Invalid integer: {number}, cannot have leading zeros")
        else:
            print(f"integer: {number}")

def checkFloat(number):
    floatNumber = re.split('.', number)
    checkInteger(floatNumber[0])
    floatExponent = re.split('e', floatNumber[1])
    checkFraction("." + floatExponent[0])
    
    exponentMatch = re.search('^[+-]+$', floatExponent[1][0])
    if (exponentMatch != None):
        checkInteger(floatExponent[1][1:])
    else:
        print(f"invalid float: {number}, exponent is not written correctly")
        
reserved = ["==", "<>", "<", ">", "<=", ">=", "+", "-", "*", "/", "=", "|", "&", "!", "(", ")", "{", "}", "[", "]", ";", ",", ".", ":", "->", "if", "then", "else", "integer", "float", "void", "public", "private", "func", "var", "struct", "while", "read", "write", "return", "self", "inherits", "let", "impl"]
comments = ["/*", "//"]

filename = input("Enter filename: ")
file = open(f"{filename}.txt", "r")

for line in file:
    
    # Regex pattern splits on spaces, semicolons, newlines, whitespaces and colons, list comprehension is used to remove any additional white space
    lexemes = [x for x in re.split('; |, |\*|\n|\s|:', line.strip()) if x]
    
    for lexeme in lexemes:
        
        # The following line is a comment, deal with it accordingly
        if (lexeme in comments):
            
            # Line comment, will ignore the rest of the line
            if (lexeme == "//"): 
                break
            # This means it is a block comment, will need to keep searching for the end of the block comment or that start of another nested comment TODO
            else:
                blockComment = True
                continue
            
        # Proccess lexeme, under this regex all valid strings should be accepted
        match = re.search('^[0-9a-zA-Z_.+-]+$', lexeme)
        
        # This means that there is an invalid character present in the string, thus making it invalid
        if (match == None):
            print(f"Invalid element: {lexeme}")
        
        # This means that the lexeme is either an integer, float, fraction or digit/nonzero
        numberMatch = re.search('^[0-9e.+-]+$', lexeme)
        if (numberMatch != None):
            print(f"number: {lexeme}")
            
            # This indicates that the first character is a period, must be a fraction.
            if (lexeme[0] == "."):
                checkFraction(lexeme)
            
            # Check if the whole number is an integer
            integerMatch = re.search('^[0-9]+$', lexeme)
            if (integerMatch != None):
                checkInteger(lexeme)
                
            # The only remaining option now is to check if its a float
            else:
                checkFloat(lexeme)    
                
        # Since it passes the valid strings and isnt in the above category, it must be an id, alphanum or letter
        letterMatch = re.search('^[a-zA-Z_]+$', lexeme)
        if (letterMatch != None):
            
            # Determine if the string is an id or alphanum by looking at the first character of the string
            leadingCharacterMatch = re.search('^[a-zA-Z]+$', lexeme[0])
            if (leadingCharacterMatch != None):
                print(f"id: {lexeme}")
            else:
                print(f"alphanumber: {lexeme}")
        
        # This means it was ultimately invalid as it was alphanum + period which is invalid   
        else:
            print(f"Invalid combination: {lexeme}. Contains both alphanum and period")