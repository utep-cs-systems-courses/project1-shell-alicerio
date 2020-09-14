import os, sys, re

if __name__ == "__main__":
    while True:
        command = input("Please enter a command:" + "\n" + "$ ")
        if command == "exit":
            break
        elif command == "help":
            print("Help")
        elif command[:2] == "cd":
            print("Change dir")
        else:
            print("Try Again!")