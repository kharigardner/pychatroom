import socket
import threading
import pytest
import pytest_mock
import typing
import time

from pychatroom.client import ChatClient, ClientMode
from pychatroom.server import ChatServer
import sys


# Tests that a client can successfully connect to a chat server in TIMEOUT mode.
def test_start_connection(server: ChatServer):
    client = ChatClient(host=server.host, port=server.port, mode='TIMEOUT')
    client.start()
    assert client.client_socket.fileno() != -1

# Tests that the client can receive messages in KEEPALIVE mode.
def test_receive_messages_keep_alive(server: ChatServer, capsys: pytest.CaptureFixture[str]):
    client = ChatClient(host=server.host, port=server.port)
    client.start()
    message = "Hello, world!"
    server.broadcast(message, client.client_socket)
    assert message in capsys.readouterr().out

# Tests the behavior of the client when multiple clients are connected to the same server.
def test_multiple_clients_connected(server: ChatServer, capsys: pytest.CaptureFixture[str]):
    client1 = ChatClient(host=server.host, port=server.port)
    client2 = ChatClient(host=server.host, port=server.port)
    client1.start()
    client2.start()
    
    time.sleep(1)

    message_1 = "Hello, world! from client 1"
    client1.send_message(message_1)
    time.sleep(1)
    assert message_1 in capsys.readouterr().out
    

    message_2 = "Hello, world! from client 2" 
    client2.send_message(message_2)
    time.sleep(1)
    assert message_2 in capsys.readouterr().out

# Tests that the client can receive messages in TIMEOUT mode.
def test_receive_messages_timeout(server: ChatServer, capsys: pytest.CaptureFixture[str]):
    client = ChatClient(host=server.host, port=server.port, mode=ClientMode.TIMEOUT, timeout=1)
    client.start()

    time.sleep(0.5)

    message = "Hello, world!"
    client.send_message(message)

    time.sleep(0.1)
    assert message in capsys.readouterr().out

# Tests that the client can handle an invalid mode being specified.
def test_invalid_mode_specified(server: ChatServer):
    with pytest.raises(ValueError):
        ChatClient(host=server.host, port=server.port, mode="INVALID")

# Tests that the client can successfully send a message to the chat server.
def test_send_message(server: ChatServer, capsys: pytest.CaptureFixture[str]):
    client = ChatClient(host=server.host, port=server.port)
    client.start()

    time.sleep(1)
    
    message = "Hello, world!"
    client.send_message(message)

    time.sleep(1)
    
    assert message in capsys.readouterr().out

# Tests that the client can close the connection gracefully.
def test_close_connection_gracefully(server: ChatServer):
    client = ChatClient(host=server.host, port=server.port)
    client.start()
    client.client_socket.close()
    assert client.client_socket.fileno() == -1