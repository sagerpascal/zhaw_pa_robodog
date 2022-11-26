from invoke import Responder
from time import sleep
from multiprocessing import Process
from threading import Thread
import sys

from auxillary_funcs.ssh_access import get_ssh_connection, check_connection, NoConnectionError
from auxillary_funcs.interprocess_comms import get_conn_listener, get_conn_client, COMMAND_PORT

COMMAND_SIT = 'sudo ./sit.sh'
COMMAND_STAND = 'sudo ./stand.sh'
COMMAND_WALK = 'sudo ./walk.sh'

_COMMAND_STOP = 'stop'

_sudopass = Responder(
    pattern=r'\[sudo\] password for unitree:',
    response='123\n')


class CommandExecutor():

    def __init__(self) -> None:
        self._sit_proc = None
        self._cmd_thrd = None

    def start(self):
        if check_connection():
            proc = Process(target=self.__start_listener__)
            proc.start()
            sleep(1)
            return proc
        else:
            raise NoConnectionError(message='Connection times out. Please check if Wifi is connected.')

    def __sit__(self):
        def sit_fun(): return get_ssh_connection().run(COMMAND_SIT, pty=True, watchers=[_sudopass])
        if self._sit_proc is None or not self._sit_proc.is_alive():
            self._sit_proc = Process(target=sit_fun)
            self._sit_proc.start()

    def __stand__(self):
        if self._sit_proc is not None and self._sit_proc.is_alive():
            self._sit_proc.terminate()

    def __exec_comnd__(self, command):
        if command == COMMAND_SIT:
            self.__sit__()
        elif command == COMMAND_STAND:
            self.__stand__()
        else:
            self.__stand__()
            sleep(2)
            get_ssh_connection().run(command, pty=True, watchers=[_sudopass])
            sleep(1)
            self.__sit__()
        sys.exit()

    def __start_listener__(self):
        listener = get_conn_listener(COMMAND_PORT)
        while True:
            con = listener.accept()
            msg = con.recv()
            if msg == _COMMAND_STOP:
                try:
                    self._cmd_thrd.terminate()
                finally:
                    sys.exit()
            if self._cmd_thrd is None or not self._cmd_thrd.is_alive():
                self._cmd_thrd = Thread(target=self.__exec_comnd__, args=(msg,))
                self._cmd_thrd.start()


def execute_command(command):
    con = get_conn_client(COMMAND_PORT)
    con.send(command)
    con.close()


def commandexec_stop():
    execute_command(_COMMAND_STOP)
