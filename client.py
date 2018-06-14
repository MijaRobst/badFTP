import os
import sys
from select import select
import socket

PORT = 2000
T = 5


def print_help():
    print("This is some help")


def get_server_cwd(sock):
    sock.send("cwd")
    (r, _, _) = select([sock], [], [], T)
    if (sock in r):
        path = sock.recv(512).strip()
        return path
    else:
        print("Lost connection to server")
        exit(1)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print_help()
        exit(0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], PORT))

    clientpath = os.getcwd()
    serverpath = get_server_cwd(sock)
    quit = False
    while(not quit):
        (stdin, _, _) = select([sock, 1], [], [])
        if (1 in stdin):
            command = os.read(1, 512).strip().split()
            if (command[0] == "exit"):
                quit = True
                sock.send("exit")
            elif (command[0] == "help"):
                print_help()
            elif (command[0] == "send"):
                print("Sending file: " + clientpath + "/" + command[1] + " to " + serverpath + "/" + command[2])
            elif (command[0] == "recv"):
                print("Receiving file: " + serverpath + "/" + command[1] + " to " + clientpath + "/" + command[2])

    print("Everything done")
    exit(0)
