# Distributed Systems Labs

This repository contains the lab assignments for the Distributed Systems class. Each lab focuses on different aspects of
distributed systems, including networking, concurrency, and communication between distributed components.

## Lab 1: Socket Programming with Threads

### Description

In Lab 1, we implemented a multi-threaded socket server and client in Python. The server can handle multiple clients
simultaneously, forwarding messages between them and maintaining a history of communications. The server uses a task
queue to manage messages that need to be processed and ensures that each message is handled by the appropriate client
thread.

### Key Features

- **Multi-threaded Server**: The server can handle multiple client connections concurrently using Python's `threading`
  module.
- **Task Queue**: A `Queue` is used to manage tasks (messages) that need to be processed by specific client threads.
- **Client ID Management**: Each client is assigned a unique ID upon connection, which is used to route messages.
- **Message Forwarding**: Clients can send messages to other clients via the server, which forwards the messages to the
  appropriate client thread.
- **History Tracking**: The server maintains a history of all messages sent and received for each client.

### Files

- `lab1/socket_server_thread.py`: Contains the implementation of the multi-threaded socket server.
- `lab1/socket_client.py`: Contains the implementation of the socket client that connects to the server.

### How to Run

1. **Start the Server**:

```sh
SERVER_IP=127.0.0.1 SERVER_PORT=9999 python socket_server_thread.py
```

2. **Start the Client**:

```sh
SERVER_IP=127.0.0.1 SERVER_PORT=9999 python socket_client.py
```

3. **Interact with the Client**:
   Clients can send messages, request the list of active clients, request message history, and forward messages to other
   clients.

### Demo
[Link](https://youtu.be/fyPZQ3c1wrQ)
