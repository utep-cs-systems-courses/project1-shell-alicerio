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
    elif '|' in command:
        pipe(userArgs)
    elif '<' in command:
        redirectInput(userArgs)
    elif '>' in command:
        redirectOutput(userArgs)
    else:
        execute(userArgs)

def pipe(userArgs):
    pid = os.getpid()
    pipe = userArgs.index("|") # Pipe symbol
    pr, pw = os.pipe()
    for i in (pr,pw):
        os.set_inheritable(i, True)
    rc = os.fork()
    if rc == 0:
        userArgs = userArgs[:pipe]
        os.close(1)
        fd = os.dup(pw) # Duplicate
        os.set_inheritable(fd, True)
        for fd in (pr,pw):
            os.close(fd)
        if os.path.isfile(userArgs[0]):
            try:
                os.execve(userArgs[0],userArgs,os.environ)
            except FileNotFoundError: # Skip if file does not exist
                pass
        else:
            for dir in re.split(":", os.environ['PATH']): # Loop directory
                launch = "%s/%s" % (dir,userArgs[0])
                try:
                    os.execve(launch, userArgs, os.environ)
                except FileNotFoundError:
                    pass
            os.write(2,("%s: command was not found. Try Agian\n" % userArgs[0]).encode())
            sys.exit(1)

    elif rc < 0: # Fork error
        os.write(2,("Unsuccessful fork, returns %d\n" %rc).encode())
        sys.exit(1)

    else:
        userArgs = userArgs[pipe+1:]
        os.close(0)
        fd = os.dup(pr)
        os.set_inheritable(fd,True)
        for fd in (pw,pr):
            os.close(fd)
        if os.path.isfile(userArgs[0]):
            try:
                os.execve(userArgs[0],userArgs,os.environ)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):
                launch = "%s/%s" % (dir,userArgs[0])
                try:
                    os.execve(launch, userArgs, os.environ)
                except FileNotFoundError:
                    pass
            os.write(2,("%s: command was not found. Try Agian\n" % userArgs[0]).encode())
            sys.exit(1)

def redirectInput(userArgs):
    pid = os.getpid()
    rc = os.fork()
    if rc == 0:
        del userArgs[1]
        fd = sys.stdout.fileno()
        try:
            os.execve(userArgs[0],userArgs,os.environ)
        except FileNotFoundError:
            pass
        for dir in re.split(":",os.environ['PATH']):
            launch = "%s/%s" % (dir,userArgs[0])
            try:
                os.execve(launch, userArgs, os.environ)
            except FileNotFoundError:
                pass
            os.write(2,("%s: command was not found. Try Agian\n" % userArgs[0]).encode())
            sys.exit(1)
    elif rc < 0: # Fork error
        os.write(2,("Unsuccessful fork, returns %d\n" %rc).encode())
        sys.exit(1)
    else:
        childPID = os.wait()


def redirectOutput(userArgs):
    i = userArgs.index('>') + 1 # Sets index
    fileName = userArgs[i]
    userArgs = userArgs[:i - 1]
    pid = os.getpid()
    rc = os.fork()

    if rc == 0:
        os.close(1)
        sys.stdout = open(fileName, 'w') # Write to file
        os.set_inheritable(1,True)
        
        if os.path.isfile(userArgs[0]): # If file exists
            try:
                os.execve(userArgs[0],userArgs,os.environ)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":",os.environ['PATH']):
                launch = "%s/%s" % (dir,userArgs[0])
                try:
                    os.execve(launch, userArgs, os.environ)
                except FileNotFoundError:
                    pass
                os.write(2,("%s: command was not found. Try Agian\n" % userArgs[0]).encode())
                sys.exit(1)
    elif rc < 0: # Fork error
        os.write(2,("Unsuccessful fork, returns %d\n" %rc).encode())
        sys.exit(1)
    else:
        childPID = os.wait()


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