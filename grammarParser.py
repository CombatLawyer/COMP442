# COMP 442 compiler design assignment 2 grammar parser

import os
from collections import deque

# This is the lookup table which dictates what to do upon seeing a certain symbol on the stack
table = {"ADDOP": {"minus": ["minus"], "plus": ["plus"], "or": ["or"]},
         "APARAMS": {"rpar":["epsilon"], "lpar":["EXPR", "REPTAPARAMS1"], "id":["EXPR", "REPTAPARAMS1"], "minus":["EXPR", "REPTAPARAMS1"], "plus":["EXPR", "REPTAPARAMS1"], "not":["EXPR", "REPTAPARAMS1"], "floatlit":["EXPR", "REPTAPARAMS1"], "intlit":["EXPR", "REPTAPARAMS1"]},
         "APARAMSTAIL": {"comma":["comma", "EXPR"]},
         "ARITHEXPR": {"lpar": ["TERM", "RIGHTRECARITHEXPR"], "id":["TERM", "RIGHTRECARITHEXPR"], "minus":["TERM", "RIGHTRECARITHEXPR"], "plus":["TERM", "RIGHTRECARITHEXPR"], "not":["TERM", "RIGHTRECARITHEXPR"], "floatlit":["TERM", "RIGHTRECARITHEXPR"], "intlit":["TERM", "RIGHTRECARITHEXPR"]},
         "ARRAYSIZE": {"lsqbr": ["lsqbr", "ENDBR"]},
         "ASSIGNOP": {"equal": ["equal"]},
         "ENDBR": {"rsqbr": ["rsqbr"], "intlit": ["intlit", "rsqbr"]},
         "EXPR": {"lpar": ["ARITHEXPR", "RELEXPREND"], "id": ["ARITHEXPR", "RELEXPREND"], "minus": ["ARITHEXPR", "RELEXPREND"], "plus": ["ARITHEXPR", "RELEXPREND"], "not": ["ARITHEXPR", "RELEXPREND"], "floatlit": ["ARITHEXPR", "RELEXPREND"], "intlit": ["ARITHEXPR", "RELEXPREND"]},
         "FACTOR": {"lpar": ["lpar", "ARITHEXPR", ")"], "id":["id", "VARORFUNC", "REPTFACTOR2"], "minus": ["SIGN", "FACTOR"], "plus": ["SIGN", "FACTOR"], "not": ["not","FACTOR"], "floatlit": ["floatlit"], "intlit": ["intlit"]},
         "FPARAMS": {"rpar": ["epsilon"], "id": ["id", "colon", "TYPE", "REPTFPARAMS3", "REPTFPARAMS4"]},
         "FPARAMSTAIL": {"comma": ["comma", "id", "colon", "TYPE", "REPTFPARAMSTAIL4"]},
         "FUNCBODY": {"lcurbr": ["lcurbr", "REPTFUNCBODY1", "rcurbr"]},
         "FUNCDECL": {"func": ["FUNCHEAD", "semi"]},
         "FUNCDEF": {"func": ["FUNCHEAD", "FUNCBODY"]},
         "FUNCHEAD": {"func": ["func", "id", "lpar", "FPARAMS", "rpar", "arrow", "RETURNTYPE"]},
         "IDNEST": {"dot": ["dot", "id", "VARORFUNC"]},
         "IMPLDEF": {"impl" : ["impl", "id", "lcurbr", "REPTIMPLDEF3", "rcurbr"]},
         "INDICE": {"lsqbr": ["lsqbr", "ARITHEXPR", "rsqbr"]},
         "MEMBERDECL": {"let": ["VARDECL"], "func": ["FUNCDECL"]},
         "MULTOP": {"and": ["and"], "div": ["div"], "mult": ["mult"]},
         "OPTSTRUCTDECL2": {"lcurbr": ["epsilon"], "inherits": ["inherits", "id", "REPTOPTSTRUCTDECL22"]},
         "PROG": {"struct": ["REPTPROG0"], "impl": ["REPTPROG0"], "func": ["REPTPROG0"]},
         "RELEXPR": {"lpar": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "id": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "minus": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "plus": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "not": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "floatlit": ["ARITHEXPR", "RELOP", "ARITHEXPR"], "intlit": ["ARITHEXPR", "RELOP", "ARITHEXPR"]},
         "RELEXPREND": {"rpar": ["epsilon"], "semi": ["epsilon"], "comma": ["epsilon"], "geq": ["RELOP" "ARITHEXPR"], "leq": ["RELOP" "ARITHEXPR"], "gt": ["RELOP" "ARITHEXPR"], "lt": ["RELOP" "ARITHEXPR"], "neq": ["RELOP" "ARITHEXPR"], "eq": ["RELOP" "ARITHEXPR"]},
         "RELOP": {"geq": ["geq"], "leq": ["leq"], "gt": ["gt"], "lt": ["lt"], "neq": ["neq"], "eq": ["eq"]},
         "REPTAPARAMS1": {"rpar": ["epsilon"], "comma": ["APARAMSTAIL", "REPTAPARAMS1"]},
         "REPTFACTOR2": {"rpar": ["epsilon"], "dot": ["IDNEST", "REPTFACTOR2"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["epsilon"], "div": ["epsilon"], "mult": ["epsilon"], "rsqbr": ["epsilon"], "or": ["epsilon"]},
         "REPTFPARAMS3": {"rpar": ["epsilon"], "comma": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTFPARAMS3"]},
         "REPTFPARAMS4": {"rpar": ["epsilon"], "comma": ["FPARAMSTAIL", "REPTFPARAMS4"]},
         "REPTFPARAMSTAIL4": {"rpar": ["epsilon"], "comma": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTFPARAMSTAIL4"]},
         "REPTFUNCBODY1": {"id": ["VARDECLORSTAT", "REPTFUNCBODY1"], "let": ["VARDECLORSTAT", "REPTFUNCBODY1"], "rcurbr": ["epsilon"], "return": ["VARDECLORSTAT", "REPTFUNCBODY1"], "write": ["VARDECLORSTAT", "REPTFUNCBODY1"], "read": ["VARDECLORSTAT", "REPTFUNCBODY1"], "while": ["VARDECLORSTAT", "REPTFUNCBODY1"], "if": ["VARDECLORSTAT", "REPTFUNCBODY1"]},
         "REPTIMPLDEF3": {"rcurbr": ["epsilon"], "func": ["FUNCDEF", "REPTIMPLDEF3"]},
         "REPTOPTSTRUCTDECL22": {"lcurbr": ["epsilon"], "comma": ["comma", "id", "REPTOPTSTRUCTDECL22"]},
         "REPTPROG0": {"struct": ["STRUCTORIMPLORFUNC", "REPTPROG0"], "impl": ["STRUCTORIMPLORFUNC", "REPTPROG0"], "func": ["STRUCTORIMPLORFUNC", "REPTPROG0"]},
         "REPTSTATBLOCK1": {"id": ["STATEMENT", "REPTSTATBLOCK1"], "rcurbr": ["epsilon"], "return": ["STATEMENT", "REPTSTATBLOCK1"], "write": ["STATEMENT", "REPTSTATBLOCK1"], "read": ["STATEMENT", "REPTSTATBLOCK1"], "while": ["STATEMENT", "REPTSTATBLOCK1"], "if": ["STATEMENT", "REPTSTATBLOCK1"]},
         "REPTSTATEFUNC": {"dot": ["dot", "STATESTART"], "semi": ["epsilon"]},
         "REPTSTATEVAR": {"dot": ["dot", "STATESTART"], "equal":["ASSIGNOP", "EXPR"]},
         "REPTSTATEVARORFUNC0": {"dot": ["epsilon"], "lsqbr": ["INDICE", "REPTSTATEVARORFUNC0"], "equal": ["epsilon"]},
         "REPTSTRUCTDECL4": {"private": ["VISIBILITY", "MEMBERDECL", "REPTSTRUCTDECL4"], "public": ["VISIBILITY", "MEMBERDECL", "REPTSTRUCTDECL4"], "rcurbr": ["epsilon"]},
         "REPTVARDECL4": {"semi": ["epsilon"], "lsqbr": ["ARRAYSIZE", "REPTVARDECL4"]},
         "REPTVARIABLE": {"rpar": ["epsilon"], "dot": ["VARIDNEST", "REPTVARIABLE"]},
         "REPTVARIABLE20": {"rpar": ["epsilon"], "dot": ["epsilon"], "lsqbr": ["INDICE", "REPTVARIABLE20"]},
         "REPTVARIDNEST20": {"rpar": ["epsilon"], "dot": ["epsilon"], "lsqbr": ["INDICE", "REPTVARIDNEST20"]},
         "REPTVARORFUNC0": {"rpar": ["epsilon"], "dot": ["epsilon"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["epsilon"], "div": ["epsilon"], "mult": ["epsilon"], "rsqbr": ["epsilon"], "lsqbr": ["INDICE", "REPTVARORFUNC0"], "or": ["epsilon"]},
         "RETURNTYPE": {"id": ["TYPE"], "float": ["TYPE"], "integer": ["TYPE"], "void": ["void"]},
         "RIGHTRECARITHEXPR": {"rpar": ["epsilon"], "semi": ["epsilon"], "minus": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"], "plus": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "rsqbr": ["epsilon"], "or": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"]},
         "RIGHTRECTERM": {"rpar": ["epsilon"], "semi": ["epsilon"], "minus": ["epsilon"], "plus": ["epsilon"], "comma": ["epsilon"], "geq": ["epsilon"], "leq": ["epsilon"], "gt": ["epsilon"], "lt": ["epsilon"], "neq": ["epsilon"], "eq": ["epsilon"], "and": ["MULTOP", "FACTOR", "RIGHTRECTERM"], "div": ["MULTOP", "FACTOR", "RIGHTRECTERM"], "mult": ["MULTOP", "FACTOR", "RIGHTRECTERM"], "rsqbr": ["epsilon"], "or": ["epsilon"]},
         "SIGN": {"minus": ["minus"], "plus": ["plus"]},
         "START": {"struct": ["PROG"], "impl": ["PROG"], "func": ["PROG"]},
         "STATBLOCK": {"id": ["STATEMENT"], "semi": ["epsilon"], "lcurbr": ["lcurbr", "REPTSTATBLOCK1", "rcurbr"], "return": ["STATEMENT"], "write": ["STATEMENT"], "read": ["STATEMENT"], "while": ["STATEMENT"], "else": ["epsilon"], "if": ["STATEMENT"]},
         "STATEMENT": {"id": ["STATESTART", "semi"], "return": ["return", "lpar", "EXPR", "rpar", "semi"], "write": ["write", "lpar", "EXPR", "rpar", "semi"], "read": ["read", "lpar", "VARIABLE", "rpar", "semi"], "while": ["while", "lpar", "RELEXPR", "rpar", "STATBLOCK", "semi"], "if": ["if", "lpar", "RELEXPR", "rpar", "then", "STATBLOCK", "else", "STATBLOCK", "semi"]},
         "STATESTART": {"id": ["id", "STATEVARORFUNC"]},
         "STATEVARORFUNC": {"lpar": ["lpar", "APARAMS", "rpar", "REPTSTATEFUNC"], "dot": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"], "lsqbr": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"], "equal": ["REPTSTATEVARORFUNC0", "REPTSTATEVAR"]},
         "STRUCTDECL": {"struct": ["struct", "id", "OPTSTRUCTDECL2", "lcurbr", "REPTSTRUCTDECL4", "rcurbr", "semi"]},
         "STRUCTORIMPLORFUNC": {"struct": ["STRUCTDECL"], "impl": ["IMPLDEF"], "func": ["FUNCDEF"]},
         "TERM": {"lpar": ["FACTOR", "RIGHTRECTERM"], "id": ["FACTOR", "RIGHTRECTERM"], "minus": ["FACTOR", "RIGHTRECTERM"], "plus": ["FACTOR", "RIGHTRECTERM"], "not": ["FACTOR", "RIGHTRECTERM"], "floatlit": ["FACTOR", "RIGHTRECTERM"], "intlit": ["FACTOR", "RIGHTRECTERM"]},
         "TYPE": {"id": ["id"], "float": ["float"], "integer": ["integer"]},
         "VARDECL": {"let": ["let", "id", "colon", "TYPE", "REPTVARDECL4", "semi"]},
         "VARDECLORSTAT": {"id": ["STATEMENT"], "let":["VARDECL"], "return": ["STATEMENT"], "write": ["STATEMENT"], "read": ["STATEMENT"], "while": ["STATEMENT"], "if": ["STATEMENT"]},
         "VARIABLE": {"id": ["id", "VARIABLE2"]},
         "VARIABLE2": {"rpar": ["REPTVARIABLE20", "REPTVARIABLE"], "lpar": ["lpar", "APARAMS", "rpar", "VARIDNEST"], "dot": ["REPTVARIABLE20", "REPTVARIABLE"], "lsqbr": ["REPTVARIABLE20", "REPTVARIABLE"]},
         "VARIDNEST": {"dot": ["dot", "id", "VARIDNEST2"]},
         "VARIDNEST2": {"rpar": ["REPTVARIDNEST20"], "lpar": ["lpar", "APARAMS", "rpar", "VARIDNEST"], "dot": ["REPTVARIABLE20", "REPTVARIABLE"], "lsqbr": ["REPTVARIDNEST20"]},
         "VARORFUNC": {"rpar": ["REPTVARORFUNC0"], "lpar": ["lpar", "APARAMS", "rpar"], "dot": ["REPTVARORFUNC0"], "semi": ["REPTVARORFUNC0"], "minus": ["REPTVARORFUNC0"], "plus": ["REPTVARORFUNC0"], "comma": ["REPTVARORFUNC0"], "geq": ["REPTVARORFUNC0"], "leq": ["REPTVARORFUNC0"], "gt": ["REPTVARORFUNC0"], "lt": ["REPTVARORFUNC0"], "neq": ["REPTVARORFUNC0"], "eq": ["REPTVARORFUNC0"], "and": ["REPTVARORFUNC0"], "div": ["REPTVARORFUNC0"], "mult": ["REPTVARORFUNC0"], "rsqbr": ["REPTVARORFUNC0"], "lsqbr": ["REPTVARORFUNC0"], "or": ["REPTVARORFUNC0"]},
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
    
    global errorFile
    errorFile = file
    
    # Used to reconstructed the parsed output
    line = 1
    col = 1
    
    # Used to hold the value of the production that will be placed on the stack before the stack is popped
    nextProduction = ""
    
    # While there is still content in the lexicon
    while lexicon:
        
        # Progress lexicon by removing the top of the queue
        lexeme = lexicon.popleft()
        while 1:
            
            # While the top of the stack is a production and not a character
            while list(set([stack[-1]]) & set(productions)) != []:
                
                # Indicates that the top of the stack is a dictionary and not a list (i.e. still going down the chain of productions)
                if isinstance(table[stack[-1]], dict):
                    
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
        while list(set([stack[-1]]) & set(nullable)) != []:
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
    if len(lexicon) != 0:
        
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