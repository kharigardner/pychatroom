import socket
import threading
import pytest
import pytest_mock
import typing
import time

from pychatroom.server import ChatServer


# Tests that the server successfully accepts a connection and sends a welcome message to the client.
def test_successful_connection(server: ChatServer):
    """
    Tests that the server successfully accepts a connection and sends a welcome message to the client.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.host, server.port))
    response = client_socket.recv(2048).decode('utf-8')
    assert response == 'Welcome to the chat room!'
    client_socket.close()

# Tests that multiple clients can connect to the server and communicate with each other.
def test_multiple_clients(server: ChatServer):
    """
    Tests that multiple clients can connect to the server and communicate with each other.
    """
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((server.host, server.port))
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect((server.host, server.port))
    
    welcome_response = client1.recv(2048).decode('utf-8')
    assert welcome_response == 'Welcome to the chat room!'
    welcome_response = client2.recv(2048).decode('utf-8')
    assert welcome_response == 'Welcome to the chat room!'

    client1.send('Hello from client 1'.encode('utf-8'))
    response = client2.recv(2048).decode('utf-8')
    assert response == '<127.0.0.1> Hello from client 1'
    client2.send('Hello from client 2'.encode('utf-8'))
    response = client1.recv(2048).decode('utf-8')
    assert response == '<127.0.0.1> Hello from client 2'
    
    client1.close()
    client2.close()

# Tests that the server properly handles a client disconnecting unexpectedly and removes the disconnected client from the list of active sockets.
def test_client_disconnect(server: ChatServer):
    """
    Tests that the server properly handles a client disconnecting unexpectedly and removes the disconnected client from the list of active sockets.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.host, server.port))
    client_socket.close()
    assert client_socket not in server.SOCKETS

# Tests that the server properly handles receiving an empty message and closes the connection.
def test_empty_message(server: ChatServer):
    """
    Tests that the server properly handles receiving an empty message and closes the connection.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.host, server.port))
    client_socket.send(''.encode('utf-8'))
    assert client_socket not in server.SOCKETS

# Tests that the server properly handles receiving a message that exceeds the maximum message size and closes the connection.
def test_max_message_size(server: ChatServer):
    """
    Tests that the server properly handles receiving a message that exceeds the maximum message size and closes the connection.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.host, server.port))
    message = 'a' * 4096
    client_socket.send(message.encode('utf-8'))
    assert client_socket not in server.SOCKETS

# Tests the behavior of the broadcast method when a client fails to receive a message.
def test_broadcast_failure(server: ChatServer):
    """
    Tests the behavior of the broadcast method when a client fails to receive a message.
    """
    # Connect two clients
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((server.host, server.port))
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect((server.host, server.port))

    # Close one of the clients
    client2.close()

    # Send message from remaining client
    client1.send('Hello from client 1'.encode('utf-8'))

    # Check that no exception is raised when broadcasting to disconnected client
    try:
        server.broadcast('<127.0.0.1> Hello from client 1', client2)
    except Exception as e:
        pytest.fail(f'Unexpected exception raised: {e}')