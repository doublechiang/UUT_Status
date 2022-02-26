import os
import stat
import logging
import settings

class TestMonitor:
    """ Main Test Monitor Configuratio settings.
    """
    __instance = None
    ENV_PRJS='UUT_PRJS'
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
    


