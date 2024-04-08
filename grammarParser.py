# COMP 442 compiler design assignment 2 grammar parser + assignment 3 attribute grammar

import os
from collections import deque
import networkx as nx
import moonCodeGenerator

# Initialize the stack used for sematinc actions
semantic = deque()

"""
Class used as nodes for AST building, has a nodeType (the type of node), a parent and children.
"""
class Node():
    def __init__(self, nodeType, children, value=None):
        self.nodeType = nodeType
        self.parent = None
        self.value = value
        self.children = children
    
    def getNodeType(self):
        return self.nodeType
    
    def getChildren(self):
        return self.children
    
    def getValue(self):
        return self.value
    
    def setParent(self, parent):
        self.parent = parent

"""
Class used as leaves for AST building, has a nodeType and parent but no children.
"""
class Leaf():
    def __init__(self, nodeType, line, value=None):
        self.nodeType = nodeType
        self.value = value
        self.parent = None
        self.line = line
        
    def getNodeType(self):
        return self.nodeType
    
    def getValue(self):
        return self.value
    
    def getLine(self):
        return self.line
    
    def setParent(self, parent):
        self.parent = parent

class Table():
    def __init__(self, id):
        self.name = id
        self.inherits = []
        self.data = []
        self.function = []
        self.classes = []
        
    def getTableName(self):
        return self.name
    
    def getInherits(self):
        return self.inherits
    
    def getData(self):
        return self.data
    
    def getFunction(self):
        return self.function
    
    def getClasses(self):
        return self.classes
    
    def addInherits(self, id):
        self.inherits.append(id)
        
    def addData(self, id, type, visibility):
        self.data.append((id, type, visibility))
        
    def addFunction(self, function):
        self.function.append(function)
    
    def addClasses(self, table):
        self.classes.append(table)

class Function():
    def __init__(self, id, returnType, visibility):
        self.name = id
        self.returnType = returnType
        self.visibility = visibility
        self.param = []
        self.local = []
        
    def getFuncName(self):
        return self.name
    
    def getReturnType(self):
        return self.returnType
    
    def getParam(self):
        return self.param
    
    def getVisibility(self):
        return self.visibility
    
    def getLocal(self):
        return self.local
        
    def addParam(self, id, type):
        self.param.append((id, type))
    
    def addLocal(self, id, type):
        self.local.append((id, type))

"""
Creates a leaf of the specified type (used to make intlits, floatlits and ids)
"""
def createLeaf(string, line, value):
    leaf = Leaf(string, line, value)
    semantic.append(leaf)

"""
Creates a dim leaf, used to specify a dimension for variables
"""    
def createLeafDim(line, notused):
    if semantic[-1].getNodeType() == "Epsilon":
        leaf = Leaf("dim", line, "[]")
    else:
        value = semantic[-1].getValue()
        semantic.pop()
        leaf = Leaf("dim", line, f"[{value}]")
    semantic.pop()
    semantic.append(leaf)

"""
Creates a type leaf, used when specifying return types
"""     
def createLeafType(line, value):
    leaf = Leaf("type", line, value)
    semantic.append(leaf)

"""
Creates a visibility leaf, used to specify the visibility of a function or variable
"""     
def createLeafVisibility(line, value):
    leaf = Leaf("Visibility", line, value)
    semantic.append(leaf)

"""
Creates a sign leaf, used to specify that whatever after is signed
"""     
def createLeafSign(line, notused):
    leaf = Leaf("Sign", line)
    semantic.append(leaf)

"""
Creates an epsilon node, used in cases where the node will take a variable length of children
"""     
def createLeafEpsilon():
    leaf = Leaf("Epsilon", 0)
    semantic.append(leaf)

"""
Create a dimlist node which looks speicfically to group the dim leaves in a variable declaration
"""
def createDimNode():
    dimList = []
    while semantic[-1].getNodeType() == "dim":
        leaf = semantic.pop()
        dimList.append(leaf)
    node = Node("Dimlist", dimList)
    for dimLeaf in dimList:
        dimLeaf.setParent(node)
    semantic.append(node)

"""
Variable declaration node, will take in an id (the name of the variable), a type and a dimlist 
"""     
def createVardeclNode():
    dimList = semantic.pop()
    type = semantic.pop()
    id = semantic.pop()
    node = Node("VarDecl", [id, type, dimList])
    for child in [id, type, dimList]:
        child.setParent(node)
    semantic.append(node)

"""
Parameter list node will look to group variable declarations in the parameter list of a function/struct/impl definition
"""     
def createParamListNode():
    paramList = []
    while semantic[-1].getNodeType() == "VarDecl":
        child = semantic.pop()
        paramList.append(child)
    node = Node("ParamList", paramList)
    for paramChild in paramList:
        paramChild.setParent(node)
    semantic.append(node)

"""
Function definition node will look to take in an id (the name of the function), the list of parameters it defines, and the return type
"""     
def createFuncDefNode():
    type = semantic.pop() 
    paramList = semantic.pop()
    id = semantic.pop()
    node = Node("FuncDef", [id, paramList, type])
    for child in [id, paramList, type]:
        child.setParent(node)
    semantic.append(node)

"""
Function creates a write node which specifies that the object on the top of the stack is to be used in the system write function
""" 
def createWriteNode():
    writeContent = semantic.pop() 
    node = Node("WriteNode", writeContent)
    writeContent.setParent(writeContent)
    semantic.append(node)

"""
Function creates a read node which specifies that the object on the top of the stack is to be used in the system read function
"""     
def createReadNode():
    readVariable = semantic.pop() 
    node = Node("ReadNode", readVariable)
    readVariable.setParent(node)
    semantic.append(node)

"""
Function creates a return node which specifies that the object on the top of the stack is to be used by returning at the end of a function
"""     
def createReturnNode():
    returnVariable = semantic.pop()
    node = Node("ReturnNode", returnVariable)
    returnVariable.setParent(node)
    semantic.append(node)

"""
Function creates a conditional node which groups a conditional right and left half
""" 
def createConditionNode():
    leftValue = semantic.pop()
    rightValue = semantic.pop()
    node = Node("ConditionNode", [rightValue, leftValue])
    rightValue.setParent(node)
    leftValue.setParent(node)
    semantic.append(node)

"""
Function creates a while node which takes in the condition node and specifies it as the while condition
""" 
def createWhileNode():
    whileCondition = semantic.pop()
    node = Node("WhileNode", whileCondition)
    whileCondition.setParent(node)
    semantic.append(node)

"""
While block encompasses the statements in the while block using the epsilon placed beforehand
"""
def createWhileBlockNode():
    whileStatements = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        whileStatements.append(leaf)
    whileStatements.reverse()
    node = Node("WhileBlockNode", whileStatements)
    for child in whileStatements:
        child.setParent(node)
    
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
If node is the same as the while but specifies the condition for an if instead
"""    
def createIfNode():
    whileCondition = semantic.pop()
    node = Node("IfNode", whileCondition)
    whileCondition.setParent(node)
    semantic.append(node)

"""
Then block will encompass the statements inside the then block
"""    
def createThenNode():
    thenStatements = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        thenStatements.append(leaf)
    thenStatements.reverse()
    node = Node("ThenNode", thenStatements)
    for child in thenStatements:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
Does the same thing as the then node but is used for the else block
"""    
def createElseNode():
    elseStatements = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        elseStatements.append(leaf)
    elseStatements.reverse()
    node = Node("ElseNode", elseStatements)
    for child in elseStatements:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
This is never used, supposed to capture what is in between parenthesis when a factor production uses it
"""    
def createFuncArgNode():
    args = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        args.append(leaf)
    args.reverse()
    node = Node("FuncArgs", args)
    for child in args:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)
    
"""
Creates a list for the parameters in a function call using the epsilon placed beforehand
"""
def createFuncParamList():
    paramList = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        paramList.append(leaf)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    paramList.reverse()
    node = Node("FuncParamList", paramList)
    for child in paramList:
        child.setParent(node)
    semantic.append(node)

"""
Function body encompasses the nodes which are present in the body of the function
"""    
def createFuncBodyNode():
    funcStatements = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        funcStatements.append(leaf)
    node = Node("FuncBody", funcStatements)
    funcStatements.reverse()
    for child in funcStatements:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
Generates an inherits node which gathers all the ids which the struct inherits from
"""
def createInheritsNode():
    inherits = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        inherits.append(leaf)
    node = Node("InheritsNode", inherits)
    for child in inherits:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
Struct definition takes in the id which gives the name of the struct and the inherits node
"""
def createStructDefNode():
    inherits = semantic.pop()
    name = semantic.pop()
    node = Node("StructDef", [name, inherits])
    inherits.setParent(node)
    name.setParent(node)
    semantic.append(node)

"""
Struct body includes all the statments in the body of the struct
"""
def createStructBodyNode():
    structBody = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        structBody.append(leaf)
    node = Node("StructBodyNode", structBody)
    structBody.reverse()
    for child in structBody:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
Struct decl node are variable declarations but with the visibility added
"""
def createStructDeclNode():
    declaration = semantic.pop()
    visibility = semantic.pop()
    node = Node("StructDeclNode", [visibility, declaration])
    visibility.setParent(node)
    declaration.setParent(node)
    semantic.append(node)

"""
Impl definitions involve just the id that the impl is given
"""
def createImplDefNode():
    id = semantic.pop()
    node = Node("ImplDef", id)
    id.setParent(node)
    semantic.append(node)

"""
Impl bodies invlove the nodes in the body of the impl
"""
def createImplBodyNode():
    implBody = []
    
    # Search for the epsilon placed at the start of the block
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        implBody.append(leaf)
    implBody.reverse()
    node = Node("ImplBodyNode", implBody)
    for child in implBody:
        child.setParent(node)
        
    # Ensure that the epsilon is popped off the stack
    semantic.pop()
    semantic.append(node)

"""
Signed nodes take in whatever is after the sign leaf and indicates that this is all signed by the sign at the front.
"""
def createSignedNode():
    signed = []
    
    # Look for the sign leaf
    while semantic[-1].getNodeType() != "Sign":
        leaf = semantic.pop()
        signed.append(leaf)
    
    # Ensure that the sign leaf is also included in the sign node
    leaf = semantic.pop()
    signed.append(leaf)
    signed.reverse()
    node = Node("SignedNode", signed)
    for child in signed:
        child.setParent(node)
    semantic.append(node)
    
"""
Indice nodes will check the stack and check if id is prsent under the top of the stack (this indicates that this current id or intlit 
is an indice of that id). If another indice node is found there, then ther indice node is remade with the new indice added.
"""    
def createIndiceNode():
    if semantic[-2].getNodeType() in ["id"]:
        indice = semantic.pop()
        array = semantic.pop()
        node = Node("IndiceNode", [array, indice])
        indice.setParent(node)
        array.setParent(node)
        semantic.append(node)
    elif semantic[-2].getNodeType() == "IndiceNode":
        indice = semantic.pop()
        array = semantic.pop()
        node = Node("AttributeNode", array.getChildren() + [indice])
        indice.setParent(node)
        for child in array.getChildren():
            child.setParent(node)
        semantic.append(node)

"""
The add node takes in two values (right and left) and indicates that an add operation will combine them (add or subtract)
"""
def createAddNode():
    rightValue = semantic.pop()
    leftValue = semantic.pop()
    node = Node("AddOp", [rightValue, leftValue])
    rightValue.setParent(node)
    leftValue.setParent(node)
    semantic.append(node)

"""
The mult node takes in two values (right and left) and indicates that an add operation will combine them (multiply or divide)
"""    
def createMultNode():
    rightValue = semantic.pop()
    leftValue = semantic.pop()
    node = Node("MultOp", [rightValue, leftValue])
    rightValue.setParent(node)
    leftValue.setParent(node)
    semantic.append(node)

"""
The and node takes in two values (right and left) and indicates that an and operation will evaluate them together
"""    
def createAndNode():
    rightValue = semantic.pop()
    leftValue = semantic.pop()
    node = Node("AndOp", [rightValue, leftValue])
    rightValue.setParent(node)
    leftValue.setParent(node)
    semantic.append(node)

"""
The or node takes in two values (right and left) and indicates that an or operation will evaluate them together
"""     
def createOrNode():
    rightValue = semantic.pop()
    leftValue = semantic.pop()
    node = Node("OrOp", [rightValue, leftValue])
    rightValue.setParent(node)
    leftValue.setParent(node)
    semantic.append(node)

"""
The assign node will pair the assignment of a variable with the expression on top of the stack to pass its value
""" 
def createAssignNode():
    expression = semantic.pop()
    variable = semantic.pop()
    node = Node("AssignVar", [variable, expression])
    variable.setParent(node)
    expression.setParent(node)
    semantic.append(node)

"""
Creates an expr subtree by using the epsilon delimited before the expr production, guaranteed to encompass the whole subtree
""" 
def createExprNode():
    expression = []
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        expression.append(leaf)
    expression.reverse()
    node = Node("ExprNode", expression)
    for child in expression:
        child.setParent(node)
    semantic.pop()
    semantic.append(node)

"""
The attribute node checks first if an id or an attribute is under the top most entry of the stack (guaranteed to be id on the top), if not it does nothing.
Otherwise if its an id it will group the id and the the id it is associated with. If its an attribute node it will grow the node by making a new one and adding
the new attribute.
""" 
def createAttributeNode():
    if semantic[-2].getNodeType() == "id":
        attribute = semantic.pop()
        parentId = semantic.pop()
        node = Node("AttributeNode", [parentId, attribute])
        attribute.setParent(node)
        parentId.setParent(node)
        semantic.append(node)
        
    elif semantic[-2].getNodeType() == "AttributeNode":
        attribute = semantic.pop()
        parentId = semantic.pop()
        
        # Grow the node by making a new node with the same children + the new attribute
        node = Node("AttributeNode", parentId.getChildren() + [attribute])
        attribute.setParent(node)
        for child in parentId.getChildren():
            child.setParent(node)
        semantic.append(node)

"""
Create a prog node (the root node) using the epsilon placed at the start it will encompass all the nodes left on the stack
"""     
def createProgNode():
    progBlocks = []
    while semantic[-1].getNodeType() != "Epsilon":
        leaf = semantic.pop()
        progBlocks.append(leaf)
    progBlocks.reverse()
    node = Node("ProgNode", progBlocks)
    for child in progBlocks:
        child.setParent(node)
    semantic.pop()
    semantic.append(node)

# This is the lookup table which dictates what to do upon seeing a certain symbol on the stack
table = {"ADDOP": {"minus": ["minus"], "plus": ["plus"], "or": ["or"]},
         "APARAMS": {"rpar":["epsilon"], "lpar":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "id":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "minus":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "plus":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "not":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "floatlit":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"], "intlit":[createLeafEpsilon, "EXPR", createExprNode, "REPTAPARAMS1"]},
         "APARAMSTAIL": {"comma":["comma", createLeafEpsilon, "EXPR", createExprNode,]},
         "ARITHEXPR": {"lpar": ["TERM", "RIGHTRECARITHEXPR"], "id":["TERM", "RIGHTRECARITHEXPR"], "minus":["TERM", "RIGHTRECARITHEXPR"], "plus":["TERM", "RIGHTRECARITHEXPR"], "not":["TERM", "RIGHTRECARITHEXPR"], "floatlit":["TERM", "RIGHTRECARITHEXPR"], "intlit":["TERM", "RIGHTRECARITHEXPR"]},
         "ARRAYSIZE": {"lsqbr": ["lsqbr", createLeafEpsilon, "ENDBR"]},
         "ASSIGNOP": {"equal": ["equal"]},
         "ENDBR": {"rsqbr": [createLeafDim, "rsqbr"], "intlit": ["intlit", createLeaf, createLeafDim, "rsqbr"]},
         "EXPR": {"lpar": ["ARITHEXPR", "RELEXPREND"], "id": ["ARITHEXPR", "RELEXPREND"], "minus": ["ARITHEXPR", "RELEXPREND"], "plus": ["ARITHEXPR", "RELEXPREND"], "not": ["ARITHEXPR", "RELEXPREND"], "floatlit": ["ARITHEXPR", "RELEXPREND"], "intlit": ["ARITHEXPR", "RELEXPREND"]},
         "FACTOR": {"lpar": ["lpar", createLeafEpsilon, "ARITHEXPR", createFuncArgNode, "rpar"], "id":["id", createLeaf, "VARORFUNC", "REPTFACTOR2"], "minus": ["SIGN", createLeafSign, "FACTOR", createSignedNode], "plus": ["SIGN", createLeafSign, "FACTOR", createSignedNode], "not": ["not", "FACTOR"], "floatlit": ["floatlit", createLeaf], "intlit": ["intlit", createLeaf]},
         "FPARAMS": {"rpar": ["epsilon"], "id": ["id", createLeaf, "colon", "TYPE", createLeafType, "REPTFPARAMS3", createDimNode, createVardeclNode, "REPTFPARAMS4"]},
         "FPARAMSTAIL": {"comma": ["comma", "id", createLeaf, "colon", "TYPE", createLeafType, "REPTFPARAMSTAIL4", createDimNode]},
         "FUNCBODY": {"lcurbr": ["lcurbr", createLeafEpsilon, "REPTFUNCBODY1", createFuncBodyNode, "rcurbr"]},
         "FUNCDECL": {"func": ["FUNCHEAD", "semi"]},
         "FUNCDEF": {"func": ["FUNCHEAD", "FUNCBODY"]},
         "FUNCHEAD": {"func": ["func", "id", createLeaf, "lpar", "FPARAMS", createParamListNode, "rpar", "arrow", "RETURNTYPE", createLeafType, createFuncDefNode]},
         "IDNEST": {"dot": ["dot", "id", createLeaf, createAttributeNode, "VARORFUNC"]},
         "IMPLDEF": {"impl" : ["impl", "id", createLeaf, createImplDefNode, "lcurbr", createLeafEpsilon, "REPTIMPLDEF3", createImplBodyNode, "rcurbr"]},
         "INDICE": {"lsqbr": ["lsqbr", "ARITHEXPR", createIndiceNode, "rsqbr"]},
         "MEMBERDECL": {"let": ["VARDECL"], "func": ["FUNCDECL"]},
         "MULTOP": {"and": ["and"], "div": ["div"], "mult": ["mult"]},
         "OPTSTRUCTDECL2": {"lcurbr": ["epsilon"], "inherits": ["inherits", "id", createLeaf, "REPTOPTSTRUCTDECL22"]},
         "PROG": {"struct": ["REPTPROG0"], "impl": ["REPTPROG0"], "func": ["REPTPROG0"]},
         "RELEXPR": {"lpar": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "id": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "minus": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "plus": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "not": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "floatlit": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode], "intlit": ["ARITHEXPR", "RELOP", "ARITHEXPR", createConditionNode]},
         "RELEXPREND": {"rpar": ["epsilon"], "semi": ["epsilon"], "comma": ["epsilon"], "geq": ["RELOP" "ARITHEXPR"], "leq": ["RELOP" "ARITHEXPR"], "gt": ["RELOP" "ARITHEXPR"], "lt": ["RELOP" "ARITHEXPR"], "neq": ["RELOP" "ARITHEXPR"], "eq": ["RELOP" "ARITHEXPR"]},
         "RELOP": {"geq": ["geq"], "leq": ["leq"], "gt": ["gt"], "lt": ["lt"], "neq": ["neq"], "eq": ["eq"]},
         "REPTAPARAMS1": {"rpar": ["epsilon"], "comma": ["APARAMSTAIL", "REPTAPARAMS1"]},
         "REPTFACTOR2": {"rpar": ["epsilon"], "dot": ["IDNEST", "REPTFACTOR2"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["epsilon"], "div": ["epsilon"], "mult": ["epsilon"], "rsqbr": ["epsilon"], "or": ["epsilon"]},
         "REPTFPARAMS3": {"rpar": ["epsilon"], "comma": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTFPARAMS3"]},
         "REPTFPARAMS4": {"rpar": ["epsilon"], "comma": ["FPARAMSTAIL", createVardeclNode, "REPTFPARAMS4"]},
         "REPTFPARAMSTAIL4": {"rpar": ["epsilon"], "comma": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTFPARAMSTAIL4"]},
         "REPTFUNCBODY1": {"id": ["VARDECLORSTAT", "REPTFUNCBODY1"], "let": ["VARDECLORSTAT", "REPTFUNCBODY1"], "rcurbr": ["epsilon"], "return": ["VARDECLORSTAT", "REPTFUNCBODY1"], "write": ["VARDECLORSTAT", "REPTFUNCBODY1"], "read": ["VARDECLORSTAT", "REPTFUNCBODY1"], "while": ["VARDECLORSTAT", "REPTFUNCBODY1"], "if": ["VARDECLORSTAT", "REPTFUNCBODY1"]},
         "REPTIMPLDEF3": {"rcurbr": ["epsilon"], "func": ["FUNCDEF", "REPTIMPLDEF3"]},
         "REPTOPTSTRUCTDECL22": {"lcurbr": ["epsilon"], "comma": ["comma", "id", createLeaf, "REPTOPTSTRUCTDECL22"]},
         "REPTPROG0": {"struct": ["STRUCTORIMPLORFUNC", "REPTPROG0"], "impl": ["STRUCTORIMPLORFUNC", "REPTPROG0"], "func": ["STRUCTORIMPLORFUNC", "REPTPROG0"]},
         "REPTSTATBLOCK1": {"id": ["STATEMENT", "REPTSTATBLOCK1"], "rcurbr": ["epsilon"], "return": ["STATEMENT", "REPTSTATBLOCK1"], "write": ["STATEMENT", "REPTSTATBLOCK1"], "read": ["STATEMENT", "REPTSTATBLOCK1"], "while": ["STATEMENT", "REPTSTATBLOCK1"], "if": ["STATEMENT", "REPTSTATBLOCK1"]},
         "REPTSTATEFUNC": {"dot": ["dot", "STATESTART"], "semi": ["epsilon"]},
         "REPTSTATEVAR": {"dot": ["dot", "STATESTART"], "equal":["ASSIGNOP", createLeafEpsilon, "EXPR", createExprNode, createAssignNode]},
         "REPTSTATEVARORFUNC0": {"dot": ["epsilon"], "lsqbr": ["INDICE", "REPTSTATEVARORFUNC0"], "equal": ["epsilon"]},
         "REPTSTRUCTDECL4": {"private": ["VISIBILITY", createLeafVisibility, "MEMBERDECL", createStructDeclNode, "REPTSTRUCTDECL4"], "public": ["VISIBILITY", createLeafVisibility, "MEMBERDECL", createStructDeclNode, "REPTSTRUCTDECL4"], "rcurbr": ["epsilon"]},
         "REPTVARDECL4": {"semi": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTVARDECL4"]},
         "REPTVARIABLE": {"rpar": ["epsilon"], "dot": ["VARIDNEST", "REPTVARIABLE"]},
         "REPTVARIABLE20": {"rpar": ["epsilon"], "dot": ["epsilon"], "lsqbr": ["INDICE", "REPTVARIABLE20"]},
         "REPTVARIDNEST20": {"rpar": ["epsilon"], "dot": ["epsilon"], "lsqbr": ["INDICE", "REPTVARIDNEST20"]},
         "REPTVARORFUNC0": {"rpar": ["epsilon"], "dot": ["epsilon"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["epsilon"], "div": ["epsilon"], "mult": ["epsilon"], "rsqbr": ["epsilon"], "lsqbr": ["INDICE", "REPTVARORFUNC0"], "or": ["epsilon"]},
         "RETURNTYPE": {"id": ["TYPE"], "float": ["TYPE"], "integer": ["TYPE"], "void": ["void"]},
         "RIGHTRECARITHEXPR": {"rpar": ["epsilon"], "semi": ["epsilon"], "minus": ["ADDOP", "TERM", createAddNode, "RIGHTRECARITHEXPR"], "plus": ["ADDOP", "TERM", createAddNode, "RIGHTRECARITHEXPR"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "rsqbr": ["epsilon"], "or": ["ADDOP", "TERM", createOrNode, "RIGHTRECARITHEXPR"]},
         "RIGHTRECTERM": {"rpar": ["epsilon"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["MULTOP", "FACTOR", createAndNode, "RIGHTRECTERM"], "div": ["MULTOP", "FACTOR", createMultNode, "RIGHTRECTERM"], "mult": ["MULTOP", "FACTOR", createMultNode, "RIGHTRECTERM"], "rsqbr": ["epsilon"], "or": ["epsilon"]},
         "SIGN": {"minus": ["minus"], "plus": ["plus"]},
         "START": {"struct": [createLeafEpsilon, "PROG", createProgNode], "impl": [createLeafEpsilon, "PROG", createProgNode], "func": [createLeafEpsilon, "PROG", createProgNode]},
         "STATBLOCK": {"id": ["STATEMENT"], "semi": ["epsilon"], "lcurbr": ["lcurbr", "REPTSTATBLOCK1", "rcurbr"], "return": ["STATEMENT"], "write": ["STATEMENT"], "read": ["STATEMENT"], "while": ["STATEMENT"], "else": ["epsilon"], "if": ["STATEMENT"]},
         "STATEMENT": {"id": ["STATESTART", "semi"], "return": ["return", "lpar", createLeafEpsilon, "EXPR", createExprNode, createReturnNode, "rpar", "semi"], "write": ["write", "lpar", createLeafEpsilon, "EXPR", createExprNode, createWriteNode, "rpar", "semi"], "read": ["read", "lpar", "VARIABLE", createReadNode, "rpar", "semi"], "while": ["while", "lpar", "RELEXPR", createWhileNode, "rpar", createLeafEpsilon, "STATBLOCK", createWhileBlockNode, "semi"], "if": ["if", "lpar", "RELEXPR", createIfNode, "rpar", "then", createLeafEpsilon, "STATBLOCK", createThenNode, "else", createLeafEpsilon, "STATBLOCK", createElseNode, "semi"]},
         "STATESTART": {"id": ["id", createLeaf, createAttributeNode, "STATEVARORFUNC"]},
         "STATEVARORFUNC": {"lpar": ["lpar", createLeafEpsilon, "APARAMS", createFuncParamList, "rpar", "REPTSTATEFUNC"], "dot": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"], "lsqbr": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"], "equal": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"]},
         "STRUCTDECL": {"struct": ["struct", "id", createLeaf, createLeafEpsilon, "OPTSTRUCTDECL2", createInheritsNode, createStructDefNode, createLeafEpsilon, "lcurbr", "REPTSTRUCTDECL4", createStructBodyNode, "rcurbr", "semi"]},
         "STRUCTORIMPLORFUNC": {"struct": ["STRUCTDECL"], "impl": ["IMPLDEF"], "func": ["FUNCDEF"]},
         "TERM": {"lpar": ["FACTOR", "RIGHTRECTERM"], "id": ["FACTOR", "RIGHTRECTERM"], "minus": ["FACTOR", "RIGHTRECTERM"], "plus": ["FACTOR", "RIGHTRECTERM"], "not": ["FACTOR", "RIGHTRECTERM"], "floatlit": ["FACTOR", "RIGHTRECTERM"], "intlit": ["FACTOR", "RIGHTRECTERM"]},
         "TYPE": {"id": ["id"], "float": ["float"], "integer": ["integer"]},
         "VARDECL": {"let": ["let", "id", createLeaf, "colon", "TYPE", createLeafType, "REPTVARDECL4", createDimNode, createVardeclNode, "semi"]},
         "VARDECLORSTAT": {"id": ["STATEMENT"], "let":["VARDECL"], "return": ["STATEMENT"], "write": ["STATEMENT"], "read": ["STATEMENT"], "while": ["STATEMENT"], "if": ["STATEMENT"]},
         "VARIABLE": {"id": ["id", createLeaf, "VARIABLE2"]},
         "VARIABLE2": {"rpar": ["REPTVARIABLE20", "REPTVARIABLE"], "lpar": ["lpar", createLeafEpsilon, "APARAMS", createFuncParamList, "rpar", "VARIDNEST"], "dot": ["REPTVARIABLE20", "REPTVARIABLE"], "lsqbr": ["REPTVARIABLE20", "REPTVARIABLE"]},
         "VARIDNEST": {"dot": ["dot", "id", createLeaf, createAttributeNode, "VARIDNEST2"]},
         "VARIDNEST2": {"rpar": ["REPTVARIDNEST20"], "lpar": ["lpar", createLeafEpsilon, "APARAMS", createFuncParamList, "rpar", "VARIDNEST"], "dot": ["REPTVARIABLE20", "REPTVARIABLE"], "lsqbr": ["REPTVARIDNEST20"]},
         "VARORFUNC": {"rpar": ["REPTVARORFUNC0"], "lpar": ["lpar", createLeafEpsilon, "APARAMS", createFuncParamList, "rpar"], "dot": ["REPTVARORFUNC0"], "semi": ["REPTVARORFUNC0"], "minus": ["REPTVARORFUNC0"], "plus": ["REPTVARORFUNC0"], "comma": ["REPTVARORFUNC0"], "geq": ["REPTVARORFUNC0"], "leq": ["REPTVARORFUNC0"], "gt": ["REPTVARORFUNC0"], "lt": ["REPTVARORFUNC0"], "neq": ["REPTVARORFUNC0"], "eq": ["REPTVARORFUNC0"], "and": ["REPTVARORFUNC0"], "div": ["REPTVARORFUNC0"], "mult": ["REPTVARORFUNC0"], "rsqbr": ["REPTVARORFUNC0"], "lsqbr": ["REPTVARORFUNC0"], "or": ["REPTVARORFUNC0"]},
         "VISIBILITY": {"private": ["private"], "public": ["public"]}}

# First sets used to recover from errors
first = {"ADDOP": ["plus", "minus", "or"],
         "ENDBR": ["intlit", "rsqbr"],
         "FUNCBODY": ["lcurbr"],
         "FUNCHEAD": ["func"],
         "FPARAMS": ["id"],
         "FUNCDECL":["func"],
         "RELEXPREND": ["eq", "neq", "lt", "gt", "leq", "geq"],
         "ARITHEXPR": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "RELOP": ["eq", "neq", "lt", "gt", "leq", "geq"],
         "APARAMSTAIL": ["comma"],
         "REPTAPARAMS1": ["comma"],
         "IDNEST": ["dot"],
         "REPTFACTOR2": ["dot"],
         "REPTFPARAMS3": ["lsqbr"],
         "FPARAMSTAIL": ["comma"],
         "REPTFPARAMS4": ["comma"],
         "REPTFPARAMSTAIL4": ["lsqbr"],
         "REPTFUNCBODY1": ["let", "if", "while", "read", "write", "return", "id"],
         "REPTIMPLDEF3": ["func"],
         "REPTOPTSTRUCTDECL22": ["comma"],
         "REPTPROG0": ["struct", "impl", "func"],
         "ASSIGNOP": ["equal"],
         "MEMBERDECL": ["let", "func"],
         "ARRAYSIZE": ["lsqbr"],
         "INDICE": ["lsqbr"],
         "RETURNTYPE": ["void", "integer", "float", "id"],
         "RIGHTRECARITHEXPR": ["plus", "minus", "or"],
         "MULTOP": ["mult", "div", "and"],
         "SIGN": ["plus", "minus"],
         "START": ["struct", "impl", "func"],
         "PROG": ["struct", "impl", "func"],
         "REPTSTATBLOCK1": ["if", "while", "read", "write", "return", "id"],
         "RELEXPR": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "STATBLOCK": ["lcurbr", "if", "while", "read", "write", "return", "id"],
         "EXPR": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "STATESTART": ["id"],
         "STATEVARORFUNC": ["lpar", "lsqbr", "equal", "dot"],
         "REPTSTATEVARORFUNC0": ["lsqbr"],
         "REPTSTATEVAR": ["equal", "dot"],
         "REPTSTATEFUNC": ["dot"],
         "OPTSTRUCTDECL2": ["inherits"],
         "REPTSTRUCTDECL4": ["public", "private"],
         "STRUCTORIMPLORFUNC": ["struct", "impl", "func"],
         "STRUCTDECL": ["struct"],
         "IMPLDEF": ["impl"],
         "FUNCDEF": ["func"],
         "TERM": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "FACTOR": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "RIGHTRECTERM": ["mult", "div", "and"],
         "TYPE": ["integer", "float", "id"],
         "REPTVARDECL4": ["lsqbr"],
         "VARDECLORSTAT": ["let", "if", "while", "read", "write", "return", "id"],
         "VARDECL": ["let"],
         "STATEMENT": ["if", "while", "read", "write", "return", "id"],
         "VARIABLE": ["id"],
         "VARIABLE2": ["lpar", "lsqbr", "dot"],
         "REPTVARIABLE20": ["lsqbr"],
         "REPTVARIABLE": ["dot"],
         "VARIDNEST2": ["lpar", "lsqbr"],
         "REPTVARIDNEST20": ["lsqbr"],
         "VARIDNEST": ["dot"],
         "VARORFUNC": ["lpar", "lsqbr"],
         "REPTVARORFUNC0": ["lsqbr"],
         "APARAMS": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
         "VISIBILITY": ["public", "private"],
         "private": ["private"],
         "public": ["public"],
         "rpar": ["rpar"],
         "lpar": ["lpar"],
         "id": ["id"],
         "dot": ["dot"],
         "semi": ["semi"],
         "colon	": ["colon"],
         "let": ["let"],
         "float": ["float"],
         "integer": ["integer"],
         "rcurbr": ["rcurbr"],
         "lcurbr": ["lcurbr"],
         "struct": ["struct"],
         "return": ["return"],
         "write": ["write"],
         "read": ["read"],
         "while": ["while"],
         "else": ["else"],
         "then": ["then"],
         "if": ["if"],
         "minus": ["minus"],
         "plus": ["plus"],
         "void": ["void"],
         "comma": ["comma"],
         "geq": ["geq"],
         "leq": ["leq"],
         "gt": ["gt"],
         "lt": ["lt"],
         "neq": ["neq"],
         "eq": ["eq"],
         "inherits": ["inherits"],
         "and": ["and"],
         "div": ["div"],
         "mult": ["mult"],
         "rsqbr": ["rsqbr"],
         "lsqbr": ["lsqbr"],
         "impl": ["impl"],
         "arrow	": ["arrow"],
         "func": ["func"],
         "not": ["not"],
         "floatlit": ["floatlit"],
         "intlit": ["intlit"],
         "intnum": ["intnum"],
         "equal": ["equal"],
         "or": ["or"]}

# Follow sets used to recover from errors
follow = {"ADDOP": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
          "ENDBR": ["semi", "lsqbr", "rpar", "comma"],
          "FUNCBODY": ["struct", "impl", "func", "rcurbr"],
          "FUNCHEAD": ["semi", "lcurbr"],
          "FPARAMS": ["rpar"],
          "FUNCDECL":["rcurbr", "public", "private"],
          "RELEXPREND": ["semi", "comma", "rpar"],
          "ARITHEXPR": ["semi", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "comma", "rpar"],
          "RELOP": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
          "APARAMSTAIL": ["rpar", "comma"],
          "REPTAPARAMS1": ["comma"],
          "IDNEST": ["semi", "mult", "div", "and", "dot", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],	
          "REPTFACTOR2": ["semi", "mult", "div", "and", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "REPTFPARAMS3": ["rpar", "comma"],
          "FPARAMSTAIL": ["comma", "rpar"],
          "REPTFPARAMS4": ["rpar"],
          "REPTFPARAMSTAIL4": ["comma", "rpar"],
          "REPTFUNCBODY1": ["rcurbr"],
          "REPTIMPLDEF3": ["rcurbr"],
          "REPTOPTSTRUCTDECL22": ["lcurbr"],
          "REPTPROG0": [],
          "ASSIGNOP": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
          "MEMBERDECL": ["rcurbr", "public", "private"],
          "ARRAYSIZE": ["semi lsqbr rpar co"],
          "INDICE": ["equal", "semi", "mult", "div", "and", "lsqbr", "dot", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "RETURNTYPE": ["semi", "lcurbr"],
          "RIGHTRECARITHEXPR": ["semi", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "comma", "rpar"],
          "MULTOP": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
          "SIGN": ["id", "intlit", "floatlit", "lpar", "not", "plus", "minus"],
          "START": [],
          "PROG": [],
          "REPTSTATBLOCK1": ["rcurbr"],
          "RELEXPR": ["rpar"],
          "STATBLOCK": ["else", "semi"],
          "EXPR": ["semi", "comma", "rpar"],
          "STATESTART": ["semi"],
          "STATEVARORFUNC": ["semi"],
          "REPTSTATEVARORFUNC0": ["equal", "dot"],
          "REPTSTATEVAR": ["semi"],
          "REPTSTATEFUNC": ["semi"],
          "OPTSTRUCTDECL2": ["lcurbr"],
          "REPTSTRUCTDECL4": ["rcurbr"],
          "STRUCTORIMPLORFUNC": ["struct", "impl", "func"],
          "STRUCTDECL": ["struct", "impl", "func"],
          "IMPLDEF": ["struct", "impl", "func"],
          "FUNCDEF": ["struct", "impl", "func", "rcurbr"],
          "TERM": ["semi", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "FACTOR": ["semi", "mult", "div", "and", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "RIGHTRECTERM": ["semi", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "TYPE": ["rpar", "lcurbr", "comma", "lsqbr", "semi"],
          "REPTVARDECL4": ["semi"],
          "VARDECLORSTAT": ["let", "if", "while", "read", "write", "return", "id", "rcurbr"],
          "VARDECL": ["public", "private", "let", "if", "while", "read", "write", "return", "id", "rcurbr"],
          "STATEMENT": ["else", "semi", "let", "if", "while", "read", "write", "return", "id", "rcurbr"],
          "VARIABLE": ["rpar"],
          "VARIABLE2": ["rpar"],
          "REPTVARIABLE20": ["rpar", "dot"],
          "REPTVARIABLE": ["rpar"],
          "VARIDNEST2": ["rpar", "dot"],
          "REPTVARIDNEST20": ["rpar", "dot"],
          "VARIDNEST": ["rpar", "dot"],
          "VARORFUNC": ["semi", "mult", "div", "and", "dot", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "REPTVARORFUNC0": ["semi", "mult", "div", "and", "dot", "rsqbr", "eq", "neq", "lt", "gt", "leq", "geq", "plus", "minus", "or", "comma", "rpar"],
          "APARAMS": ["rpar"],
          "VISIBILITY": ["let", "func"],
          "private": [],
         "public": [],
         "rpar": [],
         "lpar": [],
         "id": [],
         "dot": [],
         "semi": [],
         "colon	": [],
         "let": [],
         "float": [],
         "integer": [],
         "rcurbr": [],
         "lcurbr": [],
         "struct": [],
         "return": [],
         "write": [],
         "read": [],
         "while": [],
         "else": [],
         "then": [],
         "if": [],
         "minus": [],
         "plus": [],
         "void": [],
         "comma": [],
         "geq": [],
         "leq": [],
         "gt": [],
         "lt": [],
         "neq": [],
         "eq": [],
         "inherits": [],
         "and": [],
         "div": [],
         "mult": [],
         "rsqbr": [],
         "lsqbr": [],
         "impl": [],
         "arrow	": [],
         "func": [],
         "not": [],
         "floatlit": [],
         "intlit": [],
         "intnum": [],
         "equal": [],
         "or": []}

# List of all productions used to determine if on top of the stack is a production or a character
productions = ["ADDOP", "ENDBR", "FUNCBODY", "FUNCHEAD", "FPARAMS", "FUNCDECL", "RELEXPREND", "ARITHEXPR", "RELOP", "APARAMSTAIL", "REPTAPARAMS1", 
               "IDNEST", "REPTFACTOR2", "REPTFPARAMS3", "FPARAMSTAIL", "REPTFPARAMS4", "REPTFPARAMSTAIL4", "REPTFUNCBODY1", "REPTIMPLDEF3", 
               "REPTOPTSTRUCTDECL22", "REPTPROG0", "ASSIGNOP", "MEMBERDECL", "ARRAYSIZE", "INDICE", "RETURNTYPE", "RIGHTRECARITHEXPR", "MULTOP",
               "SIGN", "START", "PROG", "REPTSTATBLOCK1", "RELEXPR", "STATBLOCK", "EXPR", "STATESTART", "STATEVARORFUNC", "REPTSTATEVARORFUNC0",
               "REPTSTATEVAR", "REPTSTATEFUNC", "OPTSTRUCTDECL2", "REPTSTRUCTDECL4", "STRUCTORIMPLORFUNC", "STRUCTDECL", "IMPLDEF", "FUNCDEF",
               "TERM", "FACTOR", "RIGHTRECTERM","TYPE", "REPTVARDECL4", "VARDECLORSTAT", "VARDECL", "STATEMENT", "VARIABLE", "VARIABLE2",
               "REPTVARIABLE20", "REPTVARIABLE", "VARIDNEST2", "REPTVARIDNEST20", "VARIDNEST", "VARORFUNC", "REPTVARORFUNC0", "APARAMS", "VISIBILITY"]

# List of nullable productions
nullable = ["APARAMS", "FPARAMS", "OPTSTRUCTDECL2", "PROG", "RELEXPREND", "REPTAPARAMS1", "REPTFACTOR2", "REPTFPARAMS3", "REPTFPARAMS4", "REPTFPARAMSTAIL4",
            "REPTFUNCBODY1", "REPTIMPLDEF3", "REPTOPTSTRUCTDECL22", "REPTPROG0", "REPTSTATBLOCK1", "REPTSTATEFUNC", "REPTSTATEVARORFUNC0",
            "REPTSTRUCTDECL4", "REPTVARDECL4", "REPTVARIABLE", "REPTVARIABLE20", "REPTVARIDNEST20", "REPTVARORFUNC0", "RIGHTRECARITHEXPR",
            "RIGHTRECTERM", "START", "STATBLOCK", "VARIABLE2", "VARIDNEST2", "VARORFUNC"]

# Used to translate chracters into their symbol for error output
characters = {"private":"private", "public":"public", "rpar":")", "lpar":"(", "id":"id", "dot":".",	"semi":";",	"colon":":", "let":"let",
              "float":"float", "integer":"interger", "rcurbr":"}", "lcurbr":"{", "struct":"struct",	"return":"return", "write":"write","read":"read",
              "while":"while", "else":"else", "then":"then", "comma":",", "geq":">=", "leq":"<=", "gt":">", "lt":"<", "neq":"<>","eq":"==", 
              "inherits":"inherits", "and":"and", "div":"div", "mult":"mult", "if":"if", "minus":"minus", "plus":"+", "void":"void", "rsqbr":"]",
              "lsqbr":"[",	"impl":"impl", "arrow":"->", "func":"func", "not":"not", "floatlit":"floatlit",	"intlit":"intlit", "intnum":"intnum", 
              "equal":"equal", "or":"or"}

"""
Function will attempt to parse the passed lexicon using the stack
passedLexicon: queue which contains the tokens to process
filename: name to give to the output files
"""      
def parseToken(passedLexicon, filename):
    
    # Names of the output and error files created by the compiler
    parserProductions = f"{filename}.outderivation"
    parserErrors = f"{filename}.outsyntaxerrors"
    parserReconstruction = f"{filename}.outparsedtext"

    # If file does not exist, create it, otherwise overwrite the old one
    if not os.path.exists(parserProductions):
        g = open(parserProductions, "x")
    else:
        g = open(parserProductions, "w")
  
    if not os.path.exists(parserErrors):
        file = open(parserErrors, "x")
    else:
        file = open(parserErrors, "w")
        
    if not os.path.exists(parserReconstruction):
        h = open(parserReconstruction, "x")
    else:
        h = open(parserReconstruction, "w")
        
    parsedContent = ""
    
    # Global variables to allow usage during error recovery
    global lexicon
    lexicon = passedLexicon
    
    global stack

    # Initialize the stack used by the parser    
    stack = deque()
    stack.append("$")
    stack.append("START")
    
    lexeme = None
    
    global errorFile
    errorFile = file
    
    # Used to reconstructed the parsed output
    line = 1
    col = 1
    
    # Used to hold the value of the production that will be placed on the stack before the stack is popped
    nextProduction = ""
    
    # While there is still content in the lexicon
    while len(lexicon) >= 1:
        
        # This is used for sematics
        previousLexeme = lexeme
        
        # Progress lexicon by removing the top of the queue
        lexeme = lexicon.popleft()
        while 1:
            
            # While the top of the stack is a production and not a character
            while list(set([stack[-1]]) & set(productions)) != []:
                
                # Indicates that the top of the stack is a dictionary and not a list (i.e. still going down the chain of productions)
                if isinstance(table[stack[-1]], dict):
                    
                    if lexeme == None:
                        break
                    
                    # If the current lexeme is expected among the keys in the parsing table
                    if lexeme[1] in table[stack[-1]].keys():

                        # Print the current stack and then the modifications done by fufulling the production
                        print(stack, file=g)
                        print(f"{stack[-1]} --> {table[stack[-1]][lexeme[1]]}", file=g)

                        # Get the production before removing it from the stack
                        nextProduction = table[stack[-1]][lexeme[1]]
                        stack.pop()

                        # Push contents of the result of the production onto the stack, reversed so that the order remains correct for the stack
                        for production in reversed(nextProduction):
                            stack.append(production)

                    # Else this means its an error and move to error recovery    
                    else:
                        recoveryLexeme = skipErrors(lexeme)
                        if recoveryLexeme != "":
                            lexeme = recoveryLexeme

            # If the top of the stack contains epsilon            
            if stack[-1] == "epsilon":

                # Keep removing epsilons while transcribing to the file that the epsilons have been removed
                while stack[-1] == "epsilon":
                    print(stack, file=g)
                    print(f"{stack[-1]} --> epsilon", file=g)
                    stack.pop()
                continue
            
            # If the top of the stack is a callable function either create the leaf of the specific lexeme or run the function
            if callable(stack[-1]):
                if stack[-1] == createLeaf:
                    createLeaf(previousLexeme[1], previousLexeme[2], previousLexeme[0])
                elif stack[-1] in [createLeafVisibility, createLeafType, createLeafDim, createLeafSign]:
                    stack[-1](previousLexeme[2], previousLexeme[0])
                else:
                    stack[-1]()
                stack.pop()
                continue
            
            if (lexeme == None):
                break
            
            # If the top of the stack contains the lexeme we currently have, we have a match, print production to derivation file
            elif lexeme[1] == stack[-1]:
                print(stack, file=g)
                print(f"{stack[-1]} --> {lexeme[1]}", file=g)
                
                # This is to reconstruct the parsed tokens as the original file and also prints to the derivation a working copy
                while line < lexeme[2]:
                    line += 1
                    col = 1
                    print("\n", file=h, end="")
                    parsedContent += "\n"
                while col < lexeme[3]:
                    col +=1
                    print(" ", file=h, end="")
                    parsedContent += " "
                print(lexeme[0], file=h, end="")
                parsedContent += f"{lexeme[0]}"
                col += len(lexeme[0])
                print(parsedContent, file=g)
                
                stack.pop()
                break
            
            # If the top of the stack is the EOF symbol then end here
            elif stack[-1] == "$":
                break
            
            # Otherwise we have a mismatch (top of the stack is not the same as the lexeme we have), so move to error recovery
            else:
                recoveryLexeme = skipErrors(lexeme)
                if recoveryLexeme != "":
                    lexeme = recoveryLexeme
    
    # Remove nullable productions from the stack on the way out, this should ideally clear everything other than the $ that the stack was initialized
    while list(set([stack[-1]]) & set(productions)) != []:
        if list(set([stack[-1]]) & set(nullable)) != []:
            stack.pop()
        else:
            break

    # This should always be the prog node that needs to finish before emptying the stack
    if callable(stack[-1]):
        stack[-1]()
        stack.pop()
    
    # If the stack only has the $ which was placed on it initially, then the file is sucessfully parsed
    if stack[-1] == "$":
        print("Compiled successfully")
    else:
        while len(stack) > 1:
            
            # Indicates that the top of the stack is a character
            if list(set([stack[-1]]) & set(productions)) == []:
                print(f"Syntax error at the end of the file. Expected \"{characters[stack[-1]]}\" before reaching the end of the file.", file=errorFile)
            stack.pop()

    # Open the AST file to write to or create it if necessary
    astPath = f"{filename}.ast.outast"

    if not os.path.exists(astPath):
        astFile = open(astPath, "x")
    else:
        astFile = open(astPath, "w")
        
    # Print the AST to the file
    for node in semantic:
        printNode(node, 0, astFile)
        
    # Open the symbol table file to write to or create it if necessary
    symbolTable = f"{filename}.outsymboltables"

    if not os.path.exists(symbolTable):
        symbolTableFile = open(symbolTable, "x")
    else:
        symbolTableFile = open(symbolTable, "w")
    
    for node in semantic:
        globalSymbolTable = generateSymbolTable(node)
    printSymbolTable(globalSymbolTable, symbolTableFile)
        
    # Open the generated code file to write to or create it if necessary
    generatedCode = f"{filename}.m"

    if not os.path.exists(generatedCode):
        generatedCodeFile = open(generatedCode, "x")
    else:
        generatedCodeFile = open(generatedCode, "w") 
        
    print("\t\t entry".ljust(23) + "% Start here", file=generatedCodeFile)
        
    moonCodeGenerator.allocateMemory(globalSymbolTable, generatedCodeFile)
        
    # Open the semantic error file to write to or create it if necessary
    semanticErrors = f"{filename}.outsemanticerrors"

    if not os.path.exists(semanticErrors):
        semanticErrorsFile = open(semanticErrors, "x")
    else:
        semanticErrorsFile = open(semanticErrors, "w")
    
    # Generate symbol table and check semantic rules
    for node in semantic:
        checkClasses(node, semanticErrorsFile, generatedCodeFile)
        
    astFile.close()
    symbolTableFile.close()
    semanticErrorsFile.close()
    g.close()
            
def skipErrors(lexeme):
    global stack
    global lexicon
    global errorFile
    
    # First determine if the parser was looking for a list of valid characters or just 1 character for prinitng format
    if list(set([stack[-1]]) & set(productions)) != []:
        expectedLexemes = ""
        keys = list(table[stack[-1]].keys())
        for symbol in keys[:-1]:
            expectedLexemes += f"\"{characters[symbol]}\", "
        expectedLexemes += f"or \"{characters[keys[-1]]}\""
        print(f"Syntax error at row {lexeme[2]}, position {lexeme[3]}. Expected {expectedLexemes} but instead got \"{lexeme[0]}\".", file=errorFile)
    else:
        print(f"Syntax error at row {lexeme[2]}, position {lexeme[3]}. Expected \"{characters[stack[-1]]}\" but instead got \"{lexeme[0]}\".", file=errorFile)
    
    # As long as there are lexemes left in the file to process
    if (len(lexicon) != 0) or (isinstance(lexeme, list)):
        
        # Create a temp copy of the stack
        tempStack = stack.copy()
        
        # Remove all nullable productions
        while list(set([tempStack[-1]]) & set(nullable)) != []:
            tempStack.pop()
            
        # If you make it to the end of the file end it here
        if (tempStack[-1] == "$"):
            return ""
        
        # Look at the production under the top of the stack
        lookahead = tempStack[-2]
        
        # If that production is the last production or the current lexeme matches the follow set of it, pop the current top of the stack off
        if (lookahead == "$") or (lexeme[1] in follow[lookahead]):
            tempStack.pop()
            
            # Finilize changes by changing the original stack
            stack = tempStack
            return ""
        
        # Otherwise scan through the file for the right token
        else:
            nextLexeme = lexicon.popleft()
            lookahead = nextLexeme[1]
            while (lookahead not in first[stack[-1]]) and (first[stack[-1]] in nullable) and (lookahead not in follow[stack[-1]]):
                nextLexeme = lexicon.popleft()
                if len(lexicon) == 0:
                    return nextLexeme
            return nextLexeme

"""
Function that prints the AST to the file specified. It traverses the tree in a pre-order fashion recursively.
node: The root node of the tree
spaces: The number of spaces to additionally print for the offset, this should only ever be invoked originally with 0, the recursion will increment it
file: File to write to 
"""        
def printNode(node, spaces, file):
    for i in range(spaces):
        print("| ", end="", file=file)
    print(node.getNodeType(), file=file)
    if (isinstance(node, Node)) and (node.getChildren() != None):
        children = node.getChildren() if isinstance(node.getChildren(), list) else [node.getChildren()]
        for child in children:
            printNode(child, spaces+1, file)

def generateSymbolTable(root):
    tree = deque()
    tree.append(root)
    globalTable = Table("global")
    context = {}
    while tree:
        if isinstance(tree[-1], Node):
            if (tree[-1].getNodeType() == "StructDef"):
                children = tree[-1].getChildren()
                className = children[0].getValue()
                classTable = Table(className)
                globalTable.addClasses(classTable)
                if children[1].getChildren() == None:
                    classTable.addInherits("none")
                else:
                    for grandchild in children[1].getChildren():
                        classTable.addInherits(grandchild.getValue())
                tree.pop()
                for decl in tree[-1].getChildren():
                    visibility = decl.getChildren()[0].getValue()
                    name = decl.getChildren()[1].getChildren()[0].getValue()
                    returnType = decl.getChildren()[1].getChildren()[2].getValue()
                    if decl.getChildren()[1].getNodeType() == "FuncDef":
                        functionTable = Function(name, returnType, visibility)
                        context[className + "." +name + "." + returnType] = functionTable
                        classTable.addFunction(functionTable)
                        for var in decl.getChildren()[1].getChildren()[1].getChildren():
                            varName = var.getChildren()[0].getValue()
                            varType = var.getChildren()[1].getValue()
                            functionTable.addParam(varName, varType)
                    else:
                        type = decl.getChildren()[1].getChildren()[1].getValue()
                        classTable.addData(name, type, visibility)
                tree.pop()
                continue

            elif (tree[-1].getNodeType() == "ImplDef"):
                implName = tree[-1].getChildren().getValue()
                tree.pop()
                implStack = deque()
                implStack.extend(tree[-1].getChildren()[::-1])
                while implStack:
                    if (implStack[-1].getNodeType() == "FuncDef"):
                        implFuncName = implStack[-1].getChildren()[0].getValue()
                        implReturnType = implStack[-1].getChildren()[2].getValue()
                        for var in implStack[-1].getChildren()[1].getChildren():
                            varName = var.getChildren()[0].getValue()
                            varType = var.getChildren()[1].getValue()
                            if implName + "." + implFuncName + "." + implReturnType in context:
                                func = context[implName + "." + implFuncName + "." + implReturnType]
                                if (varName, varType) in func.getParam():
                                    # print("exists")
                                    # Filler code to show that I can tell if variables exist
                                    a = "a"
                        implStack.pop()
                        for nodes in implStack[-1].getChildren():
                            if nodes.getNodeType() == "VarDecl":
                                functionVarName = nodes.getChildren()[0].getValue()
                                functionVarType = nodes.getChildren()[1].getValue()
                                func.addLocal(functionVarName, functionVarType)
                        implStack.pop()
                    else:
                        implStack.pop()
                tree.pop()
                continue

            elif (tree[-1].getNodeType() == "FuncDef"):
                funcName = tree[-1].getChildren()[0].getValue()
                funcParamList = tree[-1].getChildren()[1]
                funcReturnType = tree[-1].getChildren()[2].getValue()
                globalFunc = Function(funcName, funcReturnType, "global")
                globalTable.addFunction(globalFunc)
                tree.pop()
                for nodes in tree[-1].getChildren():
                    if nodes.getNodeType() == "VarDecl":
                        functionVarName = nodes.getChildren()[0].getValue()
                        functionVarType = nodes.getChildren()[1].getValue()
                        globalFunc.addLocal(functionVarName, functionVarType)
                tree.pop()
                continue

            if tree[-1].getChildren() != None:
                children = tree[-1].getChildren() if isinstance(tree[-1].getChildren(), list) else [tree[-1].getChildren()]
                tree.pop()
                tree.extend(children[::-1])
        else:
            tree.pop()
    
    return globalTable
            
def printSymbolTable(globalTable, file):
        # This is the printing of the symbol table to the output file 
    depth = 0
    
    # Begin by printing the global table         
    printTableHeader(globalTable.getTableName(), depth, file)
    
    # Print the classes defined first
    for classes in globalTable.getClasses():
        depth = 0 
        
        # First print the class name and what classes it inherits
        printTableContents(["class", classes.getTableName()], depth, file)
        depth = 1
        printTableHeader(classes.getTableName(), depth, file)
        inherits = ", ".join(classes.getInherits()) if classes.getInherits() != [] else "none"
        printTableContents(["inherit", inherits], depth, file)
        
        # Print defined variables
        for data in classes.getData():
            printTableContents(["data", data[0], data[1], data[2]], depth, file)
            
        # Print the class functions
        for func in classes.getFunction():
            depth = 1
            
            # Concat to make the function arguments and then the function signiture
            functionArgs = ", ".join([x[1] for x in func.getParam()])
            functionSig = f"({functionArgs}): {func.getReturnType()}"
            printTableContents(["function", func.getFuncName(), functionSig, func.getVisibility()], depth, file)
            depth = 2
            
            # Print table for the function params and then local variables
            printTableHeader(f"{classes.getTableName()}::{func.getFuncName()}", depth, file)
            for param in func.getParam()[::-1]:
                printTableContents(["param", param[0], param[1]], depth, file)
            for local in func.getLocal():
                printTableContents(["local", local[0], local[1]], depth, file)
            printTableClose(depth, file)
        depth = 1
        printTableClose(depth, file)

    # Now print the functions defined in global
    for globalFunction in globalTable.getFunction():
        depth = 0
        
        # Concat to make the function arguments and then the function signiture
        functionArgs = ", ".join([x[1] for x in globalFunction.getParam()])
        functionSig = f"({functionArgs}): {globalFunction.getReturnType()}"
        printTableContents(["function", globalFunction.getFuncName(), functionSig], depth, file)
        depth = 1
        
        # Print table for the function and then local variables
        printTableHeader(f"::{globalFunction.getFuncName()}", depth, file)
        for local in globalFunction.getLocal():
            printTableContents(["local", local[0], local[1]], depth, file)
        printTableClose(depth, file)
    
    # Print the end of the table
    depth = 0
    printTableClose(depth, file)

"""
Function that prints the header of a table in the symbol table file
tableName = name to give the table
depth = offset to add to give the correct depth of the table when nested
file = symbol table file to print to
"""            
def printTableHeader(tableName, depth, file):
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)
    print("|    " * depth + "| table: " + tableName.ljust(74-depth*8) + "|" + "  |" * depth, file=file)
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)

"""
Function that prints the content of a table in the symbol table file, depending on the number of items given in content, the line layout changes
content = content to print to the table
depth = offset to add to give the correct depth of the table when nested
file = symbol table file to print to
"""       
def printTableContents(content, depth, file):
    if len(content) == 2:
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(69 - depth*8) + "|" + "  |" * depth, file=file)
        
    elif len(content) == 3:  
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(12) + "| " + content[2].ljust(55 - depth*8) + "|" + "  |" * depth, file=file)
        
    elif len(content) == 4:
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(12) + "| " + content[2].ljust(43 - depth*8) + "| " + content[3].ljust(10) + "|" +  "  |" * depth, file=file)

"""
Function that prints the bottom of a table in the symbol table file
depth = offset to add to give the correct depth of the table when nested
file = symbol table file to print to
"""   
def printTableClose(depth, file):
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)

"""
Function that will generate a symbol table and check semantic rules over the AST tree.
root = root node of the AST tree
file = file to print symbol table to
warning = file to print errors and warning to
"""            
def checkClasses(root, warning, codeOutput):
    
    # Going through the AST
    tree = deque()
    tree.append(root)
    
    # This is the object that will contain the global table and hence will contain the entire symbol table
    globalTable = Table("global")
    
    # Used for class inheritence
    inheritence = nx.DiGraph()
    
    # Used to make sure multiple cycles are not reprinted every time
    identifiedCylcles = []
    
    # Used to make sure all struct defined functions are defined by impl blocks
    context = {}
    
    # Used to keep track of functions defined by each class
    definedClasses = {}
    
    # Used to keep track of functions in the global section
    globalDefinedFunctions = {}
    
    # Used to keep track of the context in the global section
    freeContext = []
    
    # Used to keep track of errors/warnings to be printed at the end of this method
    semanticErrors = []
    
    # While the AST still contains nodes to process
    while tree:
        
        # Sanity check, but the tree should always contain a node at the top and not a free leaf
        if isinstance(tree[-1], Node):
            
            # Struct node processing, first the definition
            if (tree[-1].getNodeType() == "StructDef"):
                
                # Get information from the node
                children = tree[-1].getChildren()
                className = children[0].getValue()
                inheritsClasses = children[1].getChildren()
                inheritsLine = children[0].getLine()
                
                # Check the inherits for the struct
                if inheritsClasses != None:
                    
                    # If there is an inheriting class add it to the directed graph to keep track of parents
                    for inheriting in inheritsClasses:
                        inheritingName = inheriting.getValue()
                        inheritence.add_edge(inheritingName, className)
                    
                    # If a cycle has been discovered before, ensure that it is not reported twice
                    cyclesDiscovered = [x for x in sorted(nx.simple_cycles(inheritence)) if x not in [identifiedCylcles]]
                    
                    # Report if a new cycle is discovered and add it to the identified cycles list
                    if cyclesDiscovered != []:
                        for cycle in cyclesDiscovered:
                            identifiedCylcles.append(cycle)
                            stringCycle = " -> ".join(cycle)
                            semanticErrors.append((f"Semantic Error: circular class dependency (inheritence cycle) {stringCycle}", inheritsLine))
                
                # If the class name is defined already, skip processing the block and report the error
                if className in definedClasses:
                    semanticErrors.append((f"Semantic Error: multiple declared class {className}", children[0].getLine()))
                    tree.pop()
                    tree.pop()
                    continue
                
                # Initialize the entry in the definedClasses dictionary
                else:
                    definedClasses[className] = {}
                    
                # Create a table object for this class and begin adding details to it
                classTable = Table(className)
                globalTable.addClasses(classTable)
                if children[1].getChildren() == None:
                    classTable.addInherits("none")
                else:
                    for grandchild in children[1].getChildren():
                        classTable.addInherits(grandchild.getValue())
                
                # This concludes the struct def block process, move on to processing a struct body which needs to follow
                tree.pop()
                
                # Contains the locally defined variables
                localContext = []
                
                # For each statement in the struct body block
                for decl in tree[-1].getChildren():
                    
                    # Retieve information from the nodes, this is either a func definition or a var declaration
                    visibility = decl.getChildren()[0].getValue()
                    name = decl.getChildren()[1].getChildren()[0].getValue()
                    line = decl.getChildren()[1].getChildren()[0].getLine()
                    returnType = decl.getChildren()[1].getChildren()[2].getValue()
                    
                    # If its a func definition create the function object and 
                    if decl.getChildren()[1].getNodeType() == "FuncDef":
                        functionTable = Function(name, returnType, visibility)
                        
                        # If for some reason you have the exact same function defined in the same context (not coded due to time constraints)
                        if className + "." + name + "." + returnType in context:
                            continue
                        
                        # Add to local context as a defined function
                        else:
                            context[className + "." +name + "." + returnType] = (functionTable, line)
                            
                        # Add the function to the global table
                        classTable.addFunction(functionTable)
                        
                        # Process the variables in the function parameters
                        for var in decl.getChildren()[1].getChildren()[1].getChildren():
                            varName = var.getChildren()[0].getValue()
                            varType = var.getChildren()[1].getValue()
                            
                            # This gets the dimensions if one of the paramaters is an array
                            for dim in var.getChildren()[2].getChildren():
                                varType += dim.getValue()
                                
                            # Add param to the function object
                            functionTable.addParam(varName, varType)
                        
                        # If the function with the same name is present
                        if name in definedClasses[className]:
                            semanticErrors.append((f"Semantic Warning: overloaded member function {name}", line))
                            oldPair = definedClasses[className][name]
                            definedClasses[className][name] = [oldPair, (functionTable.getParam(), returnType)]
                        
                        # Else just add the function to the defined class dictionary under the current class
                        else:
                            definedClasses[className][name] = (functionTable.getParam(), returnType)
                        
                        # Look in parent classes by looking at other nodes in the graph, cut out the current class if its in the graph    
                        otherNodes = list(inheritence)
                        if className in otherNodes:
                            otherNodes.remove(className)
                        
                        # Check in the parent nodes (if it has a path to the current node its a parent) if a function is present
                        for graphNode in otherNodes:
                            if nx.has_path(inheritence, graphNode, className):
                                if graphNode in definedClasses:
                                    if name in definedClasses[graphNode]:
                                        
                                        # Ensure that the function has the correct number of params and the same types of parameters
                                        if definedClasses[graphNode][name][1] == returnType and len(definedClasses[graphNode][name][0]) == len(functionTable.getParam()):
                                            for i in range(len(definedClasses[graphNode][name][0])):
                                                if definedClasses[graphNode][name][0][i][1] != functionTable.getParam()[i][1]:
                                                    break
                                            semanticErrors.append((f"Semantic Warning: overridden parent {graphNode} function {name} in {className}", line))
                    
                    # This indicates its a variable declaration
                    else:
                        
                        # if the parameter is already declared in the local context
                        if name in localContext:
                            semanticErrors.append((f"Semantic Error: multiple declared data member {name} in {className}", line))
                            continue
                        else:
                            localContext.append(name)
                            
                        type = decl.getChildren()[1].getChildren()[1].getValue()
                        
                        # Check in parent classes if a variable with the same name exists
                        otherNodes = list(inheritence)
                        
                        # Remove current node from the node list
                        if className in otherNodes:
                            otherNodes.remove(className)
                        
                        # If the class is a parent and has a variable with the same definition
                        for graphNode in otherNodes:
                            if nx.has_path(inheritence, graphNode, className):
                                if graphNode in definedClasses:
                                    if name in definedClasses[graphNode]:
                                        semanticErrors.append((f"Semantic Warning: shadowed inherited data member {name}", line))
                        
                        # Add to the class definition dictionary and add as data to the table
                        definedClasses[className][name] = (type)
                        classTable.addData(name, type, visibility)
                
                # Process next block
                tree.pop()
                continue
            
            # Impl node processing, first the definition
            elif (tree[-1].getNodeType() == "ImplDef"):
                
                # The only thing in the impl definition is the name
                implName = tree[-1].getChildren().getValue()
                
                # Begin processing the impl block
                tree.pop()
                
                # Stack will contain the contents of the impl block
                implStack = deque()
                implStack.extend(tree[-1].getChildren()[::-1])
                
                # While there are nodes to process
                while implStack:
                    
                    # If the node is a function def
                    if (implStack[-1].getNodeType() == "FuncDef"):
                        
                        # Retrieve function information
                        implFuncName = implStack[-1].getChildren()[0].getValue()
                        implLine = implStack[-1].getChildren()[0].getLine()
                        implReturnType = implStack[-1].getChildren()[2].getValue()
                        
                        # Make sure that this function was defined already by a struct using the context and reteive the function object
                        if implName + "." + implFuncName + "." + implReturnType in context:
                            func = context.pop(implName + "." + implFuncName + "." + implReturnType)[0]
                            functionVariables = func.getParam()[:]
                        else:
                            semanticErrors.append((f"Semantic Error: undeclared member function {implName}.{implFuncName}", implLine))
                            implStack.pop()
                            implStack.pop()
                            continue
                        
                        # Process function parameters and ensure all the parameters are accounted for
                        for var in implStack[-1].getChildren()[1].getChildren():
                            varName = var.getChildren()[0].getValue()
                            varType = var.getChildren()[1].getValue()
                            if (varName, varType) in functionVariables:
                                functionVariables.remove((varName, varType))
                        
                        # Pop off the function definition and begin processing function body
                        implStack.pop()
                        
                        # Keep track of local variables defined in the block
                        implVariables = {}
                        for nodes in implStack[-1].getChildren():
                            
                            # Variable declaration node
                            if nodes.getNodeType() == "VarDecl":
                                
                                # Get information of the nodes
                                functionVarName = nodes.getChildren()[0].getValue()
                                functionVarType = nodes.getChildren()[1].getValue()
                                
                                # Ensures that dimensions will be properly copied
                                for dim in nodes.getChildren()[2].getChildren():
                                    functionVarType += dim.getValue()
                                
                                # Add local variable to function table
                                func.addLocal(functionVarName, functionVarType)
                                
                                # Check if this variable was defined already in the class
                                if functionVarName in definedClasses[implName]:
                                    semanticErrors.append((f"Semantic Warning: local variable {functionVarName} in a member function {implFuncName} shadows a data member of its own class", nodes.getChildren()[0].getLine()))
                                implVariables[functionVarName] = functionVarType
                            
                            # Assign variable node
                            if (nodes.getNodeType() == "AssignVar"):
                                nodeType = nodes.getChildren()[0].getNodeType()
                                
                                # Check the right side if its just a variable or something larger
                                if nodeType == "id":
                                    variable = nodes.getChildren()[0].getValue()
                                    nodeLine = nodes.getChildren()[0].getLine()
                                    if variable in implVariables:
                                        
                                        # This is missing the portion of the code that deals with single variable assignment due to time constraints
                                        assignement = nodes.getChildren()[1].getChildren()
                                    else:
                                        print("semantic error")
                                
                                # If its an attribute or indice we get the name of the variable and then the dimensions
                                elif nodeType in ["AttributeNode", "IndiceNode"]:
                                    variable = nodes.getChildren()[0].getChildren()[0].getValue()
                                    variableType = implVariables[variable]
                                    nodeLine = nodes.getChildren()[0].getChildren()[0].getLine()
                                    attribute = nodes.getChildren()[0].getChildren()[1].getValue()
                                    endType = definedClasses[variableType][attribute]
                                    assignement = nodes.getChildren()[1].getChildren()
                                    
                                    # If the expr node contains only a float or int
                                    if assignement[0].getNodeType() in ["intlit", "floatlit"]:
                                        
                                        # If the types dont match up
                                        if assignement[0].getNodeType()[:-3] != endType:
                                            semanticErrors.append((f"Semantic Error: type error in assignment statement", nodeLine))
                                            continue
                                        
                                    # This is missing the portion of the code that deals with ids due time constraints
                                    elif assignement[0].getNodeType() == "id":
                                        assignedVariable = assignement[0].getValue()
                                    
                                    # This makes it into a larger expresion node, so we decompose until we get leaves and evaluate there
                                    else:
                                        intermediateTypes = []
                                        
                                        # Set up a queue and put in the node
                                        operationQueue = deque()
                                        operationQueue.append(assignement)
                                        
                                        # While the queue still has objects
                                        while operationQueue:
                                            currentTop = operationQueue.popleft()
                                            
                                            # If the current node is a list of children
                                            if isinstance(currentTop, list):
                                                if isinstance(currentTop[0], Node):
                                                    if currentTop[0].getChildren() != None:
                                                        operationQueue.extend(currentTop[0].getChildren())
                                            # If the node has a single child
                                            elif isinstance(currentTop, Node):
                                                if currentTop.getChildren() != None:
                                                    operationQueue.extend(currentTop.getChildren())
                                            # If there are leaves on top just append
                                            else:
                                                intermediateTypes.append(currentTop)
                                        
                                        # Evaluate the types we collected from the leaves
                                        for intVarType in intermediateTypes:
                                            
                                            # If the value was a variable, retieve the type from the local context
                                            if intVarType.getValue() in implVariables:
                                                intVarType = implVariables[intVarType]
                                            
                                            # If it was a float or int 
                                            elif intVarType.getNodeType() in ["intlit", "floatlit"]:
                                                intVarType = intVarType.getNodeType()[:-3]
                                                if intVarType == "int":
                                                    intVarType = "integer"
                                            
                                            # If not found in the local context look to the class context
                                            else:
                                                functionParams = definedClasses[implName][implFuncName][0]
                                                for funcparam in functionParams:
                                                    if intVarType.getValue() == funcparam[0]:
                                                        intVarType = funcparam[1]
                                                if not isinstance(intVarType, str):
                                                    print("Error")
                                                    break
                                            
                                            # If a type doesnt match up there is a type error
                                            if intVarType != endType:
                                                semanticErrors.append((f"Seamntic Error: type error in expression", nodeLine))
                                                break
                            
                            # Return node processing                             
                            if nodes.getNodeType() == "ReturnNode":
                                
                                # Get node info
                                returnObject = nodes.getChildren().getChildren()[0].getValue()
                                returnObjectType = nodes.getChildren().getChildren()[0].getNodeType()[:-3]
                                returnLine = nodes.getChildren().getChildren()[0].getLine()
                                
                                # If the return type is not just a float or int
                                if returnObjectType not in ['int', 'float']:
                                    
                                    # Look for the variable in the local context
                                    if returnObject not in implVariables:
                                        semanticErrors.append((f"Semantic Error: retuning undefined variable {returnObject}", returnLine))
                                        break
                                    
                                    # If the variable is the wrong type
                                    elif implVariables[returnObject] != implReturnType:
                                        semanticErrors.append((f"Semantic Error: type error in return statement for {implFuncName}", returnLine))
                                        break
                                else:
                                    if returnObjectType == "int":
                                        returnObjectType = "integer"
                                        
                                    # if the float or int is the wrong thing to return
                                    if returnObjectType != implReturnType:
                                        semanticErrors.append((f"Semantic Error: type error in return statement for {implFuncName}", returnLine))
                                        break
                        
                        # Continue processing the stack
                        implStack.pop()
                    
                    # Pop if theres a func body on the top of the stack
                    else:
                        implStack.pop()
                
                # Process next block
                tree.pop()
                continue
            
            # Function block processing, global functions end up here + main
            elif (tree[-1].getNodeType() == "FuncDef"):
                
                # Define the local context
                localContext = {}
                
                # Retreive function information and add to table
                funcName = tree[-1].getChildren()[0].getValue()
                funcLine = tree[-1].getChildren()[0].getLine()
                funcReturnType = tree[-1].getChildren()[2].getValue()
                globalFunc = Function(funcName, funcReturnType, "global")
                funcParamList = tree[-1].getChildren()[1]
                functionVarName = ""
                stringParam = ""
                
                # Retrieve function parameters
                for var in funcParamList.getChildren()[::-1]:
                    functionVarName = var.getChildren()[0].getValue()
                    functionVarType = var.getChildren()[1].getValue()
                    for dim in var.getChildren()[2].getChildren():
                        functionVarType += dim.getValue()
                    stringParam += f"{functionVarType} {functionVarName}, "
                    
                    # Add to the symbol table and local context
                    globalFunc.addParam(functionVarName, functionVarType)
                    localContext[functionVarName] = functionVarType
                
                # If the function is defined in the free context already
                if f"{funcName}.{functionVarName}.{stringParam}" in freeContext:
                    semanticErrors.append((f"Semantic Error: multiple declared free function {funcName} {functionVarName}({stringParam[:-2]})", funcLine))
                    tree.pop()
                    continue
                else: 
                    freeContext.append(f"{funcName}.{functionVarName}.{stringParam}")
                    
                    # If the function is defined already
                    if funcName in globalDefinedFunctions:
                        semanticErrors.append((f"Semantic Warning: overloaded free function {funcName}", funcLine))
                        oldPair = globalDefinedFunctions[funcName]
                        globalDefinedFunctions[funcName] = [oldPair, (globalFunc.getParam(), funcReturnType)]
                    else:
                        globalDefinedFunctions[funcName] = (globalFunc.getParam(), funcReturnType)
                    globalTable.addFunction(globalFunc)
                    
                    # Now process the function body
                    tree.pop()
                calls = iter(tree[-1].getChildren())
                for nodes in calls:
                    
                    # Variable declaration processing
                    if nodes.getNodeType() == "VarDecl":
                        
                        # Get variables from the nodes
                        varName = nodes.getChildren()[0].getValue()
                        varLine = nodes.getChildren()[0].getLine()
                        varType = nodes.getChildren()[1].getValue()
                        
                        # If the type cannot be found in defined classes and is not just an int/float then its undefined
                        if varType not in definedClasses and varType not in ["integer", 'float']:
                            semanticErrors.append((f"Semantic Error: cannot create variable of undeclared class {varType}", varLine))
                            continue
                        
                        # Gets dimensions for the parameter
                        for dim in nodes.getChildren()[2].getChildren():
                            varType += dim.getValue()
                        
                        # If its already defined in the context
                        if varName in localContext:
                            semanticErrors.append((f"Semantic Error: multiple declared identifier {varName} in {funcName}", varLine))
                            continue
                        else:
                            localContext[varName] = varType
                        
                        # Add to table
                        globalFunc.addLocal(varName, varType)
                    
                    # Assignment node processing
                    if (nodes.getNodeType() == "AssignVar"):
                        nodeType = nodes.getChildren()[0].getNodeType()
                        
                        # Determine whats on the RHS and then get the correct data
                        if nodeType == "id":
                            variable = nodes.getChildren()[0].getValue()
                            nodeLine = nodes.getChildren()[0].getLine()
                        elif nodeType in ["AttributeNode", "IndiceNode"]:
                            variable = nodes.getChildren()[0].getChildren()[0].getValue()
                            nodeLine = nodes.getChildren()[0].getChildren()[0].getLine()
                        
                        # See if the variable exists in the local context
                        if variable in localContext:
                            endType = localContext[variable]
                        else:
                            print("semantic error")
                        
                        # Process the LHS
                        if nodeType == "id":
                            exprNode = nodes.getChildren()[1].getChildren()
                            
                            # Determine what is on the LHS
                            if isinstance(exprNode, list):
                                
                                # If its an attribute node
                                if exprNode[0].getNodeType() == "AttributeNode":
                                    objectName = exprNode[0].getChildren()[0].getValue()
                                    objectType = localContext[objectName]
                                    objectLine = exprNode[0].getChildren()[0].getLine()
                                    attributeName = exprNode[0].getChildren()[1].getValue()
                                    
                                    # If the attribute for the class is defined in the context
                                    if attributeName in definedClasses[objectType]:
                                        expectedNumArgs = len(definedClasses[objectType][attributeName][0])
                                        
                                        # Too many or too little arguments
                                        if len(exprNode[1].getChildren()) != expectedNumArgs:
                                            semanticErrors.append((f"Semantic Error: function {attributeName} was given invalid number of arguments", objectLine))
                                            continue
                                        index = 0
                                        
                                        # Comapre the parameter types one at a time, only return the error on the last 
                                        for node in exprNode[1].getChildren():
                                            if node.getChildren()[0].getValue() != None:
                                                type = node.getChildren()[0].getNodeType()[:-3]
                                                if type != definedClasses[objectType][attributeName][0][index][1]:
                                                    semanticErrors.append((f"Semantic Error: function {attributeName} was given an invalid type of argument", objectLine))
                                                    break
                                                index += 1
                                            else:
                                                if node.getChildren()[0].getNodeType() == "SignedNode":
                                                    type = node.getChildren()[0].getChildren()[1].getNodeType()[:-3]
                                                if type != definedClasses[objectType][attributeName][0][index][1]:
                                                    semanticErrors.append((f"Semantic Error: function {attributeName} was given an invalid type of argument", objectLine))
                                                    break
                                                index += 1
                                    else:
                                        
                                        # If its a function param list that means the function was not recognized
                                        if exprNode[1].getNodeType() == "FuncParamList":
                                            semanticErrors.append((f"Semantic Error: undeclared function {attributeName}", objectLine))
                                            continue
                                        
                                        # Otherwise its an undeclared member
                                        else:
                                            semanticErrors.append((f"Semantic Error: undeclared member {attributeName}", objectLine))
                                            continue
                                
                                # If its just an id check if the id is defined in this context
                                elif exprNode[0].getNodeType() == "id":
                                    variableName = exprNode[0].getValue()
                                    if variableName not in localContext:
                                        semanticErrors.append((f"Semantic Error: undeclared variable {variableName} in local scope", exprNode[0].getLine()))
                        
                        # Attribute node processing
                        elif nodeType == "AttributeNode":
                            
                            # This means its not an index
                            if "[" not in endType:
                                
                                # If its not on an object of a defined class then its not using the dot operator correctly
                                if endType not in definedClasses.keys():
                                    semanticErrors.append((f"Semantic Error: cannot use \".\" operator on {variable} with non-class type {endType}", nodeLine))
                                    continue

                                attNode = nodes.getChildren()[0].getChildren()
                                objectName = attNode[0].getValue()
                                objectType = localContext[objectName]
                                objectLine = attNode[0].getLine()
                                attributeName = attNode[1].getValue()
                                
                                # If the object is not defined in the current context
                                if attributeName not in definedClasses[objectType]:                  
                                    semanticErrors.append((f"Semantic Error: undeclared member {attributeName}", objectLine))
                                    continue
                            else:
                                
                                # Doing indexing now
                                for indice in nodes.getChildren()[0].getChildren()[1:]:
                                    if indice in localContext:
                                        
                                        # If it was an id, the id cannot belong to something that isnt an integer
                                        if localContext[indice] != "integer":
                                            semanticErrors.append((f"Semantic Error: cannot use non-integer array index for {variable}", nodeLine))
                                            continue
                                    
                                    # Otherwise if its a number it number be an intlit
                                    elif indice.getNodeType() != "intlit":
                                        semanticErrors.append((f"Semantic Error: cannot use non-integer array index for {variable}", nodeLine))
                                        continue
                                
                                # If the number of children doesnt equal the number of dimension on the variable
                                if len(nodes.getChildren()[0].getChildren()[1:]) != endType.count("["):
                                    semanticErrors.append((f"Semantic Error: use of array {variable} with wrong number of dimensions", nodeLine))
                        
                        # Indice node processing
                        elif nodeType == "IndiceNode":
                            
                            # Doing indexing now
                            for indice in nodes.getChildren()[0].getChildren()[1:]:
                                if indice in localContext:
                                    
                                    # If it was an id, the id cannot belong to something that isnt an integer
                                    if localContext[indice] != "integer":
                                        semanticErrors.append((f"Semantic Error: cannot use non-integer array index for {variable}", nodeLine))
                                        continue
                                
                                # Otherwise if its a number it number be an intlit
                                elif indice.getNodeType() != "intlit":
                                    semanticErrors.append((f"Semantic Error: cannot use non-integer array index for {variable}", nodeLine))
                                    continue
                            
                            # If the number of children doesnt equal the number of dimension on the variable
                            if len(nodes.getChildren()[0].getChildren()[1:]) != endType.count("["):
                                semanticErrors.append((f"Semantic Error: use of array {variable} with wrong number of dimensions", nodeLine))
                                continue
                    
                    # If a free id is called its likely a function call
                    if nodes.getNodeType() == "id":
                        functionCall = nodes.getValue()
                        
                        # The function paramlist is in the next node so we need to call iter
                        functionVars = next(calls)
                        functionLine = nodes.getLine()
                        if functionCall in globalDefinedFunctions:
                            
                            # Checking if there are multiple defined functions for a given name
                            if not isinstance(globalDefinedFunctions[functionCall], list):
                                expectedNumArgs = len(globalDefinedFunctions[functionCall][0])
                                
                                # If the number of arguments is different than the expected number
                                if len(functionVars.getChildren()) != expectedNumArgs:
                                    semanticErrors.append((f"Semantic Error: function {functionCall} was given invalid number of arguments", functionLine))
                                    continue
                                index = 0
                                
                                # Individually check each variable that the types match up
                                for node in functionVars.getChildren():
                                    
                                    # If its a leaf
                                    if node.getChildren()[0].getValue() != None:
                                        type = node.getChildren()[0].getNodeType()[:-3]
                                        
                                        # If the types don't match up
                                        if type != globalDefinedFunctions[functionCall][0][index][1]:
                                            semanticErrors.append((f"Semantic Error: function {functionCall} was given an invalid type of argument", functionLine))
                                            break
                                        index += 1
                                    else:
                                        
                                        # Unpack the value from the signed node
                                        if node.getChildren()[0].getNodeType() == "SignedNode":
                                            type = node.getChildren()[0].getChildren()[1].getNodeType()[:-3]
                                        
                                        # If the types dont match up
                                        if type != globalDefinedFunctions[functionCall][0][index][1]:
                                            semanticErrors.append((f"Semantic Error: function {functionCall} was given an invalid type of argument", functionLine))
                                            break
                                        index += 1
                            else:
                                
                                # This is because of function overloading leads to having a list of possible options, check each pair
                                for pair in globalDefinedFunctions[functionCall]:
                                    
                                    # If the number of arguments is off immediately look to the next one
                                    expectedNumArgs = len(pair[0][0])
                                    if len(functionVars.getChildren()) != expectedNumArgs:
                                        
                                        # This only returns if its the last possible options for functions
                                        if pair == globalDefinedFunctions[functionCall][-1]:
                                            semanticErrors.append((f"Semantic Error: function {functionCall} was given invalid number of arguments", functionLine))
                                        continue
                                    index = 0
                                    
                                    # Check variable by variable that the types are the same
                                    for node in functionVars.getChildren():
                                        
                                        # If its a leaf
                                        if node.getChildren()[0].getValue() != None:
                                            type = node.getChildren()[0].getNodeType()[:-3]
                                            if type != pair[0][index][1]:
                                                
                                                # This only returns if its the last possible options for functions
                                                if pair == globalDefinedFunctions[functionCall][-1]:
                                                    semanticErrors.append((f"Semantic Error: function {functionCall} was given an invalid type of argument", functionLine))
                                                break
                                            index += 1
                                        else:
                                            
                                            # Unpack the value from the signed node
                                            if node.getChildren()[0].getNodeType() == "SignedNode":
                                                type = node.getChildren()[0].getChildren()[1].getNodeType()[:-3]
                                            if type != pair[0][index][1]:
                                                
                                                # This only returns if its the last possible options for functions
                                                if pair == globalDefinedFunctions[functionCall][-1]:
                                                    semanticErrors.append((f"Semantic Error: function {functionCall} was given an invalid type of argument", functionLine))
                                                break
                                            index += 1
                        
                        # If the function isn't defined
                        else:
                            semanticErrors.append((f"Semantic Error: undefined free function {functionCall}", functionLine))                       
                tree.pop()
                continue
            
            # This will decompose nodes, normally only the prog node will be processed here 
            if tree[-1].getChildren() != None:
                children = tree[-1].getChildren() if isinstance(tree[-1].getChildren(), list) else [tree[-1].getChildren()]
                tree.pop()
                tree.extend(children[::-1])
        else:
            tree.pop()
 
    for func in context:
        values = func.split(".")
        semanticErrors.append((f"Semantic Error: undefined member declaration in {values[0]}.{values[1]}", context[func][1]))

    # Print semantic errors to the file
    semanticErrors.sort(key=lambda x: x[1])
    for error in semanticErrors:
        if error[1] == 0:
            print(error[0], file=warning)
        else:
            print(error[0] + f" found on line {error[1]}.", file=warning)
    