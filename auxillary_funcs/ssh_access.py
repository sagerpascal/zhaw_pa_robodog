from invoke import Responder
from fabric import Connection, Config
from time import sleep
import multiprocessing
import subprocess


def check_connection():
    command = ['ping', '-c', '1', '192.168.123.12']
    return subprocess.call(command) == 0


def get_ssh_connection():
    c = Connection(host='192.168.123.12', user='unitree', connect_kwargs={"password": "123"})
    return c


class NoConnectionError(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message
