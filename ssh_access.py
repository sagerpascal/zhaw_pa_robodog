import paramiko, re, time

command = "df"

# Update the next three lines with your
# server's information

host = "192.168.123.12"
username = "unitree"
password = "123"
command = "sudo ./walk.sh"

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)

channel = client.invoke_shell()
channel.send(command)
# wait for prompt
while not re.search(".*\[sudo\].*",channel.recv(1024)): time.sleep(1)
channel.send("%s\n" % password)

'''
_stdin, _stdout,_stderr = client.exec_command("df")
print(_stdout.read().decode())
client.close()
'''
