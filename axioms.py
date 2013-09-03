

import inspect
import re
import PNLI # Peter Norvig's Lisp Interpreter
import _tkinter

from Tkinter import *

from tkSimpleDialog import askstring
from tkFileDialog   import asksaveasfilename


global ifsToClose 
global identifierSet
global functionSet
ifsToClose = 0
identifierSet = []
functionSet = []


def parse(rbp=0):
    global token
    t = token
    token = next()
    left = t.nud()
   
    while rbp < token.lbp:
        t = token
        token = next()
        left = t.led(left)
    return left

class functionBuilderToken:
    lbp = 5
    def nud(self):
        self.string = ""
        global token
        global ifsToClose
        
        token = next() # advances past identifier
        token = next() # advances past :
        
        if not isinstance(token, functionBuilderToken): # if there is only one bound identifier
            self.string = self.string + str(parse()) + " " #stops at comma
            token = next()#advances past comma
        
        while isinstance(token, functionBuilderToken):
            
            while isinstance(token, functionBuilderToken): # advances past one lines  All x:
                token = next() # advances past All
                token = next() # advances past identifier
                token = next() # advances past :
                
            self.string = self.string + str(parse()) + " " #stops at comma
            token = next()#advances past comma
        
            
        else:
            self.string = self.string +')'*ifsToClose
        token = next() # advances past >    
        
        return self
    def __repr__(self):
        
        return self.string    
        
             

class functionDefinitionToken:
    lbp = 10
    def __init__(self, id):
        self.id = id
        
    def nud(self):
        
        global token
        global functionSet
        global ifsToClose
        
        ifsToClose = 0
        
        self.string = "(define ("+ self.id
        
        while not isinstance(token, operatorCloseParenToken):
            self.string = self.string + " "+ str(parse())
            if isinstance(token, symbolCommaToken):
                token = next() # advances past comma
        token = next() # advances past )
        self.string = self.string + ")"
        functionSet = []
        functionSet.append(self.string[8:]) # ignores the (define 
                
        token = next() # advances past comma
        
        self.string = self.string + " " + str(parse()) + ")"
        
        return self
    def __repr__(self):
        return self.string
    
class functionCallToken:
    lbp = 10
    def __init__(self, id):
        self.id = id
        
    def nud(self):
        global token
        self.string = "(" + self.id
        
        while not isinstance(token, operatorCloseParenToken):
            self.string = self.string + " "+ str(parse())
            if isinstance(token, symbolCommaToken):
                token = next() # advances past comma
        token = next() # advances past )
        self.string = self.string + ")"
        
        if self.string in functionSet:
            if isinstance(token, symbolCommaToken):
                self.string = "#t"
            if isinstance(token, operatorEqualToken):
                token = next() #advances past =
                self.string = str(parse())
            if isinstance(token, operatorIfAndOnlyIfToken):
                token = next() # advances past <->
                self.string = str(parse())
            
            
        return self
    def __repr__(self):
        return self.string        
                
        
class functionPrefixHeadToken:
    lbp = 10
    def nud(self):
        global token
        self.string = "(car "+ str(parse()) + ")"
        token = next() # advances past )
        return self
    def __repr__(self): 
        return self.string
           
class functionPrefixTailToken:
    lbp = 10
    def nud(self):
        global token
        self.string = "(cdr "+ str(parse()) + ")"
        token = next() # advances past )
        return self
    def __repr__(self): 
        return self.string
    
class functionPrefixConsToken:
    lbp = 10
    def nud(self):
        global token
        self.string = "(cons " +  str(parse()) + " "       
        token = next() # advances past ,
        self.string = self.string +  str(parse()) + ")"
        token = next() # advances past )
        return self
    def __repr__(self): 
        return self.string
           
    
class expressionPrefixLambdaToken:
    lbp = 10
    def nud(self):
        
        global token
        self.identifiers = []
        self.args = []
        self.string = "((lambda (" + token.symbol()
        token = next() # advances past first argument
        
        while str(token) != ":":
            if str(token) == ",":
                token = next()
            self.string =  self.string + " " + token.symbol()
            token = next()
             
        token = next() #advances past :
        self.string = self.string + ") " + str(parse()) + ") " #parse() should go untill it hits the comma
        token = next() #advances past comma
        
        while str(token) != "end" and str(token) != ")" :
            if str(token) == ",":
                token = next() #advances past comma if there is one
            self.string = self.string + " " + str(parse())
            
        self.string = self.string + ")"
        return self
    
    def __repr__(self):
        
        return self.string 
                   
class expressionPrefixIfToken:
    lbp = 10
    def nud(self):
        global token
        
        self.string = "(if " + str(parse())
        token = next() # advances past comma
        
        self.string =  self.string + " " + str(parse())
        token= next() # advances past comma
        token = next() #advances past else
       
        self.string =  self.string + " " + str(parse()) + ")"
        
        return self 
        
    def __repr__(self):
        return self.string

class identifierToken:
    def __init__(self, value):
        self.value = value
        
    def nud(self):
        return self
    def symbol(self):
        return str(self.value)
    def __repr__(self):
        return "%s" % self.value
    
class integerToken:
    def __init__(self, value):
        self.value = value
    def nud(self):
        return self
    def symbol(self):
        return str(self.value)
    def __repr__(self):
        return "%s" % self.value
    
class operatorImpliesToken:
    lbp = 20
    def led(self, left):
        global ifsToClose
        ifsToClose += 1
        self.first = left
        self.second = parse(19)
        return self
    def __repr__(self):
        return "(if %s %s" % (self.first, self.second)

class operatorIfAndOnlyIfToken:
    lbp = 20
    def led(self, left):
        self.first = left
        self.second = parse(19)
        return self
    def __repr__(self):
        return "(this made it here hmm %s %s)" % (self.first, self.second)
    
class operatorOrToken:
    lbp = 30
    def led(self, left):
        self.first = left
        self.second = parse(30)
        return self
    def __repr__(self):
        return "((lambda (x y) (if x #t y)) %s %s)" % (self.first, self.second)
    
class operatorAndToken:
    lbp = 30
    def led(self, left):
        self.first = left
        self.second = parse(30)
        return self
    def __repr__(self):
        return "((lambda (x y) (if x y #f)) %s %s)" % (self.first, self.second)
        
class operatorNotToken:
    lbp = 31
    def nud(self):
        self.first = parse(31)
        return self
    def led(self, left):
        self.fisrt = parse(31)
        return self
    def __repr__(self):
        return "(not %s)" % (self.first)
       
class operatorAssignToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
        
        
    def symbol(self):
        return ":="
    def __repr__(self):
        global identifierSet
        
        if str(self.first) in identifierSet:
            
            return "(set! %s %s)" % (self.first, self.second)
        identifierSet.append(str(self.first))
        return "(define " + str(self.first) + " 0) (set! %s %s)" % (self.first, self.second)
       
class operatorEqualToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
    def __repr__(self):
        return "(equal? %s %s)" % (self.first, self.second)
    
class operatorLessThanToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
    def __repr__(self):
        return "(< %s %s)" % (self.first, self.second)
    
class operatorGreaterThanToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
    def __repr__(self):
        return "(> %s %s)" % (self.first, self.second)
    
class operatorLessThanEqualToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
    def __repr__(self):
        return "(<= %s %s)" % (self.first, self.second)
    
class operatorGreaterThanEqualToken:
    lbp = 40
    def led(self, left):
        self.first = left
        self.second = parse(40)
        return self
    def __repr__(self):
        return "(>= %s %s)" % (self.first, self.second)
    
class operatorAddToken:
    lbp = 50
    def nud(self): #if function is unary
        self.first = parse(70)
        self.second = 0
        return self
    def led(self, left):
        self.first = left
        self.second = parse(50)
        return self
    def __repr__(self):
        return "(+ %s %s)" % (self.first, self.second) 
    
class operatorMinToken:
    lbp = 50
    def nud(self): #if function is unary
        self.first = 0 
        self.second = parse(70)
        return self
    def led(self, left):
        self.first = left
        self.second = parse(50)
        return self
    def __repr__(self):
        return "(- %s %s)" % (self.first, self.second) 
    
class listOperatorAppendToken:
    lbp = 50
    def led(self, left):
        self.first = left
        self.second = parse(50)
        return self
    def __repr__(self):
        return "(append %s %s)" % (self.first, self.second) 
    
class operatorMulToken:
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = parse(60)
        return self
    def __repr__(self):
        return "(* %s %s)" % (self.first, self.second) 
    
class operatorModToken:
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = parse(60)
        return self
    def __repr__(self):
        return "(mod %s %s)" % (self.first, self.second) 

class operatorExponToken: 
    lbp = 75 
    def led(self, left):
        self.first = left
        self.second = parse(74)
        return self
    def __repr__(self):
        return "(^ %s %s)" % (self.first, self.second)  
       
class operatorOpenParenToken:
    lbp = 80
    def nud(self):
        expression = parse()
        global token
        token = next()
        return expression
      
class operatorOpenBracketToken: #this token could be used to do whole expresions by using a comma
    lbp = 80
    def nud(self):
        global token
        string = "(list " + str(token)
        token = next() #advances the past the first element
        while str(token) != "]":
            if str(token) == ",":
                token = next()
            string = string + " "+ str(token) 
            token = next()
            
        token = next()
        self.first = string
        return self
    def __repr__(self):
        return "%s)" % (self.first) 

class operatorCloseBracketToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return "]"
    
class operatorCloseParenToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return ")"
    
class symbolCommaToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return ","

class symbolEmptyBracketsToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return "(list )"

class symbolColonToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return ":"
    
class endToken:
    lbp = 0
    def __repr__(self):
        return "end"
class booleanFalseToken():
    lbp = 0
    def nud(self):
        return self
    def __repr__(self):
        return "#f"
    
class booleanTrueToken():
    lbp = 0    
    def nud(self):
        return self
    def __repr__(self):
        return "#t"
    
tokenToFunctionDictionary= {"All":"functionBuilderToken()","all" :"functionBuilderToken()", "++" : "listOperatorAppendToken()","cons(" : "functionPrefixConsToken()","tail(" : "functionPrefixTailToken()","head(" : "functionPrefixHeadToken()","false" : "booleanFalseToken()","False" : "booleanFalseToken()", "true" : "booleanTrueToken()","True" : "booleanTrueToken()","if" : "expressionPrefixIfToken()", ":" : "symbolColonToken()", "[]" : "symbolEmptyBracketsToken()", "," : "symbolCommaToken()","lambda" : "expressionPrefixLambdaToken()","(lambda" : "expressionPrefixLambdaToken()","if" : "expressionPrefixIfToken()", "^" : "operatorExponToken()", "%": "operatorModToken()",":=" : "operatorAssignToken()", "]": "operatorCloseBracketToken()", "[" : "operatorOpenBracketToken()", "=" : "operatorAssignToken()", "=" : "operatorEqualToken()", "->" : "operatorImpliesToken()","<->" : "operatorIfAndOnlyIfToken()", "not" : "operatorNotToken()", "and" : "operatorAndToken()", "or" : "operatorOrToken()", "=>" : "operatorGreaterThanEqualToken()", "=<" : "operatorLessThanEqualToken()", "<" : "operatorLessThanToken()", ">" : "operatorGreaterThanToken()", "+" : "operatorAddToken()", "*" : "operatorMulToken()", "-" : "operatorMinToken()", "(" : "operatorOpenParenToken()", ")" : "operatorCloseParenToken()",None : "endToken()"}

#         ((expresion)) 80 (unary - +) 70 (/ *) 60 (+ -) 50 (< > =< => =) 40 (not) 31 (and or) 30  (<-> ->) 20 (if else lambda) 10  (:=) 5
tokenPattern = re.compile("[\*+]+|[\*+%^\[\]]|[0-9]+|<[A-Za-z]+\(|[A-Za-z]+\(|[A-Za-z0-9]+|'or'|'and'|'not'|\(|\)|=<|<->|->|=>|:=|<|>|-|=|:|,")
  
def printTokens(program): # Used for debugging tokenizer
    for token in tokenPattern.findall(program):
        print token
        


def tokenize(program):
    
    for token in tokenPattern.findall(program):
        
        if token.isdigit():
            yield integerToken(token)       
        elif token in tokenToFunctionDictionary:
            yield  eval(tokenToFunctionDictionary[token])
        elif token.startswith("<"):
            yield functionDefinitionToken(token.replace("<","").replace("(",''))
        elif token.endswith("("):
            yield functionCallToken(token.replace("(",""))
        else:
            yield identifierToken(token)  
        
    yield endToken()   

    
def parseString(program):
    
    
    
    if len(program) == 0:
        return
    global token, next
    next = tokenize(program).next
    token = next()
    return str(parse())


        
def formatProgram(filename):
    text = [] 
    input = open(filename, 'r') 
    definitionBuilding = False
    string = ""
    
    for line in input:
        if len(line) > 1:
            
            
            if line.startswith("<"):
                definitionBuilding = True
             
            if definitionBuilding:
                
                if line.endswith('>\n'):
                   
                    string = string + line[:-2]+ ",>\n"
                    
                    text.append(string)
                    string = ""
                    definitionBuilding = False
                else:
                    string = string + line[:-1] + ', '
                
                 
            else:   
                text.append(line)
                
    input.close()
    output = open(filename, 'w') 
    for line in text:

        output.write(line+ "\n")
            
    output.close()
    
    

        
def parseProgram(filename):
    text = [] 
    input = open(filename, 'r')
    for line in input:
        if len(line) > 1:
            text.append(line)
    input.close()
    output = open(filename, 'w') 
    for line in text:
            output.write(parseString(line)+ "\n")
    output.close()

#formatProgram("testformatinginput.txt")
#parseProgram("testformatinginput.txt")

class textFrame(Frame):
    
    def __init__(self, parent = None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makewidgets()
    def makewidgets(self):
        text = Text(self)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        
        self.text = text
    def getText(self):
        return self.text.get('1.0', END+'-1c') 
    def setText(self):
        lastinput = open("lastinput", 'r')
        return self.text.insert(1.0, str(lastinput.read()) )
        
    
 
       
class App(textFrame):

    def __init__(self, parent = None, file = None):
        
        frame1= Frame(parent)
        frame1.pack(fill=X)
        
        
        Button(frame1, text='Save As',  command=self.onSave).pack(side=LEFT)
        Button(frame1, text='Run Code',   command=self.onRunCode).pack(side=LEFT)
        
        textFrame.__init__(self)
        
#        self.frame2 = Frame(parent)
#        self.frame.pack(fill=X,side=BOTTOM)
        self.text2 = Text(height = 8,borderwidth = 5 )
        self.text2.pack()
        self.setText()
        
        
    def onSave(self):
        filename = asksaveasfilename()
        if filename:
            alltext = self.textbox.gettext()                      
            open(filename, 'w').write(alltext) 
                
    def onRunCode(self):
        
        f = open('codeToRun.txt', 'w')
        f.write(self.getText())
        save = open('lastInput', 'w')
        save.write(self.getText())
        save.close()
        f.close()
        
        formatProgram("codeToRun.txt")
        parseProgram("codeToRun.txt")
        
        
        self.text2.delete(1.0, END)
        self.text2.insert(1.0, PNLI.load("codeToRun.txt") )
        
        
        

if __name__ == '__main__':
    try:
        App(file=sys.argv[1]).mainloop()   
    except IndexError:
        App().mainloop()        





    






