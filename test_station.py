#!/usr/bin/env python3

import os
import logging

from uut import Uut
from iscdhcpleases import Lease, IscDhcpLeases

class TestStation:
    """ A test station include the DHCP server response file.
    """

    data_path = "data/"

    # remote path and local path
    data_files = {
        'RPATH' : '/WIN/RMK_I/response/config/*.txt',
        'LPATH' : 'WIN/RMK_I/response/config'
    }
    

    def sync(self, hop= None):
        """ rsync the teststation response files and dhcp lease file
        """

        # Do not sync when in development mode
        if 'development' == os.getenv('FLASK_ENV'):
            logging.debug("Development mode, do not sync the Test station data")
            return 

        ts_data = os.path.join(TestStation.data_path, self.hostn)
        if os.path.exists(ts_data) is False:
            os.makedirs(ts_data)


        # Get config files
        fn = TestStation.data_files.get('RPATH')
        local_folder = os.path.join(TestStation.data_path, self.hostn, TestStation.data_files.get('LPATH'))
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync -v {}:{} {}".format(self.hostn, fn, local_folder)
        if hop is not None:
            cmd = "rsync -ve 'ssh -A -J {}' {}:{} {}".format(hop, self.hostn, fn, local_folder)
        logging.info(cmd)
        os.system(cmd)

        # get dhcpd leases
        local_folder = os.path.join(TestStation.data_path, self.hostn, './var/lib/dhcpd/')
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync -v {}:{} {}".format(self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        if hop is not None:
            cmd = "rsync -ve 'ssh -A -J {}' {}:{} {}".format(hop, self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        logging.info(cmd)
        os.system(cmd)
      

    @staticmethod
    def to_macstr(mac):
        if ',' in mac:
            mac = mac.split(',')[0]
            return TestStation.to_macstr(mac)
        elif mac.find(':') == -1:
            result = []
            for i in range(0, len(mac), 2):
                result.append(mac[i:i+2])
            return ':'.join(result).lower()
        else:
            return mac


    def getLeaseIp(self, mac):
        """ Based on the input mac, return the leased ip. 
            the mac could be "aa:bb:cc:dd:ee:ff" or 
            "123456789abc" or 
            "123456789abc,<model>,<speed> format
            return none if nothing found.
        """
        mac = self.to_macstr(mac)
        leasef = os.path.join(TestStation.data_path, self.hostn, './var/lib/dhcpd/dhcpd.leases')
        leases=IscDhcpLeases(leasef)
        cur = leases.get_current()
        # for l in cur:
        #     lease = cur[l]
        #     print("{0}, {1}".format(l, lease.ip))
        lease = cur.get(mac)
        # print("mac:{}".format(mac))
        # print(lease)
        if lease is not None:
            logging.debug("mac:{}, ip {}".format(mac, lease.ip))
            return lease.ip
        return None


    def GetUutFacotry(self):
        local_folder = os.path.join(TestStation.data_path, self.hostn, TestStation.data_files.get('LPATH'))
        uuts = Uut.parse_dir(local_folder)
        logging.info("total {} uuts in the path {}".format(len(uuts), local_folder))
        for u in uuts:
            # bmcip = self.getLeaseIp(u.bmcmac)
            pass 
        return uuts


    def getRackFactory(self):
        """
            A Test station handle multiple Racks.
            return a dictionary contain the Rack parsed information

            Scan all response files and retrieve the Rack SN and RM MAC.
        """
        rack={}
        racks = {}
        uuts = self.GetUutFacotry()
        for u in uuts:
            rsn = u.racksn
            rmac = u.rack_mount_mac1
            racks[rsn] = {'rmac':rmac, 'rsn': rsn, 'ts': self}
        return list(racks.values())
            

    def __init__(self, host):
        # use hostname root@192.168.0.83 as the host identifier
        logging.basicConfig(level=logging.INFO)
        self.hostn = host


    
