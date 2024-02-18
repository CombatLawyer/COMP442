# COMP 442 compiler design assignment 1 lexical analyzer

import os
import lexicalAnalyzer
import grammarParser
from collections import deque

# Allows input for the file to be used
filename = input("Enter filename: ")
file = open(f"{filename}.src", "r")

# Names of the output and error files created by the compiler
outputErrorName = f"{filename}.outlexerrors"

# If file does not exist, create it, otherwise overwrite the old one    
if not os.path.exists(outputErrorName):
    e = open(outputErrorName, "x")
else:
    e = open(outputErrorName, "w")

# Queue that will contain all the lexemes
lexicon = deque()
    
while 1:
    lexeme = lexicalAnalyzer.nextToken(file)
    
    # Until the nextToken function reaches the end of the file
    if lexeme == -1:
        break
    
    # Don't need to parse comments
    if lexeme[1] in ["cmt", "blockcmt"]:
        continue
    
    # If the lexeme is classified as an error print it to the error file and skip parsing otherwise
    if isinstance(lexeme[1], dict):
        e.write(f'Lexical Error: Invalid {lexeme[1]["error"]}: \"{lexeme[0]}\", found at line {lexeme[2]}, col {lexeme[3]}.\n')
        continue
    
    # Append all lexemes into the queue
    lexicon.append([lexeme[0], lexeme[1], lexeme[2], lexeme[3]])

# Send lexicon to be parsed
grammarParser.parseToken(lexicon, filename)

# Close all the files that were open  
file.close()
e.close()

'''
Legacy code for printing productions
outputFileName = f"{filename}.outlextokens"
# If file does not exist, create it, otherwise overwrite the old one
if not os.path.exists(outputFileName):
    f = open(outputFileName, "x")
else:
    f = open(outputFileName, "w")
else:
    if lexeme[2] not in lexicon.keys():
        lexicon[lexeme[2]] = []
    lexicon[lexeme[2]].append([lexeme[1], lexeme[0], lexeme[2], lexeme[3]])
for line in lexicon:
    print(*lexicon[line], file=f)
f.close()
'''