#! /usr/bin/env python3
# Modified by: Alan Licerio
# 09-15-20

import sys, os, re

def handleInput(command):
    userArgs = command.split()
    if command == "": # Empty user input, ignore and continue loop.
        pass
    elif 'exit' in command: # Exists the system.
        sys.exit(0)
    elif 'cd' in userArgs[0]:
        try:
            if len (userArgs) >= 2: # Change to the specified directory.
                os.chdir(userArgs[1])
            else: # Go back to parent directory.
                os.chdir("..")
        except FileNotFoundError:
            os.write(1,("cd %s: No such file or directory. Try Again!" % userArgs[1]).encode())
            pass
    elif '|' in userArgs:
        print()
        #TODO: FIX THIS.    
    else:
        execute(userArgs)


def prompt():
    while True:
        if 'PS1' in os.environ:
            os.write(1,(os.environ['PS1']).encode())
        else:
            os.write(1, ("$ ").encode())
        try:
            command = input()
        except ValueError: # Incorrect argument value
            sys.exit(1)
        handleInput(command)


def execute(userArgs):
    rc = os.fork() # New Process
    pid = os.getpid()
    
    if rc == 0:
        for dir in re.split(":", os.environ['PATH']): # Loop through each directory
            launch = "%s/%s" % (dir, userArgs[0])
            try:
                os.execve(launch, userArgs, os.environ) # Executed command
            except FileNotFoundError:
                pass
        os.write(2,("%s: command was not found. Try Agian\n" % userArgs[0]).encode())

    elif rc < 0: # Catches fork error.
        os.write(2,("Unsuccessful fork, returns %d\n" %rc).encode())
        sys.exit(1)

    else:
        childPID = os.wait()

if __name__ == "__main__":
    prompt()