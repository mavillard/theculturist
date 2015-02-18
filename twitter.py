# -*- coding: utf-8 -*-
#!/usr/bin/env python

import twitter
import time
import serial

#Functions
def getCommanders():
    commanders = api.GetFriends()
    commanders.append(api.GetUser(user))
    return commanders

def isCommand(p,u):
    if p.text.count('$') == 2:
        if u.screen_name == user:
            result = True
        elif '@'+ user in p.text:
            result = True
        else:
            result = False
    else:
        result = False
    return result

def getLastCommands():
    commands = {}
    for c in getCommanders():
        timeline = api.GetUserTimeline(c.screen_name)
        if timeline:
            new = timeline[0]
            if isCommand(new,c):
                commands[c] = new
    return commands

def extractInstruction(s):
    ini = s.find('$')
    sub = s[ini+1:]
    end = sub.find('$')
    sub = sub[:end]
    return sub

def getCommand():
    command = []
    last_commands = getLastCommands()
    if last_commands:
        u = last_commands.keys()[0]
        i = last_commands[u]
        command.append(u.screen_name)
        command.append(extractInstruction(i.text))
        command.append(i.id)
    return command

def executed(command):
    return exec_commands and command[2] in exec_commands
    
def arduino_send(s):
    for c in s:
        arduino.write(c)


#Authenticate yourself with twitter
ck = t_consumer_key
cs = t_consumer_secret
atk = t_access_token
ats = t_access_token_secret
api = twitter.Api(ck,cs,atk,ats)
#User
user = 'H9832B'

#Arduino
arduino = serial.Serial('/dev/ttyACM0',9600,timeout=1)

#Begin
exec_commands = []
while True:
    command = getCommand()
    if len(command) > 0 and not executed (command):
        msg = command[0] + " -> " + command[1]
        arduino_send("@"+msg+"%")
        exec_commands.append(command[2])
        print "user: " + command[0] + ", command: " + command[1]
    else:
        print "No new commands."
    time.sleep(5)
#End
