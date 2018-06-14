import socket
import os
import signal
from select import select

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
        return string

    @staticmethod
    def unpack(packet):
        return (int(packet[0]), packet[1:].rstrip('\x00'))


def manageConnection(socket):
    quit = False
    path = os.getcwd()
    while (not quit):
        (r, _, _) = select([socket], [], [])
        command, data = struct.unpack(socket.recv(512))
        print command, data
        if (command == QUIT):
            quit = True
            print("Finishing connection: " + ip[0])

        elif (command == CWD):
            socket.send(struct.pack(CWD, path))

        elif (command == SEND):
            fh = open(path + "/" + data, "w")
            print("Opened " + path + "/" + data)
            r, _, _ = select([socket], [], [], T)
            if (socket not in r):
                print("Lost connection with client")
                exit(1)
            command, data = struct.unpack(socket.recv(512))

            while (data != ""):
                if (command != SEND):
                    print("Error receiving data")
                    exit(1)

                fh.write(data)

                r, _, _ = select([socket], [], [], T)
                if (socket not in r):
                    print("Lost connection with client")
                    exit(1)
                command, data = struct.unpack(socket.recv(512))

        elif (command == RECV):
            pass  # Send packet (fragmented if necessary)
    exit(0)


if(__name__ == "__main__"):
    incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incoming.bind(("0.0.0.0", PORT))
    incoming.listen(5)
    while(True):
        (connection, ip) = incoming.accept()
        if (os.fork() == 0):
            manageConnection(connection)
        else:
            print("Connection received! " + ip[0])
    exit(1)
