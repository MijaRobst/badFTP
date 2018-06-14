import os
import sys
from select import select
import socket

PORT = 2001
T = 5

QUIT = 0
CWD = 1
SEND = 2
RECV = 3

class struct:
    @staticmethod
    def pack(command, data):
        string = str(command) + data
        while (len(string) < 512):
            string += '\x00'
        print string
        return string

    @staticmethod
    def unpack(packet):
        return (int(packet[0]), packet[1:].rstrip('\x00'))


def print_help():
    print("This is some help")


def get_server_cwd(sock):
    sock.send(struct.pack(CWD, ""))
    (r, _, _) = select([sock], [], [], T)
    if (sock in r):
        _, path = struct.unpack(sock.recv(512))
        return path
    else:
        print("Lost connection to server")
        exit(1)


def send_packet(sock, string):
    packet = struct.pack(SEND, string)
    sent = 0
    while (sent < len(packet)):
        sent += sock.send(packet[sent:])


def send(sock, origin, dest):
    try:
        fh = open(origin, "r")
    except:
        print("File " + origin + " doesn't exist!")
        return

    print("Sending file: " + origin + " to " + dest)
    send_packet(sock, dest)
    content = None
    while (content != ""):
        content = fh.read(511)
        send_packet(sock, content)

    print("File sent correctly")


def recv(origin, dest):
    print("Receiving file: " + origin + " to " + dest)


def run_command(sock, command, path):
    if (command[0] == "exit"):
        sock.send(struct.pack(QUIT, ""))
        return (True, path)

    elif (command[0] == "help"):
        print_help()
        return (False, path)

    elif (command[0] == "send"):
        if (len(command) >= 3):
            send(sock, path + "/" + command[1], command[2])
            return (False, path)

    elif (command[0] == "recv"):
        if (len(command) >= 3):
            recv(sock, command[1], path + "/" + command[2])
            return (False, path)

    elif (command[0] == "cd"):
        print("Not implemented yet")
        return (False, path)

    elif (command[0] == "pwd"):
        if (len(command) >= 2):
            if (command[1] == "client"):
                print(path)
                return (False, path)
            elif (command[1] == "server"):
                print(get_server_cwd(sock))
                return (False, path)

    print("Invalid command: " + " ".join(command))
    return (False, path)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print_help()
        exit(0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], PORT))

    path = os.getcwd()
    quit = False
    while(not quit):
        (stdin, _, _) = select([sock, 1], [], [])
        if (1 in stdin):
            command = os.read(1, 512).strip().split()
            quit, path = run_command(sock, command, path)

    print("Everything done")
    exit(0)
