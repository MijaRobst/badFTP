"""badFTP's client."""
import os
import sys
from select import select
import socket
import logistics as logs


def print_help():
    """Print the client's help."""
    print("This is some help")


def get_server_ls(sock):
    """Perform ls in the server."""
    return logs.sendTCP(sock, logs.LS, "", True)


def get_server_cwd(sock):
    """Get server's current working directory."""
    return logs.sendTCP(sock, logs.CWD, "", True)


def server_cd(sock, newpath):
    """Perform cd in the server."""
    logs.sendTCP(sock, logs.CD, newpath)


def run_command(sock, command, path):
    """Run the given command."""
    if (command[0] == "bye" or command[0] == "exit"):
        logs.sendTCP(sock, logs.QUIT, "")
        return (True, path)

    elif (command[0] == "help"):
        print_help()
        return (False, path)

    elif (command[0] == "cd"):
        if (len(command) == 2):
            path = logs.changedir(path, command[1])
            return (False, path)
        if (len(command) >= 3):
            if (command[1] == "client"):
                path = logs.changedir(path, command[2])
                return (False, path)
            elif (command[1] == "server"):
                server_cd(sock, command[2])
                return (False, path)

    elif (command[0] == "ls"):
        if (len(command) < 2 or command[1] == "client"):
            print logs.ls(path)
            return (False, path)
        elif (command[1] == "server"):
            print(get_server_ls(sock))
            return (False, path)

    elif (command[0] == "pwd"):
        if (len(command) < 2 or command[1] == "client"):
            print(path)
            return (False, path)
        elif (command[1] == "server"):
            print(get_server_cwd(sock))
            return (False, path)

    elif (command[0] == "send"):
        if (len(command) >= 3):
            origin = logs.get_new_dir(path,  command[1])
            if (origin):
                fh = open(origin, "r")
            else:
                print("File " + command[1] + " doesn't exist!")
                return(False, path)

            print("Sending file: " + origin)
            logs.sendTCP(sock, logs.SEND, command[2])
            logs.send(sock, fh)
            fh.close()
            return (False, path)

    elif (command[0] == "recv"):
        lst = command[2].split("/")
        if (len(lst) < 2):
            relpath = path
        else:
            relpath = logs.get_new_dir(path, "/".join(lst[:-1]))
        filename = lst[-1]
        if (not relpath):
            print ("/".join(lst[:-1]) + " does not exist!")
            return (False, path)

        if (len(command) >= 3):
            logs.sendTCP(sock, logs.RECV, command[1])
            logs.recv(sock, relpath + "/" + filename)
            return (False, path)

    print("Invalid command: " + " ".join(command))
    return (False, path)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print_help()
        exit(0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], logs.PORT))

    path = os.getcwd()
    quit = False
    while(not quit):
        (stdin, _, _) = select([sock, 1], [], [])
        if (1 in stdin):
            command = os.read(1, 512).strip().split()
            print("\n")
            quit, path = run_command(sock, command, path)
            print("\n")
    print("Bye!")
    exit(0)
