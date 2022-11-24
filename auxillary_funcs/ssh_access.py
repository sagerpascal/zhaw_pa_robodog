from invoke import Responder
from fabric import Connection, Config
from time import sleep
import multiprocessing


COMMAND_SIT = 'sudo ./sit.sh'
COMMAND_WALK = 'sudo ./walk.sh'

_process = None

_sudopass = Responder(
    pattern=r'\[sudo\] password for unitree:',
    response='123\n')

commands_dict = {
    'sit': COMMAND_SIT,
    'walk': COMMAND_WALK,
}


def get_ssh_connection():
    c = Connection(host='192.168.123.12', user='unitree', connect_kwargs={"password": "123"})
    return c


def sit():
    global _process
    _process = multiprocessing.Process(target=lambda: get_ssh_connection().run(
        COMMAND_SIT, pty=True, watchers=[_sudopass]))
    _process.start()


def execute_command(connection, command):
    global _process
    _process.terminate()
    sleep(2)
    connection.run(command, pty=True, watchers=[_sudopass])
    sleep(2)
    _process = multiprocessing.Process(target=execute_command, args=(get_ssh_connection(), "walk"))
    _process.start()


def switch(cmd):
    # TODO: switch with class Command later.
    if cmd == 'walk':
        return 'sudo ./walk.sh'
    if cmd == 'dance1':
        return 'sudo ./dance1.sh'
