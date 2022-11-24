from multiprocessing.connection import Listener, Client

ADDRESS = 'localhost'
AUTHKEY = b'zhaw'
GESTREC_PORT = 4444
COMMAND_PORT = 8888
MSG_GESTREC_ON = 'gestrecon'
MSG_GESTREC_OFF = 'gestrecoff'


def get_conn_listener(port):
    listener = Listener((ADDRESS, port), authkey=AUTHKEY)
    return listener


def get_conn_client(port):
    return Client((ADDRESS, port), authkey=AUTHKEY)
