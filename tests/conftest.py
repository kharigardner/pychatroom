import pytest
from pychatroom.client import ChatClient
from pychatroom.server import ChatServer
import threading

@pytest.fixture(scope='session')
def server():
    server = ChatServer(host='localhost', port=8001)
    threading.Thread(target=server.start).start()
    yield server
    server.server_socket.close()