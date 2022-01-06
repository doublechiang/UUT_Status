#!/usr/bin/env python3

import os
import logging

from uut import Uut
from iscdhcpleases import Lease, IscDhcpLeases

class TestStation:
    """ A test station include the DHCP server response file.
    """

    data_path = "data/"
    data_files = {
        'RPATH' : '/WIN/RMK_I/response/config/*.txt',
        'LPATH' : 'WIN/RMK_I/response/config'
    }
    

    def sync(self):
        """ rsync the teststation response files and dhcp lease file
        """
        ts_data = os.path.join(TestStation.data_path, self.hostn)
        if os.path.exists(ts_data) is False:
            os.makedirs(ts_data)


        # Get config files
        fn = TestStation.data_files.get('RPATH')
        local_folder = os.path.join(TestStation.data_path, self.hostn, TestStation.data_files.get('LPATH'))
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync {}:{} {}".format(self.hostn, fn, local_folder)
        logging.info(cmd)
        print(cmd)
        os.system(cmd)

        # get dhcpd leases
        local_folder = os.path.join(TestStation.data_path, self.hostn, './var/lib/dhcpd/')
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync {}:{} {}".format(self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        logging.info(cmd)
        print(cmd)
        os.system(cmd)
        

    def __convert_mac_str(self, mac):
        if ',' in mac:
            mac = mac.split(',')[0]
            return self.__convert_mac_str(mac)
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
        mac = self.__convert_mac_str(mac)
        leasef = os.path.join(TestStation.data_path, self.hostn, './var/lib/dhcpd/dhcpd.leases')
        leases=IscDhcpLeases(leasef)
        cur = leases.get_current()
        # for l in cur:
        #     lease = cur[l]
        #     print("{0}, {1}".format(l, lease.ip))
        lease = cur.get(mac)
        if lease is not None:
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

    def __init__(self, host):
        # use hostname root@192.168.0.83 as the host identifier
        self.hostn = host


    
