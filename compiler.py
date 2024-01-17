import re

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
        match = re.search('^[0-9a-zA-Z_.]+$', lexeme)
        
        # This means that there is an invalid character present in the string, thus making it invalid
        if (match == None):
            print(f"Invalid element: {lexeme}")
        
        # This means that the lexeme is either an integer, float, fraction or digit/nonzero
        numberMatch = re.search('^[0-9e.]+$', lexeme)
        if (numberMatch != None):
            print(f"number: {lexeme}")
        
        # Since it passes the valid strings and isnt in the above category, it must be an id, alphanum or letter
        else:
            print(f"alphanumber: {lexeme}")
            
            
            