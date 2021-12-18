#!/usr/bin/python
from iscdhcpleases import Lease, IscDhcpLeases
leases=IscDhcpLeases('/var/lib/dhcpd/dhcpd.leases')
cur = leases.get_current()
for l in cur:
    lease = cur[l]
    print("{0}, {1}".format(l, lease.ip))
