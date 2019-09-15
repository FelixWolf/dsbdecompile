#!/usr/bin/env python3
#This is a poorly written script to do one thing, normally you won't need this
#It accepts the keys.ini from furcadia.
import csv
import configparser

data = []
config = configparser.ConfigParser(delimiters=("="))
config.read('keys.ini')
for section in ["Causes", "Additional Conditions", "Areas", "Filters", "Effects"]:
    for key in config[section]:
        data.append(config[section][key])

def parseLine(line):
    line = list(csv.reader([line]))[0][2]
    Type, Id, String = None, None, None
    buffer = ""
    state = 0
    for c in line:
        if state == 0:
            if c == "(":
                state = 1
            else:
                print("ERROR unexpected "+c)
                exit()
        elif state == 1:
            if c == ":":
                if buffer == "":
                    print("ERROR empty buffer state 1")
                    exit()
                else:
                    Type = int(buffer)
                    buffer = ""
                    state = 2
            else:
                buffer = buffer + c
        elif state == 2:
            if c == ")":
                if buffer == "":
                    print("ERROR empty buffer state 2")
                    exit()
                else:
                    Id = int(buffer)
                    buffer = ""
                    state = 3
            else:
                buffer = buffer + c
        elif state == 3:
            if c == " ":
                if buffer != "":
                    print("ERROR buffer not empty state 3")
                    exit()
                else:
                    state = 4
            else:
                buffer = buffer + c
        elif state == 4:
            buffer = buffer + c
    String = buffer.rstrip()
    return ((Type, Id), String)
            
with open("dslist.txt", "w") as f:
    for line in data:
        ln, txt = parseLine(line)
        txt = txt.replace("(#,#)","(%p)").replace("variable #", "%v").replace("#", "%i").replace("{...}", "%s").replace("~", "%r")
        f.write("{}\t{}\t{}\n".format(ln[0], ln[1], txt))