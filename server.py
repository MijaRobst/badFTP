import socket
import os
import signal
from select import select

PORT = 2000


def manageConnection(socket):
    quit = False
    while (not quit):
        (r, _, _) = select([socket], [], [])
        command = socket.recv(512).strip().split()
        if (command[0] == "exit"):
            quit = True
        elif (command[0] == "cwd"):
            socket.send(os.getcwd())
        elif (command[0] == "send"):
            pass  # Receive packet (fragmented if necessary)
        elif (command[0] == "recv"):
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
            incoming.close()
            connection.close()
            exit(0)
    exit(1)
