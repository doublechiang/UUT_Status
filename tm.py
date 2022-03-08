import os
import stat
import logging
import settings
import subprocess

class TestMonitor:
    """ Main Test Monitor Configuratio settings.
    """
    __instance = None
    ENV_PRJS='UUT_PRJS'
    TUNNEL_PORT_START=50000
    TUNNEL_PORT_END=50100

    @staticmethod
    def getConfigPath(prj):
        return os.path.join('WIN', str(prj), 'response/config')

    @staticmethod
    def getSupportedPrj():
        """
            Read OS environment and return the prject object in list
        """
        supported_prjs = []
        prjs = os.environ.get(TestMonitor.ENV_PRJS)
        if prjs is not None:
            # supportd_prjs = list(map(lambda x : Project(x), prjs.split(',')))
            supported_prjs = prjs.split(',')
        # logging.debug("Supported Prj {}".format(supported_prjs))
        return supported_prjs

    @staticmethod
    def getSettings():
        return settings

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
            return free_port
        return None
     

    def __readPXEs(self):
        """ Read UUT_SSHPASS environment to get the list of Instance of TS.
        """
        listing = os.environ.get('UUT_SSHPASS')
        if listing is None:
            logging.error("No UUT_SSHPASS defined in the environment, check README.md to define it.")
            return []

        all_pxe = []
        for s in listing.split(','):
            host = s.split('@')[1]
            userpass= s.split('@')[0]
            usern = userpass.split(':')[0]
            passw = userpass.split(':')[1]
            all_pxe.append((host, usern, passw))
        return all_pxe

    def __init__(self):
        self.pxes = self.__readPXEs()

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super(TestMonitor, cls).__new__(cls)
        return cls.__instance

if __name__ == '__main__':
    t1 = TestMonitor()
    t2 = TestMonitor()
    print(t1)
    print(t2)
    


