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
    @staticmethod
    def pack(command, data):
        string = str(command) + data
        while (len(string) < 512):
            string += '\x00'
        return string

    @staticmethod
    def unpack(packet):
        return (int(packet[0]), packet[1:].rstrip('\x00'))


def sendTCP(sock, packtype, data, waitans=False):
    packet = struct.pack(packtype, data)
    sent = 0
    while (sent < len(packet)):
        sent += sock.send(packet[sent:])

    if (waitans):
        (r, _, _) = select([sock], [], [], T)
        if (sock in r):
            anstype, ans = struct.unpack(sock.recv(512))
            if (packtype != anstype):
                print("Wrong packet type (expected %d, got %d)" % (packtype, anstype))
                exit(1)
            return ans
        else:
            print("Lost connection to server")
            exit(1)


def ls(path):
    return "\n".join(os.listdir(path))


def get_new_dir(path, movements):
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
    new = get_new_dir(currentpath, relpath)
    if (not new):
        print(relpath + " does not exist")
        return currentpath
    return new


def send(sock, fh):
    content = None
    while (content != ""):
        content = fh.read(511)
        sendTCP(sock, SEND, content)
    print("File sent correctly")


def recv(sock, dest):
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
