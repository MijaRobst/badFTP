import socket
import os
import signal
from select import select
import logistics as logs


def manageConnection(socket):
    quit = False
    path = os.getcwd()
    while (not quit):
        (r, _, _) = select([socket], [], [])
        command, data = logs.struct.unpack(socket.recv(512))
        print command, data
        if (command == logs.QUIT):
            quit = True

        elif (command == logs.CWD):
            logs.sendTCP(socket, logs.CWD, path)

        elif (command == logs.LS):
            logs.sendTCP(socket, logs.LS, logs.ls(path))

        elif (command == logs.CD):
            path = logs.changedir(path, data)

        elif (command == logs.SEND):
            lst = data.split("/")
            if (len(lst) < 2):
                relpath = path
            else:
                relpath = logs.get_new_dir(path, "/".join(lst[:-1]))
            filename = lst[-1]
            if (not relpath):
                print("/".join(lst[:-1]) + " does not exist!")
                continue
            logs.recv(socket, relpath + "/" + filename)

        elif (command == logs.RECV):
            origin = logs.get_new_dir(path, data)
            if (origin):
                fh = open(origin, "r")
            else:
                logs.sendTCP(socket, logs.ERR, "File does not exist")
                continue

            print("Sending file: " + origin)
            logs.send(socket, fh)

    print("Finishing connection: " + ip[0])
    socket.close()
    exit(0)


if(__name__ == "__main__"):
    incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incoming.bind(("0.0.0.0", logs.PORT))
    incoming.listen(5)
    while(True):
        (connection, ip) = incoming.accept()
        if (os.fork() == 0):
            manageConnection(connection)
        else:
            print("Connection received! " + ip[0])
    exit(1)
