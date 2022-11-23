from invoke import Responder
from fabric import Connection


def execute_command(command):
    c = Connection(host='192.168.123.12', user='unitree', connect_kwargs={"password": "123"})
    sudopass = Responder(
        pattern=r'\[sudo\] password:',
        response='123\n')
    c.run('sudo ./walk.sh', pty=True, watchers=[sudopass])


execute_command("walk")
