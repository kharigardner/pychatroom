import socket
import threading
import typing
import collections
import logging
import sys

HOST = 'localhost'
PORT = 9999

class ChatServer:
    """
    A class representing a chat server that listens for incoming connections
    and broadcasts messages to all connected clients.
    """
    def __init__(self, host: str = HOST, port: int = PORT, mode = 'DEBUG') -> None:
        self.logger = logging.getLogger(__name__)
        log_level = logging.DEBUG if mode == 'DEBUG' else logging.WARN
        self.logger.setLevel(log_level)
        self.host = host
        self.port = port
        self.mode = mode
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.SOCKETS = [self.server_socket]
        
    def start(self):

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)

        while True:
            client_socket, client_address = self.server_socket.accept()
            
            self.logger.warn(f'Accepted connection from {client_address}')
            self.logger.warn(f'Socketname: {client_socket.getsockname()}, fileno: {client_socket.fileno()}')

            self.SOCKETS.append(client_socket)

            thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            thread.setDaemon(True)
            thread.start()

    def handle_client(self, conn: socket.socket, client_address: typing.Tuple[str, int]):
        conn.send('Welcome to the chat room!'.encode('utf-8'))
        while True:
            try:
                message = conn.recv(2048)
                logging.warn(f'Received message from {client_address}: {message.decode("utf-8")}')
                if message:
                    msg_to_send = f'<{client_address[0]}> {message.decode("utf-8")}'
                    self.broadcast(msg_to_send, conn)

                else:
                    logging.warn('Message is empty... closing connection')
                    conn.close()
                    self.SOCKETS.remove(conn)
            except Exception as e:
                if isinstance(e, OSError):
                    logging.error('Panic...an OS error was caught')
                    continue

                else:
                    continue


    def broadcast(self, msg: str, conn: socket.socket):
        for client in self.SOCKETS:
            if client != conn:
                try:
                    client.send(msg.encode('utf-8'))
                except Exception as e:
                    if self.mode == 'DEBUG':
                        self.logger.error(e)
                    else:
                        self.logger.warn(e)
                        client.close()
                        self.SOCKETS.remove(client)

if __name__ == '__main__':
    server = ChatServer()
    server.start()