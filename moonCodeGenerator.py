# COMP 442 compiler design assignment 2 grammar parser + assignment 3 attribute grammar

import os
import re
import math
from collections import deque

# Dictionary which keeps track of the sizes of every data structure
dataSizes = {"integer":4, "float":8}

# Dictionary that keeps track of what offset each variable should be placed at
classOffsets = {}

# Variable that keeps track of what returns tag is used for each function
global functionReturns
functionReturns = {}

# Variable that keeps track of the tag that refers to each function
global functionReturnLoc
functionReturnLoc = {}

# Flag that allows tags to be placed in the left most column
global conditionalFlag
conditionalFlag = False

# Variable generator to ensure looping variables stay unique
global loopCounter
loopCounter = 1

# Variable generator to ensure if variables stay unique
global ifCounter
ifCounter = 1

# Variable generator to ensure intermediates variables stay unique
global intermediateCounter
intermediateCounter = 1

# Variable generator to ensure intermediates for expressions stay unique
global intermediateArithmetic
intermediateArithmetic = 1

# Default empty tag
global loopVar
loopVar = " " * 8

"""
Function initializes the code output file and begins writing the lines (entry and the top of the stack)
outputName: name of the source file to allow appropriate naming of the .moon file
"""
def beginProgram(outputName):
    
    global output
    
    if not os.path.exists(outputName):
        generatedCodeFile = open(outputName, "x")
    else:
        generatedCodeFile = open(outputName, "w") 
    
    output = generatedCodeFile    
    print(" " * 8 + "\t   entry".ljust(24) + "% Start here", file=output)
    print(" " * 8 + " addi".ljust(8) + " r14,r0,topaddr".ljust(21) + "% Define top of the stack in case we need to print later", file=output)

"""
Function which uses the passed AST to determine the allocation of the variables it needs for the program
ast: Abstract Syntax Tree that was generated in the previous assignment
"""
def allocateMemory(ast):
    allocation = " " * 8 + " buf".ljust(8) + " res 20".ljust(21) + "% Buffer reservation in case printing to console is needed\n"
    for definedClass in ast.getClasses():
        className = definedClass.getTableName()
        classOffsets[className] = {}
        currentSize = 0
        for dataMember in definedClass.getData():
            if "[" in dataMember[1]:
                memberType = dataMember[1].split("[")[0]
                indexes = re.findall(r"\[\s*\+?(-?\d+)\s*\]", dataMember[1])
                indexes = [int(i) for i in indexes]
                numOfObjects = math.prod(indexes)
                classOffsets[className][dataMember[0]] = currentSize
                currentSize += dataSizes[memberType] * numOfObjects
            else:
                classOffsets[className][dataMember[0]] = currentSize
                currentSize += dataSizes[dataMember[1]]
        dataSizes[className] = currentSize
    for function in ast.getFunction():
        for dataMember in function.getLocal():
            if "[" in dataMember[1]:
                    memberType = dataMember[1].split("[")[0]
                    indexes = re.findall(r"\[\s*\+?(-?\d+)\s*\]", dataMember[1])
                    indexes = [int(i) for i in indexes]
                    numOfObjects = math.prod(indexes)
                    allocation += reserveMemory(dataMember[0], memberType, numOfObjects)
            else:
                allocation += reserveMemory(dataMember[0], dataMember[1])

    # Return the code to reserve the correct varaibles and strip the final endline
    return allocation.rstrip()

"""
Function which will additionally print extra content to the code file, used for printing the functions and variable reservations after the running code
string: string to print to the code file
"""            
def printAllocation(string):
    print(string, file=output, end="")

"""
Function which reserves memory for the given variable, returns a string to construct the reservation code so it can later be called by printAllocation
name: name of the variable to be given
dataType: datatype of the variable (decides the size of the allocation)
members: optional param to specify that its and array of objects (defaults to 1)
"""            
def reserveMemory(name, dataType, members=1):
    if dataType in dataSizes:
        return " " * 8 + (" " + name).ljust(8) + (" res " + str(dataSizes[dataType] * members)).ljust(21) + f"% Reserve variable {name}\n"
    else:
        return f"% {dataType} is not defined currently"
    
"""
Function which writes the allocation variables for function, i.e. return variables and parameter passing functions
funcClass: class the function belongs to
name: name of the function
params: parameters to be given to the function
returnType: return type of the function
"""  
def reserveFunction(funcClass, name, params, returnType):
    global functionReturnLoc
    global functionReturns
    global loopVar
    functionReservation = ""
    functionIndex = len(functionReturnLoc)
    functionReturnLoc[f"{funcClass}.{name}"] = f"fn{functionIndex}"
    functionReturns[f"{funcClass}.{name}"] = returnType
    if returnType != "void":
        functionReservation += f"\n         fnres{functionIndex}".ljust(16) + f"  res {dataSizes[returnType]}".ljust(22) + "% Reserve memory for the return variable of the function"
    for var in params:
        paramIndex = 0
        functionReservation += f"\n         fn{functionIndex}p{paramIndex}".ljust(16) + f"  res {dataSizes[var[1]]}".ljust(22) + "% Reserve memory for the parameters passed to the function"
    return functionReservation

"""
Function which creates the break in the code to jump to the function to allow a proper program flow
funcClass: class which the function belongs to
funcName: name of the function
funcParameters: parameter that will be passed to the function
funcParamNames: name of each function parameter
"""        
def createFunctionBreakCode(funcClass, funcName, funcParameters, funcParamNames):
    global conditionalFlag
    global loopVar
    funcTag = functionReturnLoc[f"{funcClass}.{funcName}"]
    for i in range(len(funcParameters)):
        index = 0
        funcParam = f"{funcTag}p{index}"
        if funcParameters[i].isnumeric():
            print(loopVar + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{funcParameters[i]}".ljust(21) + f"% We are loading the number into r1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {funcParam}(r0),r1".ljust(21) + f"% Store that value in the address of function param {funcParam}", file=output)
            print(" " * 8 + " lw".ljust(8) + f" r1,{funcParam}(r0)".ljust(21) + f"% We are loading the stored input param into r1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {funcParamNames[0][i][0]}(r0),r1".ljust(21) + f"% We are inserting the input param into the variable the function expects it", file=output)
        if conditionalFlag:
            loopVar = " " * 8
            conditionalFlag = False
        index += 1
    print(" " * 8 + " jl".ljust(8) + f" r12,{funcTag}".ljust(21) + f"% Jump to function {funcTag}", file=output)

"""
Function that reserves the parameters for a function
parametersName: tuples of names and datatypes to allow the proper labeling and reservation of memory
""" 
def reserveFunctionParam(parametersName):
    functionReservationCode = ""
    for var, type in parametersName[0]:
        functionReservationCode += f"\n         {var}".ljust(16) + f"  res {dataSizes[type]}".ljust(22) + "% Reserve memory for the function parameter"
    return functionReservationCode

"""
Function that reserves a single parameter instead of all in a loop
var: name of the variable to reserve
type: type of the variable to reserve
""" 
def reserveSingleParam(var, type):
    functionReservationCode = ""
    functionReservationCode += f"\n         {var}".ljust(16) + f"  res {dataSizes[type]}".ljust(22) + "% Reserve memory for the intermediate parameter"
    return functionReservationCode

"""
Function which begins the start of the code of a function, ensure the correct label is placed
className: name of the class the function belongs to
func: name of the function
""" 
def beginFunctionCode(className, func):
    global loopVar
    global conditionalFlag
    functionLabel = functionReturnLoc[f"{className}.{func}"]
    loopVar = functionLabel.ljust(8)
    conditionalFlag = True

"""
Function which allows the proper termination of the function block to allow jumping back to the original code
""" 
def endFunctionCode():        
    return " " * 8 + " jr".ljust(8) + f" r12".ljust(21) + f"% Jump back to the position the function was called\n"

"""
Function which provides moon code for setting a variable to a given value
name: name of the variable
content: value to give to the variable
offset: offset that might need to be prsent to place the value in the correct position
""" 
def setVariable(name, content, offset):
    global loopVar
    global conditionalFlag
    print(loopVar + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    if offset == 0:
        if "." not in content:
            offset = "r0"
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            offset = "r2"
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the the first 8 bytes of {name}", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,8".ljust(21) + f"% Shift the offset by 8 bits", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the the last 8 bytes of {name}", file=output)
    else:
        if "." not in content:
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            offset = "r2"
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the first 8 bytes of {name}", file=output)
            offset += 8
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add an additional 8 bytes to the offset of the value into register 2", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the last 8 bytes of {name}", file=output)

"""
Function that allows passing the value of a variable to another variable
name: name of the variable
content: name of the variable that will be giving the value
offset: offset to position the variable in the correct place if doing this for an object/array
""" 
def setMemberVariableToVariable(name, content, offset):
    global loopVar
    global conditionalFlag
    if offset == 0:
        offset = "r0"
    print(loopVar + " lw".ljust(8) + f" r1,{content}({offset})".ljust(21) + f"% Load the variable into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store the variable into {name}", file=output) 

"""

""" 
def setIndexedContentMember(name, content, type, attribute, offset):
    global loopVar
    global conditionalFlag
    additionalOffset = classOffsets[type][attribute] + dataSizes[type] * int(offset[0])
    print(loopVar + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    if offset == 0:
        if "." not in content:
            offset = "r0"
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r0),r1".ljust(21) + f"% Store that value in the the first 8 bytes of {name}", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,8".ljust(21) + f"% Shift the offset by 8 bits", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the the last 8 bytes of {name}", file=output)
    else:
        if "." not in content:
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{additionalOffset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{additionalOffset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the first 8 bytes of {name}", file=output)
            additionalOffset += 8
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{additionalOffset}".ljust(21) + f"% Add an additional 8 bytes to the offset of the value into register 2", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the last 8 bytes of {name}", file=output)
    
"""

""" 
def setMemberVariable(name, content, varType, offset, additionalOffset):
    global loopVar
    global conditionalFlag
    offset = classOffsets[varType][offset] + additionalOffset
    print(loopVar + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    if offset == 0:
        if "." not in content:
            offset = "r0"
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r0),r1".ljust(21) + f"% Store that value in the the first 8 bytes of {name}", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,8".ljust(21) + f"% Shift the offset by 8 bits", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal portion of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the the last 8 bytes of {name}", file=output)
    else:
        if "." not in content:
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            offset = "r2"
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content}".ljust(21) + f"% Add the content of the value into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}({offset}),r1".ljust(21) + f"% Store that value in the address of {name}", file=output)
        else:
            content = str(content).split(".")
            print(" " * 8 + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[0]}".ljust(21) + f"% Add the integer content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the first 8 bytes of {name}", file=output)
            offset += 8
            print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add an additional 8 bytes to the offset of the value into register 2", file=output)
            print(" " * 8 + " sub".ljust(8) + f" r1,r1,r1".ljust(21) + f"% Reset the value of register 1", file=output)
            print(" " * 8 + " addi".ljust(8) + f" r1,r1,{content[1]}".ljust(21) + f"% Add the decimal content of the float into register 1", file=output)
            print(" " * 8 + " sw".ljust(8) + f" {name}(r2),r1".ljust(21) + f"% Store that value in the last 8 bytes of {name}", file=output)

"""
Function which does the multiplication code and stores it in the returned intermediate
term1: first term in the equation
term2: term to multiply from the first term
""" 
def createMultOperation(term1, term2):
    global loopVar
    global conditionalFlag
    global intermediateArithmetic
    if term1.isnumeric() or term2.isnumeric():
        if term1.isnumeric() and (not term2.isnumeric()):
            temp = term1
            term1 = term2
            term2 = temp
        print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
        if conditionalFlag:
            loopVar = " " * 8
            conditionalFlag = False
        print(" " * 8 + " muli".ljust(8) + f" r2,r1,{term2}".ljust(21) + f"% Multiply r1 by the term", file=output)
        print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r2".ljust(21) + f"% Store the result in the intermediate", file=output)
    else:
        print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
        if conditionalFlag:
            loopVar = " " * 8
            conditionalFlag = False
        print(" " * 8 + " lw".ljust(8) + f" r2,{term2}(r0)".ljust(21) + f"% We are loading {term2} into r2", file=output)
        print(" " * 8 + " mul".ljust(8) + f" r3,r1,r2".ljust(21) + f"% Multiply the numbers into r3", file=output)
        print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r3".ljust(21) + f"% Store the result in the intermediate", file=output)
    intermediateArithmetic += 1
    return intermediateArithmetic - 1

"""
Function which does the addition code and stores it in the returned intermediate
term1: first term in the equation
term2: term to add to the first term
""" 
def createAddOperation(term1, term2):
    global loopVar
    global conditionalFlag
    global intermediateArithmetic
    print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " addi".ljust(8) + f" r2,r1,{term2}".ljust(21) + f"% Add the number to r1", file=output)
    print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r2".ljust(21) + f"%  Store the result in the intermediate", file=output)
    intermediateArithmetic += 1
    return intermediateArithmetic - 1

"""
Function which does the division code and stores it in the returned intermediate
term1: first term in the equation
term2: term to divide from the first term
""" 
def createDivOperation(term1, term2):
    global loopVar
    global conditionalFlag
    global intermediateArithmetic
    print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " divi".ljust(8) + f" r2,r1,{term2}".ljust(21) + f"% Divide the number stored in r1 by the term", file=output)
    print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r2".ljust(21) + f"%  Store the result in the intermediate", file=output)
    intermediateArithmetic += 1
    return intermediateArithmetic - 1

"""
Function which does the subtraction code and stores it in the returned intermediate
term1: first term in the equation
term2: term to subtract from the first term
""" 
def createSubOperation(term1, term2):
    global loopVar
    global conditionalFlag
    global intermediateArithmetic
    if term1.isnumeric() or term2.isnumeric():
        if term1.isnumeric() and (not term2.isnumeric()):
            temp = term1
            term1 = term2
            term2 = temp
        print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
        if conditionalFlag:
            loopVar = " " * 8
            conditionalFlag = False
        print(" " * 8 + " subi".ljust(8) + f" r2,r1,{term2}".ljust(21) + f"% Subtract the number from the number in r1", file=output)
        print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r2".ljust(21) + f"% Store the result in the intermediate", file=output)
    else:
        print(loopVar + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
        if conditionalFlag:
            loopVar = " " * 8
            conditionalFlag = False
        print(" " * 8 + " lw".ljust(8) + f" r2,{term2}(r0)".ljust(21) + f"% We are loading {term2} into r2", file=output)
        print(" " * 8 + " sub".ljust(8) + f" r3,r1,r2".ljust(21) + f"% Subtract the numbers into r3", file=output)
        print(" " * 8 + " sw".ljust(8) + f" t{intermediateArithmetic}(r0),r3".ljust(21) + f"% Store the result in the intermediate", file=output)
    intermediateArithmetic += 1
    return intermediateArithmetic - 1

"""
Function which writes the content of the given variable with a given offset
name: name of the variable
offset: offset of the start of the variable to get the content of
""" 
def writeContent(name, offset):
    global loopVar
    global conditionalFlag
    if offset == 0:
        offset = "r0"
        print(loopVar + " lw".ljust(8) + f" r1,{name}({offset})".ljust(21) + f"% We are loading {name} into r1", file=output)
    else:
        print(loopVar + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
        print(" " * 8 + " addi".ljust(8) + f" r2,r2,{offset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
        print(" " * 8  + " lw".ljust(8) + f" r1,{name}(r2)".ljust(21) + f"% We are loading {name} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r1".ljust(21) + f"% Placing {name} onto the top of the stack", file=output)
    print(" " * 8 + " addi".ljust(8) + f" r1,r0,buf".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -12(r14),r1".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,intstr".ljust(21) + f"% Calling intstr subroutine from lib.m", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r13".ljust(21) + f"% Retrieve output of intstr and place where putstr expects it", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,putstr".ljust(21) + f"% Calling putstr subroutine from lib.m to print to console", file=output)

"""
Function which writes the content of an attribute of an object to the console
name: name of the object
type: type of the object
attribute: attribute of the object to print
offset: additional offset in the case its the member of an array
"""     
def writeContentMember(name, type, attribute, offset):
    global loopVar
    global conditionalFlag
    additionalOffset = classOffsets[type][attribute] + offset
    if additionalOffset == 0:
        offset = "r0"
        print(loopVar + " lw".ljust(8) + f" r1,{name}({offset})".ljust(21) + f"% We are loading {name} into r1", file=output)
    else:
        print(loopVar + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
        print(" " * 8 + " addi".ljust(8) + f" r2,r2,{additionalOffset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
        print(" " * 8  + " lw".ljust(8) + f" r1,{name}(r2)".ljust(21) + f"% We are loading {name} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r1".ljust(21) + f"% Placing {name} onto the top of the stack", file=output)
    print(" " * 8 + " addi".ljust(8) + f" r1,r0,buf".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -12(r14),r1".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,intstr".ljust(21) + f"% Calling intstr subroutine from lib.m", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r13".ljust(21) + f"% Retrieve output of intstr and place where putstr expects it", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,putstr".ljust(21) + f"% Calling putstr subroutine from lib.m to print to console", file=output)

"""
Function to write to console an attribute of an object in an array
name: name of the array
type: type of the objects contained
attribute: attribute of the object to be written to console
offset: index of the object to get
""" 
def writeIndexedContentMember(name, type, attribute, offset):
    global loopVar
    global conditionalFlag
    additionalOffset = classOffsets[type][attribute] + offset * dataSizes[type]
    if additionalOffset == 0:
        offset = "r0"
        print(loopVar + " lw".ljust(8) + f" r1,{name}({offset})".ljust(21) + f"% We are loading {name} into r1", file=output)
    else:
        print(loopVar + " sub".ljust(8) + f" r2,r2,r2".ljust(21) + f"% Reset the value of register 2", file=output)
        print(" " * 8 + " addi".ljust(8) + f" r2,r2,{additionalOffset}".ljust(21) + f"% Add the offset of the value into register 2", file=output)
        print(" " * 8  + " lw".ljust(8) + f" r1,{name}(r2)".ljust(21) + f"% We are loading {name} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r1".ljust(21) + f"% Placing {name} onto the top of the stack", file=output)
    print(" " * 8 + " addi".ljust(8) + f" r1,r0,buf".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -12(r14),r1".ljust(21) + f"% Load the buffer on the stack", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,intstr".ljust(21) + f"% Calling intstr subroutine from lib.m", file=output)
    print(" " * 8 + " sw".ljust(8) + f" -8(r14),r13".ljust(21) + f"% Retrieve output of intstr and place where putstr expects it", file=output)
    print(" " * 8 + " jl".ljust(8) + " r15,putstr".ljust(21) + f"% Calling putstr subroutine from lib.m to print to console", file=output)

"""
Function that writes code to write to console the variable given
name: name of the variable to write
""" 
def writeFunctionWriteCode(name):
    global loopVar
    global conditionalFlag
    returnedCode = ""
    returnedCode += loopVar + " lw".ljust(8) + f" r1,{name}(r0)".ljust(21) + f"% We are loading {name} into r1\n"
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    returnedCode += " " * 8 + " sw".ljust(8) + f" -8(r14),r1".ljust(21) + f"% Placing {name} onto the top of the stack\n"
    returnedCode += " " * 8 + " addi".ljust(8) + f" r1,r0,buf".ljust(21) + f"% Load the buffer on the stack\n"
    returnedCode += " " * 8 + " sw".ljust(8) + f" -12(r14),r1".ljust(21) + f"% Load the buffer on the stack\n"
    returnedCode += " " * 8 + " jl".ljust(8) + " r15,intstr".ljust(21) + f"% Calling intstr subroutine from lib.m\n"
    returnedCode += " " * 8 + " sw".ljust(8) + f" -8(r14),r13".ljust(21) + f"% Retrieve output of intstr and place where putstr expects it\n"
    returnedCode += " " * 8 + " jl".ljust(8) + " r15,putstr".ljust(21) + f"% Calling putstr subroutine from lib.m to print to console\n"
    return returnedCode

"""
Function which compares the terms using the operator provided and evaluates it
term1: value to compare
term2: other value to compare
operator: operator to compare the two value with
"""    
def createConditional(term1, term2, operator):
    global loopVar
    global conditionalFlag
    global intermediateCounter
    conditionals = {">":"cgt", ">=":"cge", "<":"clt", "<=":"cle", "==":"ceq", "<>":"cne"}
    intermediateVar = f"tn{intermediateCounter}"
    print(loopVar.ljust(8) + " lw".ljust(8) + f" r1,{term1}(r0)".ljust(21) + f"% We are loading {term1} into r1", file=output)
    if conditionalFlag:
        loopVar = " " * 8
        conditionalFlag = False
    if term2.isnumeric():
        changedOperator = conditionals[operator] + "i"
        print(" " * 8 + f" {changedOperator}".ljust(8) + f" r2,r1,{term2}".ljust(21) + f"% Check the condition compared to a literal value", file=output)
        print(" " * 8 + " sw".ljust(8) + f" {intermediateVar}(r0),r2".ljust(21) + f"% Value of the result will be stored here", file=output)
    else:
        print(" " * 8 + " lw".ljust(8) + f" r2,{term2}(r0)".ljust(21) + f"% We are loading {term2} into r2", file=output)
        print(" " * 8 + f" {conditionals[operator]}".ljust(8) + f" r3,r1,r2".ljust(21) + f"% Check the condition comapering both terms", file=output)
        print(" " * 8 + " sw".ljust(8) + f" {intermediateVar}(r0),r3".ljust(21) + f"% Value of the result will be stored here", file=output)
    print(" " * 8 + " lw".ljust(8) + f" r1,{intermediateVar}(r0)".ljust(21) + f"% We are loading {intermediateVar} into r1", file=output)
    intermediateCounter += 1
    return f"\n         {intermediateVar}".ljust(16) + "  res 4".ljust(22) + "% Reserve memory for the temp variable used to contain the result of the conditional"

"""
Function that generates the tag to jump to if the condition was true
""" 
def thenBlock():
    breakpointName = f"else{ifCounter}"
    print(" " * 8 + " bz".ljust(8) + f" r1,{breakpointName}".ljust(21) + f"% Send the code to the else block if condition false", file=output)
    return breakpointName

"""
Function which starts the else block by putting the correct tag in loopVar, returns the tag of the last block
blockName: name of the block to jump to if the condition was true (hence skipping this block)
""" 
def elseBlock(blockName):
    global loopVar
    nextBreakpointName = f"endif{ifCounter}"
    print(" " * 8 + " j".ljust(8) + f" {nextBreakpointName}".ljust(21) + f"% Skip the next code block if condtional was true", file=output)
    loopVar = blockName.ljust(8)
    return nextBreakpointName

"""
Function which allows the tagging of the next block using the block name given to it
blockName: name of the block used to after the if/then/else block
""" 
def endBlock(blockName):
    global loopVar
    global conditionalFlag
    global ifCounter
    loopVar = blockName.ljust(8)
    conditionalFlag = True
    ifCounter += 1

"""
Function which creates the while condition in the loopVar, this allows the tag to be present in the next line of code
"""     
def createWhileConditional():
    global loopVar
    global conditionalFlag
    loopName = f"swhile{loopCounter}"
    loopVar = f"swhile{loopCounter}".ljust(8)
    conditionalFlag = True
    return loopName

"""
Function which begins the while block, will return a variable that allows looping back to the start of this block
""" 
def createWhileBlock():
    loopVariable = f"ewhile{loopCounter}"
    print(" " * 8 + " bz".ljust(8) + f" r1,{loopVariable}".ljust(21) + f"% Send the code to the end while block if condition false", file=output)
    return loopVariable

"""
Function which generates the end of the while block to allow it to loop
whileloop: variable to jump back to
blockName: name of the block to jump to when the while condition is no longer satisfied, it is passed through to the loopVar to print on the next code print
"""     
def endWhileBlock(whileloop, blockName):
    global loopVar
    global conditionalFlag
    global loopCounter
    print(" " * 8 + " j".ljust(8) + f" {whileloop}".ljust(21) + f"% Skip the next code block if condtional was true", file=output)
    loopVar = blockName.ljust(8)
    conditionalFlag = True
    loopCounter += 1

"""
Function which prints the end of the moon code
"""       
def endCode():
    print(loopVar.ljust(8) + "\t   hlt".ljust(24) + "% All done", file=output)