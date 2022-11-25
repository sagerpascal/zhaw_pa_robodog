from invoke import Responder
from fabric import Connection
from time import sleep
from multiprocessing import Process, current_process
from threading import Thread
import subprocess
import sys

from auxillary_funcs.ssh_access import get_ssh_connection, check_connection
from auxillary_funcs.interprocess_comms import get_conn_listener, get_conn_client, COMMAND_PORT

COMMAND_SIT = 'sudo ./sit.sh'
COMMAND_STAND = 'sudo ./stand.sh'
COMMAND_WALK = 'sudo ./walk.sh'

_procs = []


class CommandExecutor():

    def __init__(self) -> None:
        self._sit_process = Process()
        self._cmd_thread = Thread()
        self._sudopass = Responder(
            pattern=r'\[sudo\] password for unitree:',
            response='123\n')

    def start(self):
        if check_connection() or True:
            proc = Process(target=self.__start_listener__)
            _procs.append(proc)
            proc.start()
            return proc
        else:
            raise NoConnectionError(message='Connection times out. Please check if Wifi is connected.')

    def __sit__(self):
        def sit_fun(): return get_ssh_connection().run(COMMAND_SIT, pty=True, watchers=[self._sudopass])
        if not self._sit_process.is_alive():
            self._sit_process = Process(target=sit_fun)
            self._sit_process.start()

    def __stand__(self):
        if self._sit_process.is_alive():
            self._sit_process.terminate()

    def __exec_comnd__(self, command):
        if command == COMMAND_SIT:
            self.__sit__()
        elif command == COMMAND_STAND:
            self.__stand__()
        else:
            self.__stand__()
            sleep(2)
            get_ssh_connection().run(command, pty=True, watchers=[self._sudopass])
            sleep(1)
            self.__sit__()
        sys.exit()

    def __start_listener__(self):
        listener = get_conn_listener(COMMAND_PORT)
        while True:
            con = listener.accept()
            msg = con.recv()
            if not self._cmd_thread.is_alive():
                self._cmd_thread = Thread(target=self.__exec_comnd__, args=(msg,), deamon=True)
                self._cmd_thread.start()


def execute_command(command):
    con = get_conn_client(COMMAND_PORT)
    con.send(command)
    con.close()


def commandexec_stop():
    for proc in _procs:
        proc.terminate()


class NoConnectionError(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message
