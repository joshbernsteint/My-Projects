import os
import sys

class var:
    def __init__(self,line,lc):
        self.offset = lc
        parts = line.split("=")
        parts = map(lambda x: x.strip(),parts)
        self.name,self.value = parts                
    def getName(self):
        return self.name
    def getValue(self):
        return int(self.value)
    def getAddress(self):
        return self.offset
    def __str__(self):
        return self.value
    


class instruction:
    def __init__(self,opLst,lc):
        self.branch = False
        self.branchLabel = ""
        self.lineCount = lc
        self.offset = 0
        self.instruct = opLst[0]
        if self.instruct not in opCode:
            self.label = self.instruct
            self.instruct = opLst[1]
            self.operands = opLst[2:]
        elif self.instruct == "BACK":
            self.operands = []
            self.label = ""
        else:
            self.label = ""
            self.operands = opLst[1:]

        if len(self.operands) == 1:
            self.branch = True
            self.branchLabel = self.operands[0]
        elif self.instruct == "JUMPT":
            self.branch = True
            self.branchLabel = self.operands[1]
    
    def getOps(self):
        return self.operands
    def hasLabel(self):
        return self.label != ""
    def getLabel(self):
        return self.label
    def getLineNum(self):
        return self.lineCount
    def setOffset(self,x):
        self.offset = x
    def getOffset(self):
        return self.offset
    def getInstruct(self):
        return self.instruct
    def isBranch(self):
        return self.branch
    def getBranchLabel(self):
        return self.branchLabel

    def __str__(self):
        return f'{self.instruct} {self.operands}'
    
def removeEmptyLines(lst):
    '''Removes empty spaces from the list'''
    newList = []
    for i in lst:
        if i != '' and i[0:2] != "//":
            newList.append(i)
    return newList

def map(function,lst):
    '''Returns a list with function mapped over it'''
    newLst = []
    for element in lst:
        newLst.append(function(element))
    return newLst

def removeNewLine(instruct):
    '''Removes the newline command to instructions'''
    temp = instruct[-1:]
    if temp == '\n':
        return instruct[:-1]
    else:
        return instruct

def getOperands(instruct):
    '''Takes in the full instruction and returns the instruction name, and its operands'''
    label = removeEmptyLines(instruct.split(":",1))
    hasLabel = False
    if len(label) > 1: 
        hasLabel = True
    ops = []
    result = []
    if hasLabel:
        temp = label[1].split(" ",2)[1:]
        result.append(label[0])
        result.append(temp[0])
        ops =  temp[1].split(",")
        ops = map(lambda x: x.strip(),ops)
    else:
        if(label[0][0] == "."):
            result.append(label[0])
        elif label[0] == "BACK":
            return ["BACK"]
        else:

            temp = label[0].split(" ",1)

            result.append(temp[0])
            ops = temp[1].split(",")
            ops = map(lambda x: x.strip(), ops)

    return result + ops

def removeComments(instruct):
    '''Removes comments from a line'''
    temp = instruct.split("//")
    return temp[0]


def SplitVars(lst):
    '''Splits the variables from the code segment'''
    vars = []
    index = 0
    for element in lst:
        if element == ".VAR":
            vars = lst[index:]
            lst = lst[0:index]
        index += 1
    return (lst[1:], vars[1:])
def toInstruction(lst,index):
    return instruction(lst,index)

def makeOffset(instructionObjects):
    index = 0
    for line in instructionObjects:
        if line.hasLabel():
            tLabel = line.getLabel()
            for i in range(len(instructionObjects)):
                if instructionObjects[i].isBranch() and instructionObjects[i].getBranchLabel() == tLabel:
                    instructionObjects[i].setOffset(index-i)
        index +=1
    return instructionObjects

def toMachineCode(instruct,vars):
    '''Converts an ETHEL instruction object to machine code'''
    def binPad(target,tString):
        '''Converts target string to a binary number of size target'''
        t = bin(int(tString) & int("1"*target,base=2))
        if int(tString) < 0:
            t = t[3:]
        else:
            t = t[2:]
        if len(t) < target and int(tString) >= 0:
            t = "0"*(target-len(t)) + t
        elif len(t) < target and int(tString) < 0:
            t = "1"*(target-len(t))+t
        elif (len(t)) > target:
            raise ValueError("Offset too large, number must be smaller than or equal to 131,071")
        return t
    i = instruct.getInstruct()
    if i in opKeys:
        machineCode = ""
        if i in reg2Loc:
            '''Transcribing for instructions with reg2Loc as 1'''
            machineCode += (opCode[i])
            machineCode += ("00000000111")
            length = len(instruct.getOps())
            if length == 2 and i == "FETCH":
                machineCode += binPad(3,instruct.getOps()[0][1]) + "000" + binPad(3,instruct.getOps()[1][1]) 
            elif length == 2 and i == "STAY":
                machineCode += "000" + binPad(3,instruct.getOps()[0][1]) + binPad(3,instruct.getOps()[1][1])
            else:
                for reg in instruct.getOps():
                    machineCode += binPad(3,reg[1])
                if length != 3:
                    machineCode += "000"

        else:
            if i == "BACK":
                machineCode = opCode[i] + "0"*17 + "111"
            elif i == "SPEAK":
                label = instruct.getOps()[1]
                for l in vars:
                    if l.getName() == label:
                        machineCode = opCode[i] + "0"+binPad(16,l.getAddress()) + binPad(3,instruct.getOps()[0][1:])
                        break
            else:
                machineCode += opCode[i]
                if instruct.isBranch():
                    temp = instruct.getOffset()
                    machineCode += "0"+binPad(16,temp)
                    if i == "JUMPS":
                        machineCode += "111"
                    elif i == "JUMPT": 
                        machineCode += binPad(3,instruct.getOps()[0][1:])
                    else:
                        machineCode += "000"
                else:
                    temp = instruct.getOps()[1]
                    machineCode += binPad(17,temp)
                    machineCode += binPad(3,instruct.getOps()[0][1:])
        return machineCode
    else:
        raise ValueError(f'Incorrect Instruction {i}')



def  toImageFile(code,addressSize,dataSize,label):
    '''Converts machine code to hex and formats it for logisim'''
    def hexPad(num,l):
        '''Takes a binary string and converts it to a hex number with a length of l'''
        temp = hex(num)[2:]
        diff = int(l - len(str(temp)))
        for i in range(diff):
            temp = "0"+temp
        return temp

    codeIndex = 0
    codeLen = len(code)
    with open(f'{label}','w') as file:
        file.write('v3.0 hex words addressed\n')
        size = pow(2,addressSize)
        rows = size//8
        hexSize = addressSize//4
        i = 0
        while i <= size - 1:
            file.write(f'{hexPad(i,hexSize)}: ')
            for j in range(8):
                if codeIndex < codeLen:
                    file.write(f'{hexPad(int(code[codeIndex],base=2),dataSize//4)} ')
                    codeIndex += 1
                else:
                    file.write(f'{"0"*(dataSize//4)} ')

                if j == 7:
                    file.write('\n')
            i += 8



    





opCode = {
    "FETCH": "000110110000","STAY":  "100011000000", "UP":   "010110000000", 
    "DOWN":  "110110000000", "JUMP": "001000000100","JUMPT": "000000000010", 
    "JUMPS": "001100001100", "BACK": "000000000001","DROPIT":"100110000000","DROPITN":"001100000000",
    "SPEAK": "001100000000"
}
reg2Loc = ["FETCH","STAY","UP","DOWN","DROPIT"]
opKeys = opCode.keys()

inputFileName = sys.argv[1]
instructions = []
with open(inputFileName,mode = 'r') as inputFile:
    instructions = map(removeNewLine,inputFile.readlines())
instructions = removeEmptyLines(instructions)
instructions = map(removeComments,instructions)
instructions,variables = SplitVars(instructions)
instructions = map(getOperands,instructions)

tempLst = []
for i in range(len(instructions)):
    tempLst.append(toInstruction(instructions[i],i))
instructions = tempLst




tempLst = []
for i in range(len(variables)):
    tempLst.append(var(variables[i],i))
variables = tempLst

instructions = makeOffset(instructionObjects=instructions)

machineInstructions = map(lambda x: toMachineCode(x,variables),instructions)

toImageFile(machineInstructions,16,32,'Instructions')

if variables != []:
    varValues = []
    for e in variables:
        varValues.append(bin(e.getValue()))
    toImageFile(varValues,8,64,"Data")