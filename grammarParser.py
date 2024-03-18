# COMP 442 compiler design assignment 2 grammar parser + assignment 3 attribute grammar

import os
from collections import deque

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
    def __init__(self, nodeType, value=None):
        self.nodeType = nodeType
        self.value = value
        self.parent = None
        
    def getNodeType(self):
        return self.nodeType
    
    def getValue(self):
        return self.value
    
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
def createLeaf(string, value):
    leaf = Leaf(string, value)
    semantic.append(leaf)

"""
Creates a dim leaf, used to specify a dimension for variables
"""    
def createLeafDim():
    leaf = Leaf("dim")
    semantic.append(leaf)

"""
Creates a type leaf, used when specifying return types
"""     
def createLeafType(value):
    leaf = Leaf("type", value)
    semantic.append(leaf)

"""
Creates a visibility leaf, used to specify the visibility of a function or variable
"""     
def createLeafVisibility(value):
    leaf = Leaf("Visibility", value)
    semantic.append(leaf)

"""
Creates a sign leaf, used to specify that whatever after is signed
"""     
def createLeafSign():
    leaf = Leaf("Sign")
    semantic.append(leaf)

"""
Creates an epsilon node, used in cases where the node will take a variable length of children
"""     
def createLeafEpsilon():
    leaf = Leaf("Epsilon")
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
         "ARRAYSIZE": {"lsqbr": ["lsqbr", "ENDBR"]},
         "ASSIGNOP": {"equal": ["equal"]},
         "ENDBR": {"rsqbr": ["rsqbr"], "intlit": ["intlit", createLeafDim, "rsqbr"]},
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
                    createLeaf(previousLexeme[1], previousLexeme[0])
                elif stack[-1] in [createLeafVisibility, createLeafType]:
                    stack[-1](previousLexeme[0])
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
        symbolTable = open(symbolTable, "x")
    else:
        symbolTable = open(symbolTable, "w")    
    
    for node in semantic:
        checkClasses(node, symbolTable)
        
    astFile.close()
    symbolTable.close()
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
            
def checkClasses(root, file):
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
    
    depth = 0        
    printTableHeader(globalTable.getTableName(), depth, file)
    for classes in globalTable.getClasses():
        depth = 0 
        printTableContents(["class", classes.getTableName()], depth, file)
        depth = 1
        printTableHeader(classes.getTableName(), depth, file)
        inherits = ", ".join(classes.getInherits()) if classes.getInherits() != [] else "none"
        printTableContents(["inherit", inherits], depth, file)
        for data in classes.getData():
            printTableContents(["data", data[0], data[1], data[2]], depth, file)
        for func in classes.getFunction():
            functionArgs = ", ".join([x[1] for x in func.getParam()])
            functionSig = f"({functionArgs}): {func.getReturnType()}"
            printTableContents(["function", func.getFuncName(), functionSig, func.getVisibility()], depth, file)
            depth = 2
            printTableHeader(f"{classes.getTableName()}::{func.getFuncName()}", depth, file)
            for param in func.getParam()[::-1]:
                printTableContents(["param", param[0], param[1]], depth, file)
            for local in func.getLocal():
                printTableContents(["local", local[0], local[1]], depth, file)
            printTableClose(depth, file)
        depth = 1
        printTableClose(depth, file)
    for globalFunction in globalTable.getFunction():
        depth = 0
        printTableContents(["function", globalFunction.getFuncName()], depth, file)
        depth = 1
        printTableHeader(f"::{globalFunction.getFuncName()}", depth, file)
        for local in globalFunction.getLocal():
            printTableContents(["local", local[0], local[1]], depth, file)
        printTableClose(depth, file)
    depth = 0
    printTableClose(depth, file)
    
            
def printTableHeader(tableName, depth, file):
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)
    print("|    " * depth + "| table: " + tableName.ljust(74-depth*8) + "|" + "  |" * depth, file=file)
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)
    
def printTableContents(content, depth, file):
    if len(content) == 2:
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(69 - depth*8) + "|" + "  |" * depth, file=file)
        
    elif len(content) == 3:  
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(12) + "| " + content[2].ljust(55 - depth*8) + "|" + "  |" * depth, file=file)
        
    elif len(content) == 4:
        print("|    " * depth + "| " + content[0].ljust(10) + "| " + content[1].ljust(12) + "| " + content[2].ljust(43 - depth*8) + "| " + content[3].ljust(10) + "|" +  "  |" * depth, file=file)

def printTableClose(depth, file):
    print("|    " * depth + "="*(84-depth*8) + "  |" * depth, file=file)