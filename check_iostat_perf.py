
#!/usr/bin/python

# First version by delaosa
# v1.1 by delaosa

"""
linux:~# iostat -dxk
Linux 2.6.32-5-amd64 (esplx203)         12/12/2013      _x86_64_        (4 CPU)

Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
xvda              0.00     0.31    0.29    2.91     8.24    11.43    12.29     0.02    5.51   1.73   0.55


solaris# iostat -x
                 extended device statistics
device    r/s    w/s   kr/s   kw/s wait actv  svc_t  %w  %b
sd3       0.0    0.0    0.0    0.0  0.0  0.0   64.0   0   0
"""




import getopt
import sys
import shlex
import subprocess
import re
from collections import defaultdict


def help():
    print sys.argv[0] + ' -o "Linux|Solaris" [-H hostname] [-d "space separated list of disks"] [-s sample time(s)]'
    sys.exit(2)

def main(argv):

    arg_hostname = ''
    arg_disks = ''
    os = ''
    sampletime = 15

    try:
        opts, args = getopt.getopt(argv,"hH:d:o:s:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt == '-H':
            arg_hostname = arg
        elif opt == '-d':
            arg_disks = arg
        elif opt == '-o':
            os = arg
        elif opt == '-s':
            sampletime = arg


    if os not in ("solaris", "linux"):
        help()


    if os == 'solaris':
            cmd = 'iostat -x'
            rs = 1
            ws = 2
            krs = 3
            kws = 4
            svct = 7
            busy = 9
    else:
            cmd = 'iostat -dxk'
            rs = 3
            ws = 4
            krs = 5
            kws = 6
            svct = 9 # use wait insead of svctm
            busy = 11


    if arg_disks:
        cmd += ' ' + arg_disks +  ' ' + str(sampletime) + ' 2'
    else:
        cmd += ' ' + str(sampletime) + ' 2'


    if arg_hostname:
        sshcommand = 'ssh -qx -o IdentityFile=/usr/local/nagios/.ssh/id_rsa_nagios -l root ' + arg_hostname
        cmd = sshcommand + ' ' + cmd


    p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output,err = p1.communicate()

    iostat = output.split('\n')

    mark = 0

    disks = defaultdict(dict)


    for ioline in iostat[0:-1]:

            match = re.search('^[dD]evice', ioline)
            if mark > 1 and ioline:
                    iodisk = ioline.split()
                    disks[iodisk[0]]['rs'] = iodisk[rs]
                    disks[iodisk[0]]['ws'] = iodisk[ws]
                    disks[iodisk[0]]['krs'] = iodisk[krs]
                    disks[iodisk[0]]['kws'] = iodisk[kws]
                    disks[iodisk[0]]['svct'] = iodisk[svct]
                    disks[iodisk[0]]['busy'] = iodisk[busy]
            if match:
                    mark += 1

    perfdata = ''

    for disk in disks:
            for k, v in disks[disk].items():
                    #DG print disk +  ':' + k + '=' + str(v)
                    perfdata += disk + '_' + k + '=' + str(v) + ' '


    print "OK|" + perfdata
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
