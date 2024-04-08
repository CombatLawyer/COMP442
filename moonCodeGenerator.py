# COMP 442 compiler design assignment 2 grammar parser + assignment 3 attribute grammar

import os
from collections import deque
import grammarParser

dataSizes = {"integer":4, "float":8}

def beginProgram(outputName):
    
    global output
    
    if not os.path.exists(outputName):
        generatedCodeFile = open(outputName, "x")
    else:
        generatedCodeFile = open(outputName, "w") 
    
    output = generatedCodeFile    
    print("\t\t entry".ljust(23) + "% Start here", file=output)

def allocateMemory(ast):
    for function in ast.getFunction():
        for param in function.getLocal():
            reserveMemory(param[0], param[1])
            
def reserveMemory(name, dataType):
    if dataType in dataSizes:
        print((" " + name).ljust(8) + (" res " + str(dataSizes[dataType])).ljust(21) + f"% Reserve variable {name}", file=output)
        
def setVariable(name, content, offset):
    if offset == 0:
        offset = "r0"
    print(" sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
    print(" addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
    print(" sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)