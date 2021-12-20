#!/bin/env python

import os
from ConfigParser import ConfigParser
from StringIO import StringIO
import commands
from iscdhcpleases import Lease, IscDhcpLeases

path = "/WIN/Response/"


def string_to_mac(str):
    """ Add the semi column into string and return the mac format
    """
    result = []
    for i in range(0, len(str), 2):
        result.append(str[i:i+2])
    return ':'.join(result)

def parse_file(fname):
    uuts = []
    uut = {}
    parser = ConfigParser()
    with open(path + fname) as stream:
        stream = StringIO("[dummy]\n" + stream.read())
        parser.readfp(stream)
    mac = parser.get('dummy', 'BMCMAC')
    mac = string_to_mac(mac)
    uut['bmc_mac'] = mac.lower()
    return uut
    

dir_list = os.listdir(path)
uuts = []
for f in dir_list:
    ext = os.path.splitext(f)[-1].lower()
    if ext == ".txt":
        uut = parse_file(f)
        uuts.append(uut)

leases = IscDhcpLeases('/var/lib/dhcpd/dhcpd.leases')
current=leases.get_current()

for u in uuts:
#    cmd = "arp -a | grep {0}".format(u.get('bmc_mac'))
#    out= commands.getoutput(cmd)
#    if len(out.split()) > 0:
#        ip = out.split()[1].replace('(', '').replace(')', '')
#        print(ip)
    lease=current.get(u.get('bmc_mac'))    
    print(lease.ip)
