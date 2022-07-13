import os
import stat
import logging
import settings
import subprocess

import test_station

class TestMonitor:
    """ Main Test Monitor Configuratio settings.
    """
    __instance = None
    TUNNEL_PORT_START=50000
    TUNNEL_PORT_END=50100

    @staticmethod
    def getConfigPath(prj):
        return os.path.join('WIN', str(prj), 'response/config')

    @staticmethod
    def __getOccupiedPort():
        cmd = 'ss -ntulp4 | grep LISTEN'
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        occupied_port = []
        for line in output.decode('utf-8').splitlines():
            port = (line.strip()).split()[4].split(':')[1]
            occupied_port.append(int(port))
        return occupied_port


    def getFreeTunnelPort(self):
        occupied_port = TestMonitor.__getOccupiedPort()
        logging.debug("occupied_port:{}".format(occupied_port))
        free_port = None
        for port in range(TestMonitor.TUNNEL_PORT_START,TestMonitor.TUNNEL_PORT_END):
            if port in occupied_port:
                continue
            free_port =port
            break
        return free_port
     

    def __init__(self):
        # pxes contail a list of all the test station (pxe)
        self.pxes = []
        for p in settings.tss:
            ts = test_station.TestStation(**p)
            self.pxes.append(ts)

        logging.debug(f'All_Pxe info: {self.pxes}')

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super(TestMonitor, cls).__new__(cls)
        return cls.__instance

if __name__ == '__main__':
    tm = TestMonitor()
    print(tm.pxes)
    pass
    


