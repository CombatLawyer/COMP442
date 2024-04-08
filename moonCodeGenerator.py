# COMP 442 compiler design assignment 2 grammar parser + assignment 3 attribute grammar

import os
from collections import deque
import grammarParser

dataSizes = {"integer":4, "float":8}

def allocateMemory(ast, output):
    for function in ast.getFunction():
        for param in function.getLocal():
            reserveMemory(param[0], param[1], output)
            
def reserveMemory(name, dataType, output):
    if dataType in dataSizes:
        print((" " + name).ljust(8) + (" res " + str(dataSizes[dataType])).ljust(21) + f"% reserve variable {name}", file=output)