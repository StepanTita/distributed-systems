import sys

sys.path.append('../scripts')

import os
import uuid
import random
import socket
import threading
import queue
import logger

# Server IP and port configuration
ip_port = (os.getenv('SERVER_IP'), int(os.getenv('SERVER_PORT')))

# List of famous people for generating random client IDs
famous_people = [
    "gauss", "dijkstra", "turing", "curie", "newton",
    "einstein", "lovelace", "hopper", "babbage", "tesla"
]


def get_random_name_id():
    """Generate a random name ID from the list of famous people."""
    return random.choice(famous_people) + '-' + str(uuid.uuid4())


class Server:
    def __init__(self, queue_limit=5):
        """Initialize the server with a queue limit and set up necessary data structures."""
        self.queue_limit = queue_limit
        self.clients = {}
        self.clients_rev = {}
        self.active_clients = set()
        self.history = {}
        self.task_queue = queue.Queue()
        self.client_connections = {}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ip_port)
        self.log = logger.get_logger('../logs', 'socket_server.log', 'socket_server')

    def list_active_clients(self):
        """Return a list of active client IDs."""
        return list(self.active_clients)

    def forward(self, client_id, msg):
        """Forward a message to the specified client by putting it in the task queue."""
        self.task_queue.put((client_id, msg))
        return f'Message forwarded to {client_id}'

    def handle(self, conn, address):
        """Handle communication with a connected client."""
        self.log.info(f'server start to receiving msg from [{address[0]}:{address[1]}]...')
        if address not in self.clients:
            client_id = get_random_name_id()
            self.clients[address] = client_id
            self.clients_rev[client_id] = address
            self.history[client_id] = []

        client_id = self.clients[address]
        self.active_clients.add(client_id)
        self.client_connections[client_id] = conn

        conn.sendall(client_id.encode())
        self.history[client_id].append({'role': 'server', 'msg': f'connected with id: {client_id}'})

        while True:
            try:
                client_data = conn.recv(1024).decode()
                if not client_data:
                    break
                self.log.info(f'client from [{address[0]}:{address[1]}]-(id:{client_id}) send a msg：{client_data}')
                self.history[client_id].append({'role': 'client', 'msg': client_data})

                if client_data == "list":
                    msg = f'active clients: {self.list_active_clients()}'
                    conn.sendall(msg.encode())
                elif client_data.startswith('history'):
                    hist_client_id = client_data.split(' ')[-1]
                    msg = self.history[hist_client_id]
                    conn.sendall(str(msg).encode())
                elif client_data.startswith('forward'):
                    forw_client_id = client_data.split(' ')[-1]
                    msg = ' '.join([f'{client_id}:'] + client_data.split(' ')[1:-1])
                    conn.sendall(self.forward(forw_client_id, msg).encode())
                elif client_data == "exit":
                    self.log.info(f'communication end with [{address[0]}:{address[1]}]-(id:{client_id})...')
                    conn.sendall('Goodbye'.encode())
                    self.history[client_id].append({'role': 'server', 'msg': 'Goodbye'})
                    break
                else:
                    msg = 'server had received your msg'
                    conn.sendall(msg.encode())

                self.history[client_id].append({'role': 'server', 'msg': msg})

            except Exception as e:
                self.log.error(f'Error handling client {client_id}: {e}')
                break

        self.active_clients.remove(client_id)
        del self.client_connections[client_id]
        conn.close()

    def process_queue(self):
        """Process tasks from the queue and send messages to the appropriate clients."""
        while True:
            task_client_id, task_msg = self.task_queue.get()
            if task_client_id in self.client_connections:
                conn = self.client_connections[task_client_id]
                try:
                    conn.sendall(task_msg.encode())
                    self.history[task_client_id].append({'role': 'server', 'msg': task_msg})
                except Exception as e:
                    self.log.error(f'Error sending message to client {task_client_id}: {e}')

    def start(self):
        """Start the server and listen for incoming connections."""
        self.log.info(f'server start to listen on [{ip_port[0]}:{ip_port[1]}]')
        self.server.listen(self.queue_limit)

        # Start the background thread for processing the queue
        threading.Thread(target=self.process_queue, daemon=True).start()

        while True:
            conn, address = self.server.accept()
            self.log.info(f'create a new thread to receive msg from [{address[0]}:{address[1]}]')
            t = threading.Thread(target=self.handle, args=(conn, address))
            t.start()


if __name__ == '__main__':
    server = Server()
    server.start()
