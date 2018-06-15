"""Miscellaneous constants and functions for badFTP."""
from select import select
import os

PORT = 2000
T = 5

QUIT = 0
CWD = 1
LS = 2
CD = 3
SEND = 4
RECV = 5
ERR = 6


class struct:
    """Methods to pack and unpack messages."""

    @staticmethod
    def pack(command, data):
        """Pack a command and data into a string."""
        string = str(command) + data
        while (len(string) < 512):
            string += '\x00'
        return string

    @staticmethod
    def unpack(packet):
        """Unpack a string into a command and data."""
        return (int(packet[0]), packet[1:].rstrip('\x00'))


def sendTCP(sock, packtype, data, waitans=False):
    """
    Send a TCP packet with type packtype and given data.

    If waitans is true, wait and return the data in its answer.
    """
    packet = struct.pack(packtype, data)
    sent = 0
    while (sent < len(packet)):
        sent += sock.send(packet[sent:])

    if (waitans):
        (r, _, _) = select([sock], [], [], T)
        if (sock in r):
            anstype, ans = struct.unpack(sock.recv(512))
            if (packtype != anstype):
                print("Wrong packet type (expected %d, got %d)" %
                      (packtype, anstype))
                exit(1)
            return ans
        else:
            print("Lost connection to server")
            exit(1)


def ls(path):
    """Return the contents of path, one line each."""
    return "\n".join(os.listdir(path))


def get_new_dir(path, movements):
    """Return the result of applying the movements to the given path."""
    currentdirs = path.split("/")
    dirs = movements.rstrip("/").split("/")
    for dir in dirs:
        if (dir == "."):
            pass
        elif (dir == ".."):
            currentdirs = currentdirs[:-1]
        elif (dir in os.listdir("/".join(currentdirs))):
            currentdirs += [dir]
        else:
            return None
    return "/".join(currentdirs)


def changedir(currentpath, relpath):
    """
    Return the new path applying the relpath to currentpath if it exists.

    If the path does not exist, return currentpath.
    """
    new = get_new_dir(currentpath, relpath)
    if (not new):
        print(relpath + " does not exist")
        return currentpath
    return new


def send(sock, fh):
    """Send a file described by fh through sock."""
    content = None
    while (content != ""):
        content = fh.read(511)
        sendTCP(sock, SEND, content)
    print("File sent correctly")


def recv(sock, dest):
    """Receive a file at dest through sock."""
    fh = open(dest, "w")
    print("Opened " + dest)
    r, _, _ = select([sock], [], [], T)
    if (sock not in r):
        print("Lost connection")
        exit(1)
    command, data = struct.unpack(sock.recv(512))

    while (data != ""):
        if (command == ERR):
            print("Error receiving data: " + data)

        fh.write(data)

        r, _, _ = select([sock], [], [], T)
        if (sock not in r):
            print("Lost connection")
            exit(1)
        command, data = struct.unpack(sock.recv(512))
    fh.close()
