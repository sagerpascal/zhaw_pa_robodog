from invoke import Responder
from fabric import Connection, Config
from time import sleep
import multiprocessing

process = None


def pull_up(func):
    def wrapped_func(*args, **kwargs):
        global process
        process.terminate()
        sleep(2)
        func(*args, **kwargs)
        sleep(2)
        process = multiprocessing.Process(target=execute_command, args=(ssh_connect(), "walk"))
        process.start()
    return wrapped_func


sudopass = Responder(
    pattern=r'\[sudo\] password for unitree:',
    response='123\n')


def ssh_connect():
    c = Connection(host='192.168.123.12', user='unitree', connect_kwargs={"password": "123"})
    return c


def execute_command(connection, command):
    cmd = switch(command)
    connection.run(cmd, pty=True, watchers=[sudopass])

@pull_up
def play_dead():
    print('bla')

def switch(cmd):
    # TODO: switch with class Command later.
    if cmd == 'walk':
        return 'sudo ./walk.sh'
    if cmd == 'dance1':
        return 'sudo ./dance1.sh'


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
