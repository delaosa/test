#!/usr/bin/python

# First version by delaosa


import getopt
import sys
import shlex
import subprocess
import re
from datetime import date,timedelta,datetime
from time import strptime
from collections import defaultdict


def help():
    print sys.argv[0] + ' [ [-H hostname] [-s snapshot sufix (default: backup)] [-w warning threshold in hours since snapshot creation (default: 24)] [-c critical threshold in hours since snapshot creation (default: 48)]'
    sys.exit(2)

def main(argv):

    arg_hostname = ''
    arg_snapshotname = 'backup'
    arg_warning = '24'
    arg_critical = '48'
   
    try:
        opts, args = getopt.getopt(argv,"hH:s:w:c:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt == '-s':
            arg_snapshotname = arg
        elif opt == '-w':
            arg_warning = arg
        elif opt == '-c':
            arg_critical = arg
        elif opt == '-H':
            arg_hostname = arg


    if arg_critical <= arg_warning: help()

    cmd = 'for i in `/usr/sbin/zfs list -Ht snapshot|grep backup|cut -f1`; do /usr/sbin/zfs get -H creation $i;done'

    if arg_hostname:
        sshcommand = 'ssh -qx -o IdentityFile=/usr/local/nagios/.ssh/id_rsa_nagios -l root ' + arg_hostname
        cmd = sshcommand + ' \'' + cmd + '\''
    	p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
    else:	  
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       

    output,err = p1.communicate()

    snaplines = output.split('\n')
 
    snapshots = defaultdict(dict)
    
    for snapline in snaplines[0:-1]:
   
        snaplist = snapline.split()        
	timelist=snaplist[5].split(':')
        snapshots[snaplist[0]] = datetime(int(snaplist[6]),strptime(snaplist[3],'%b').tm_mon,int(snaplist[4]),int(timelist[0]),int(timelist[1]))


    alarmlist = []
    alarmcat = ''

    for k, v in snapshots.items():
                   
        if datetime.today() > v + timedelta(hours=int(arg_critical)):
        	alarmlist.insert(0,k + ':' + str(v))
		alarmcat = 'Critical'
        elif datetime.today() > v + timedelta(hours=int(arg_warning)):
		alarmlist.insert(0,k + ':' + str(v))
		alarmcat = 'Warning'
        else:
		alarmlist.append(k + ':' + str(v))

    if alarmcat == 'Warning':
    	print alarmcat + ' - ' + ', '.join(alarmlist)
	sys.exit(1)
    if alarmcat == 'Critical':
    	print alarmcat + ' - ' + ', '.join(alarmlist)
	sys.exit(2)
    else:
	if alarmlist:
		print "OK - " + ', '.join(alarmlist)
	else:
		print "OK"	
    	sys.exit(0)
    
if __name__ == "__main__":
    main(sys.argv[1:])
