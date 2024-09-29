# -*- coding:utf-8 -*-

import sys

# Add the scripts directory to the system path
sys.path.append('../scripts')

import os
import socket
import select
import logger

# Server IP and port configuration
ip_port = (os.getenv('SERVER_IP'), int(os.getenv('SERVER_PORT')))


class Client:
    def __init__(self):
        """Initialize the client and connect to the server."""
        self.s = socket.socket()
        self.s.connect(ip_port)
        self.log = logger.get_logger('../logs', 'socket_client.log', 'socket_client')

    def start(self):
        """Start the client to communicate with the server."""
        client_id = self.s.recv(1024).decode()
        self.log.info(f'connected with id: {client_id}')

        while True:
            # Use select to monitor both the socket and standard input
            readable, _, _ = select.select([self.s, sys.stdin], [], [])
            for r in readable:
                if r == self.s:
                    # Handle server messages
                    server_reply = self.s.recv(1024).decode()
                    if not server_reply:
                        self.log.warn('Server closed the connection')
                        return
                    self.log.info(server_reply)
                elif r == sys.stdin:
                    # Handle user input
                    inp = input().strip()
                    if inp:
                        self.s.sendall(inp.encode())
                        if inp == "exit":
                            server_reply = self.s.recv(1024).decode()
                            self.log.warn(server_reply)
                            self.s.close()
                            return


if __name__ == '__main__':
    client = Client()
    client.start()