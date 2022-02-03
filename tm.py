import os
import stat
import logging

class TestMonitor:

    """ Test Monitor Configuratio settings.
    """
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
            # supported_prjs = list(map(lambda x : Project(x), prjs.split(',')))
            supported_prjs = prjs.split(',')
        logging.debug("Supported Prj {}".format(supported_prjs))
        return supported_prjs

