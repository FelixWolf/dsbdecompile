#!/usr/bin/env python3
import argparse
import struct
dsbHeader = struct.Struct("<5sII8x")
dsbLine = struct.Struct("<2H8H")
def parseDSB(data):
    offset = 0
    magic, lines, flags = dsbHeader.unpack_from(data, offset)
    offset = offset + dsbHeader.size
    result = []
    for i in range(0, lines):
        line = dsbLine.unpack_from(data, offset)
        offset = offset + dsbLine.size
        print(line)
        result.append(((line[0], line[1]), line[2:]))
    return result

def parseDSList(data):
    lines = [{},{},{},{},{},{}]
    for line in data.split("\n"):
        if line == "":
            continue
        Type, SubType, String = line.split("\t", 2)
        lines[int(Type)][int(SubType)] = String
    return lines
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decompile DSB file')
    parser.add_argument('-d', '--dslist', default="dslist.txt",
                        help='DS List table')
    parser.add_argument('-s', '--strings', default="default.txt",
                        help='DS string table')
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='DS string table')
    parser.add_argument('dsb', default="default.dsb", nargs="?",
                        help='DragonSpeak Binary')

    args = parser.parse_args()
    
    dsList = None
    with open(args.dslist, "r") as f:
        dsList = parseDSList(f.read())
    
    dsLines = None
    with open(args.dsb, "rb") as f:
        dsLines = parseDSB(f.read())
    
    stringTable = []
    
    print("DSPK V04.00 Furcadia\n")
    lastLineType = 0
    for line in dsLines:
        template = dsList[line[0][0]][line[0][1]]
        text = ""
        paramOffset = 0
        i = 0
        l = len(template)
        while i < l:
            c = template[i]
            if c == "%":
                v = template[i+1]
                param = line[1][paramOffset]
                #String
                if v == "s":
                    string = "String #{}".format(param)
                    if param < len(stringTable):
                        string = stringTable[param]
                    text += "{{{}}}".format(string)
                
                #Integer or Variable
                elif v == "i":
                    #Integer
                    if param < 50000:
                        text += "{}".format(param)
                    #Variable
                    else:
                        text += "%var{}".format(param-50000)
                
                #Variable
                elif v == "v":
                    text += "%var{}".format(param)
                
                #Position
                elif v == "p":
                    param2 = line[1][paramOffset+1]
                    paramOffset += 1
                    #Both values are numbers
                    if param < 50000 and param2 < 50000:
                        text += "{},{}".format(param, param2)
                    
                    #One value is a variable
                    elif param >= 50000 and param2 < 50000:
                        text += "%var{},{}".format(param-50000, param2)
                    elif param < 50000 and param2 >= 50000:
                        text += "{},%var{}".format(param, param2-50000)
                    
                    #Both values are part of a position variable
                    elif param == param2-1:
                        text += "%var{}".format(param-50000)
                    
                    #Both values are different variables
                    else:
                        text += "%var{},%var{}".format(param-50000, param2-50000)
                
                #String variable
                elif v == "r":
                    print("Don't know how to handle string variables yet!")
                
                #Panic
                else:
                    print("UNKNOWN VARIABLE TYPE {}".format(v))
                    exit()
                i += 2
                paramOffset += 1
            else:
                text += c
                i += 1
        
        if lastLineType == 5 and line[0][0] == 0:
            print("")
        
        print("{}({}:{}) {}".format((" "*args.indent)*line[0][0], *line[0], text))
        lastLineType = line[0][0]
    print("\n*Endtriggers* 8888 *Endtriggers*")
    
    #print(dsList)