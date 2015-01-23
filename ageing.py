#!/usr/bin/python
import paramiko
import os
import sys
import time
import re


if(len(sys.argv) > 1): 
    str_filter = sys.argv[1]
else:
    str_filter = "okada"


if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
    host_file = os.path.expanduser('D:\Repositorio\claves\hosts')
    key_file = os.path.expanduser('D:\Repositorio\claves\id_rsa')
else:
    host_file = os.path.expanduser('/etc/hosts')
    key_file = os.path.expanduser('~/.ssh/id_rsa')

user = "root"
warn_days = 7

def connect_ssh_key(hostname, hostip, user, keyfile):
    
    privatekeyfile = os.path.expanduser(keyfile)
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostip, username = user, pkey = mykey)
    except paramiko.SSHException:
        print hostname+':ssh negotiation failed'
        return 1
    except Exception:
        print hostname+':connect failed'
        return 1
    
    stdin, stdout, stderr = ssh.exec_command('grep root /etc/shadow')
    
    if stderr.readline(): return 1   
    
    salida=stdout.readline()

    if not salida.split(':')[4] or not salida.split(':')[2]:
        print hostname+":not expire"
        return 0   
    
    set_epoch=int(salida.split(':')[2])
    days=int(salida.split(':')[4])
    exp_epoch=set_epoch+days
    exp_time=time.strftime("%a %d %b %Y",time.localtime(exp_epoch*24*60*60))
  
       
    if days==99999 or days==-1:
        print hostname+":not expire"
        hosts_ageing[hostname] = 99999
    else:
        hosts_ageing[hostname] = exp_epoch
        print hostname+":expire in " + str(exp_epoch - curr_epoch) + " days, at " + exp_time
   
    ssh.close()



# Main

curr_epoch=int(time.mktime(time.localtime())/(24*60*60))
hosts_ageing = {}   


f = open(host_file, "r")

print ""
print "=== status ==="
print ""

while True:

    line = f.readline()

    if not line: break
    
    if re.search(str_filter, line):
        hostname = line.split()[1]
        hostip = line.split()[0]
        connect_ssh_key (hostname, hostip, user, key_file)
    
f.close()


print ""
print "=== list of hosts which password expiration is due to expire in " + str(warn_days) + " days ==="
print ""

for  k, v in hosts_ageing.iteritems():     
        if v - curr_epoch < warn_days:
            exp_time=time.strftime("%a %d %b %Y",time.localtime(v*24*60*60))
            print k+":expire in " + str(v - curr_epoch) + " days, at " + exp_time             

print ""               
