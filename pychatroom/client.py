import socket
import threading
import typer
import typing
import logging
import sys
from pychatroom.server import ChatServer
import enum

HOST = 'localhost'
PORT = 9999

app = typer.Typer()

class ClientMode(enum.Enum):
    KEEPALIVE = 'KEEPALIVE'
    TIMEOUT = 'TIMEOUT'
    
class ChatClient:
    """
    A client for connecting to a chat server and sending/receiving messages.

    Args:
        host (str, optional): The hostname or IP address of the chat server. Defaults to 'localhost'.
        port (int, optional): The port number of the chat server. Defaults to 9999.
        mode (Union[ClientMode, str], optional): The mode of the client. Can be either 'KEEPALIVE' or 'TIMEOUT'. Defaults to ClientMode.KEEPALIVE.
        timeout (int, optional): The timeout value in seconds for the 'TIMEOUT' mode. Defaults to None.

    Attributes:
        host (str): The hostname or IP address of the chat server.
        port (int): The port number of the chat server.
        mode (ClientMode): The mode of the client.
        timeout (int): The timeout value in seconds for the 'TIMEOUT' mode.
    """

    def __init__(self, host: str = HOST, port: int = PORT, mode: typing.Union[ClientMode, str] = ClientMode.KEEPALIVE, timeout: typing.Optional[int] = None) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

        if isinstance(mode, str):
            self.mode = ClientMode(mode)
        else:
            self.mode = mode
        
        if self.mode == ClientMode.TIMEOUT:
            self.timeout = timeout or 10
    
    def start(self):
        
        self.logger.info(f'Connecting to {self.host}:{self.port}')

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        self.logger.info(f'Connected to {self.host}:{self.port}')

        
        thread = threading.Thread(target=self.receive_messages)
        thread.setDaemon(True)
        thread.start()
    
    def receive_messages(self):
        if self.mode == ClientMode.KEEPALIVE:
            self.keep_alive_mode()
        elif self.mode == ClientMode.TIMEOUT:
            self.timeout_mode()
        else:
            raise ValueError(f'Unknown mode {self.mode}')

    def timeout_mode(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    sys.stdout.write(message)
                    sys.stdout.flush()
                else:
                    self.logger.warn('Message is empty... closing connection')
                    self.client_socket.close()
                    break
            except socket.timeout:
                if not self.client_socket.fileno():
                    self.logger.warn('Connection closed...')
                    break
    
    def keep_alive_mode(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    sys.stdout.write(message)
                    sys.stdout.flush()
                else:
                    self.logger.warn('Message is empty... closing connection')
                    self.client_socket.close()
                    break
            except Exception as e:
                self.logger.error(e)
                self.client_socket.close()
                break

    def send_message(self, msg: str):
        self.client_socket.sendall(msg.encode())

import time

# create the cli withtyper
@app.command()
def main(host: str = HOST, port: int = PORT, mode: typing.Union[ClientMode, str] = ClientMode.KEEPALIVE, timeout: typing.Optional[int] = None):
    client = ChatClient(host=host, port=port, mode=mode, timeout=timeout)
    client.start()

    time.sleep(0.1)

    while True:
        msg = input()
        if msg == 'exit':
            break
        client.send_message(msg)
        if client.mode == ClientMode.TIMEOUT:
            print('Timeout mode activated... connection will close if no message received in {} seconds'.format(client.timeout))

if __name__ == '__main__':
    app()
