# -*- coding: utf-8 -*-

import select
import sys
import utils
from client import Client


def prompt():
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()


# main function
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print 'Usage: archive.py username server_number server_port'
        sys.exit()

    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    client = Client(name, (host, port), None)

    try:
        client.getSocket().connect((host, port))
        client.getSocket().send(name)
    except:
        print utils.CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()

    print 'Conectado ao servidor!'
    prompt()

    while 1:
        try:
            socket_list = [sys.stdin, client.getSocket()]
            # Pegando a lista de sockets disponiveis
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                # Recebendo mensagens do servidor
                if sock == client.getSocket():
                    data = sock.recv(200)
                    if not data:
                        print utils.CLIENT_SERVER_DISCONNECTED.format(client.getAddress())
                        sys.exit()
                    else:
                        sys.stdout.write(data)
                        prompt()
                # Mensagem do usuário
                else:
                    message = sys.stdin.readline()
                    if len(message) < 200:
                        for i in range(len(message), 201):
                            message += ' '
                    client.getSocket().send(message)
                    prompt()
        except KeyboardInterrupt:
            sys.stdout.write('\nBye!\n')
            client.disconnetc()
            sys.exit()