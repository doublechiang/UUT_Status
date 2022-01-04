#!/usr/bin/env python3

import os

class TestStation:
    """ A test station include the DHCP server response file.
    """

    data_path = "./data/"
    data_files = {
        '/WIN/Response/*.txt' : './WIN/Response/',  
        "/var/lib/dhcpd/dhcpd.leases": './var/lib/dhcpd/'
    }

    def sync(self):
        """ rsync the teststation response files and dhcp lease file
        """
        ts_data = os.path.join(TestStation.data_path, self.hostn)
        if os.path.exists(ts_data) is False:
            os.makedirs(ts_data)

        for fn, folder in TestStation.data_files.items():
            local_folder = os.path.join(TestStation.data_path, folder)
            cmd = "rsync {}:{} {}".format(self.hostn, fn, folder)
            print(cmd)
#            os.system(cmd)

    def __init__(self, host):
        # use hostname root@192.168.0.83 as the host identifier
        self.hostn = host


    