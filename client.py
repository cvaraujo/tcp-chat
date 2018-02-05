# --*-- coding: utf-8 --*--
import socket
# --*-- coding: utf-8 --*--
import socket


class ClientS:
    def __init__(self, name, address, channel, socket):
        self.name = name
        self.address = address
        self.channel = channel
        self.socket = socket

    def __eq__(self, o):
        if type(self) == type(o):
            return self.name == o.name and self.socket == o.socket and self.channel == o.channel
        return False

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getAddress(self):
        return self.address

    def setAddress(self, address):
        self.address = address

    def getChannel(self):
        return self.channel

    def setChannel(self, channel):
        self.channel = channel

    def getSocket(self):
        return self.socket

    def setSocket(self, socket):
        self.socket = socket

    def post(self, message):
        self.socket.send(message.encode())


class Client:
    def __init__(self, name, address, channel):
        self.name = name
        self.address = address
        self.channel = channel

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getAddress(self):
        return self.address

    def setAddress(self, address):
        self.address = address

    def getChannel(self):
        return self.channel

    def setChannel(self, channel):
        self.channel = channel

    def getSocket(self):
        return self.socket

    def setSocket(self, socket):
        self.socket = socket
    def disconnetc(self):
        self.socket.close()