# -*- coding: utf-8 -*-
import socket
import sys

from server import servidor

if __name__ == "__main__":

    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    server = servidor(IP, PORT)

    print 'Servidor de chat iniciado na porta: ' + str(PORT)

    while 1:
        try:
            for sock in server.get_sockets():
                # Nova conexão
                if sock == server.server_socket:
                    server.connect_client()
                else:
                    # Caso não haja nova conexão, manter fluxo de dados
                    server.get_data(server.get_client(sock))
        except KeyboardInterrupt:
            sys.exit()
