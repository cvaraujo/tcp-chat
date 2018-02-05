# -*- coding: utf-8 -*-
import select
import socket
from client import ClientS
import utils
import sys


class servidor:
    def __init__(self, IP, PORT):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen(10)

        # Adicionando socket à lista de sockets viáveis
        self.channels_list = dict()
        self.clients = []

    # Verifica se o cliente da nova conexão está no Map, se não estiver o método adiciona no clients
    def storage(self, client):
        for c in self.clients:
            if c.getName() == client.getName():
                return True
        self.clients.append(ClientS(client.getName(), client.getAddress(), None, client.getSocket()))
        return False

    # Verifica se o cliente já está no canal que ele deseja entrar, se ele está em algum canal e trata esses casos antes de realocar ele pra outro
    # canal
    def join_channel(self, channel, client):
        if client.getChannel() == channel:
            client.post(utils.CLIENT_WIPE_ME + 'You are already on that channel!' + '\n')
        else:
            if channel in self.channels_list:
                if client.getChannel() in self.channels_list:
                    self.broadcastdata(client, '', utils.SERVER_CLIENT_LEFT_CHANNEL.format(client.getName()))
                    self.channels_list[client.getChannel()].remove(client)
                client.setChannel(channel)
                self.channels_list[channel].append(client)
                self.broadcastdata(client, utils.SERVER_CLIENT_JOINED_CHANNEL.format(client.getName()), '')
            else:
                client.post(utils.CLIENT_WIPE_ME + utils.SERVER_NO_CHANNEL_EXISTS.format(channel) + '\n')

    # Cria canal e realoca o usuário criador para ele
    def createchannel(self, name_channel, client):
        if name_channel in self.channels_list:
            client.post(utils.CLIENT_WIPE_ME + utils.SERVER_CHANNEL_EXISTS.format(name_channel) + '\n')
        else:
            self.channels_list[name_channel] = list()
            self.join_channel(name_channel, client)
            client.post(utils.CLIENT_WIPE_ME + 'Chat criado com sucesso!\n')

    # Lista todos os canais disponíveis
    def listchannels(self, client):
        s = ''
        for ch in self.channels_list.keys():
            s += 'Canal: ' + ch + '\n'
        client.post(s)

    # Função que envia mensagem para todos os cliente conectados de acordo com o canal do cliente que está enviando
    def broadcastdata(self, client, action, message):
        if client.getChannel() is None:
            client.getSocket().send(utils.SERVER_CLIENT_NOT_IN_CHANNEL + '\n')
        elif client.getChannel() in self.channels_list:
            for c in self.channels_list[client.getChannel()]:
                if c != client:
                    try:
                        c.post(utils.CLIENT_WIPE_ME + utils.CLIENT_MESSAGE_PREFIX.format(client.getName()) +
                               ' ' + action + ' ' + message + '\n')
                    except:
                        self.remove(c)

    # Verifica algum socket está solicitanto conexão
    def connect_client(self):
        new_sock, addr = self.server_socket.accept()
        client_name = new_sock.recv(200)
        client_name = client_name.strip()
        c = ClientS(client_name, addr, None, new_sock)
        if self.storage(c):
            c.post('Name already in use!\n')
            c.getSocket().close()
        print 'Client ' + client_name + ' has been connected\n'

    # Lista de sockets conectados a partir do SELECT
    def get_sockets(self):
        s = [self.server_socket] + [cli.getSocket() for cli in self.clients]
        return select.select(s, [], [])[0]

    # Retorna um cliente baseado em um sucket dado como parâmetro
    def get_client(self, socket):
        for client in self.clients:
            if client.getSocket() == socket:
                return client

    # Remove o cliente em caso de erro de socket ou de quit.
    def remove(self, client):
        self.channels_list[client.getChannel()].remove(client)
        self.clients.remove(client)
        client.getSocket().close()
        print 'Client ' + client.getName() + ' has been dsconnected'

    # Remove o usuário que executou o comando do canal atual dele
    def quit(self, client):
        if client.getChannel() is None:
            self.remove(client)
        else:
            client.post('System : You are in Limbo\n')
            self.broadcastdata(client, 'System : ' + utils.SERVER_CLIENT_LEFT_CHANNEL.format(client.getName()), '')
            if len(self.channels_list[client.getChannel()]) == 1:
                del self.channels_list[client.getChannel()]
            else:
                self.channels_list[client.getChannel()].remove(client)
            client.setChannel(None)

    # Verifica se o dado vindo do cliente é um comando
    def is_command(self, inp, client):
        if str(inp[0].startswith('/')):  # Mensagem de comando
            if inp[0] == '/quit':
                self.quit(client)
            if inp[0] == '/join':
                if len(inp) >= 2:
                    self.join_channel(inp[1], client)
                    return False
                else:
                    client.post(utils.CLIENT_WIPE_ME + utils.SERVER_CREATE_REQUIRES_ARGUMENT + '\n')
                    return False
            elif inp[0] == '/create':
                if len(inp) >= 2:
                    self.createchannel(inp[1], client)
                    return False
                else:
                    client.post(utils.CLIENT_WIPE_ME + utils.SERVER_JOIN_REQUIRES_ARGUMENT + '\n')
                    return False
            elif inp[0] == '/list':
                if len(inp) == 1:
                    self.listchannels(client)
                    return False
                else:
                    client.post(utils.CLIENT_WIPE_ME + utils.SERVER_INVALID_CONTROL_MESSAGE.format(inp[0]) + '\n')
                    return False
        return True

    # Mannipula os dados vindos dos clientes
    def get_data(self, client):
        try:
            data = client.getSocket().recv(200)
            if data:
                while len(data) <= 200:
                    data += client.getSocket().recv(200)
                data = data.strip()
                POST = True
                if len(str(data).split()) >= 1:
                    inp = str(data).split()
                    POST = self.is_command(inp, client)
                else:
                    POST = False
                    client.post('You can not send empty messages\n')
                if POST:
                    self.broadcastdata(client, '\r[{}] say: '.format(client.getName()), data)
        except Exception as e:
            self.remove(client)
