#!/usr/bin/python
import paramiko
import os
privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('espux055nfs', username = 'root', pkey = mykey)
stdin, stdout, stderr = ssh.exec_command('grep root /etc/shadow')
print stdout.readlines()
ssh.close()
