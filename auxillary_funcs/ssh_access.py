from invoke import Responder
from fabric import Connection, Config
from time import sleep
import multiprocessing

sudopass = Responder(
    pattern=r'\[sudo\] password for unitree:',
    response='123\n')


def ssh_connect():
    c = Connection(host='192.168.123.12', user='unitree', connect_kwargs={"password": "123"})
    return c


def execute_command(connection, command):
    cmd = switch(command)
    connection.run(cmd, pty=True, watchers=[sudopass])


def switch(cmd):
    # TODO: switch with class Command later.
    if cmd == 'walk':
        return 'sudo ./walk.sh'
    if cmd == 'dance1':
        return 'ls'


# TODO: run "sit" command seperately in a  loop
c = ssh_connect()
process = multiprocessing.Process(target=execute_command, args=(c, "walk"))
process.start()

# TODO; implement while loop with global variable
sleep(10)
process.terminate()


class Command:
    def __init__(self, cmd, duration):
        self.cmd = cmd
        self.duration = duration
