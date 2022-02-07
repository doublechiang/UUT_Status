#!/usr/bin/env python3

import os
import logging
import datetime
import base64
import subprocess

from uut import Uut
from iscdhcpleases import Lease, IscDhcpLeases
from rack import Rack
from tm import TestMonitor

class TestStation:
    """ A test station include the DHCP server response file.
    """

    data_path = "data/"
    SYNC_INTERVAL_SECS = 600

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

    @staticmethod
    def getTestStationFactory():
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

        tsl_list = []
        for s in all_pxe:
            ts = TestStation("{}@{}".format(s[1], s[0]))
            ts.passw = s[2]
            tsl_list.append(ts)
        return tsl_list

    @staticmethod
    def getBase64(str):
        return base64.b64encode(str.encode()).decode('utf-8')


    def __sync_prj(self, prj, hop=None):
        # create local test station data folder
        local_folder = os.path.join(TestStation.data_path, self.getHost(), TestMonitor.getConfigPath(prj))
        logging.info("sync local folder :{}".format(local_folder))
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)

        # Get config files
        fn = os.path.join('/', TestMonitor.getConfigPath(prj), '*.txt')
        cmd = "rsync -a {}:{} {}".format(self.hostn, fn, local_folder)
        if hop is not None:
            cmd = "rsync -ea 'ssh -A -J {}' {}:{} {}".format(hop, self.hostn, fn, local_folder)
        logging.info(cmd)
        os.system(cmd)

    def sync(self, prjs, hop= None):
        """ 
            rsync the teststation response files and dhcp lease file
            Since client can call sync frequently, if called within 300 seconds, it will not execute.
            return True if sync performed, False is not sync
        """

        # Do not sync when in development mode
        if 'development' == os.getenv('FLASK_ENV'):
            logging.debug("Development mode, do not sync the Test station data")
            return False

        now = datetime.datetime.now()
        if self.last_sync is not None:
            time_diff = now - self.last_sync
            if time_diff.seconds < TestStation.SYNC_INTERVAL_SECS:
                logging.debug("Sync call within SYNC_INTERVAL_SECS, ignored")
                return False
            
        self.last_sync = now

        for p in prjs:
            self.__sync_prj(p, hop)

        # get dhcpd leases
        local_folder = os.path.join(TestStation.data_path, self.getHost(), './var/lib/dhcpd/')
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync {}:{} {}".format(self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        if hop is not None:
            cmd = "rsync -e 'ssh -A -J {}' {}:{} {}".format(hop, self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        logging.info(cmd)
        os.system(cmd)
        return True
      

    def sync_scan(self, prjs):
        if self.sync(prjs):
            self.scanPrjConfig()

    def getLeaseIp(self, mac):
        """ Based on the input mac, return the leased ip. 
            the mac could be "aa:bb:cc:dd:ee:ff" or 
            "123456789abc" or 
            "123456789abc,<model>,<speed> format
            return none if nothing found.
        """
        mac = self.to_macstr(mac)
        leasef = os.path.join(TestStation.data_path, self.getHost(), './var/lib/dhcpd/dhcpd.leases')
        leases=IscDhcpLeases(leasef)
        cur = leases.get_current()
        lease = cur.get(mac)
        if lease is not None:
            # logging.debug("mac:{}, ip {}".format(mac, lease.ip))
            return lease.ip
        return None


    def GetUutFacotry(self, sn):
        """
            return the uut based on sn
        """
        uut = self.uuts.get(sn)
        if uut is not None:
            uut.ts =self

            # TODO: check if uut's RM got IP or not, we may need to filter it out.
            if self.getLeaseIp(uut.rack_mount_mac1) is None:
                pass

        # logging.debug("Return SN {}, UUT {}".format(sn, uut))
        return uut


        remove_list = []
        for u in uuts:
            u.ts = self
            # If the TS do not have a valid RM IP, do not put it in the list
            if self.getLeaseIp(u.rack_mount_mac1) is None:
                remove_list.append(u)

        for unit in remove_list:
            uuts.remove(unit)
        return uuts


    def getRackFactory(self, prj):
        """
            A Test station handle multiple Racks.
            Scan all response files and retrieve the list of Rack object
        """
        racks = {}
        uuts = self.GetUutFacotry()
        for u in uuts:
            rsn = u.racksn
            rmac = u.rack_mount_mac1
            r = racks.get(rsn)

            # if RM's MAC doesn't get an IP, just ignore it.
            if self.getLeaseIp(rmac) is None:
                continue

            if r is None:
                r = Rack(rsn)
                r.rmac = rmac
                r.rsn = rsn
                r.ts = self

            if r.rmac != rmac or r.rsn != rsn:
                logging.error("Response data Rack Manager doesn't match in files")
            r.uuts.append(u)
            racks[rsn] = r
            
        return list(racks.values())

    def getHost(self):
        return self.hostn.split('@')[1]

    def getHostLogin(self):
        return self.hostn.split('@')[0]

    def getHostPassBase64(self):
        coded = self.getBase64(self.passw)
        # logging.debug("passwd {}, base64 coded {}".format(self.passw, coded))
        return coded


    def __scanConfigDir(self, path):
        """ Scan the configuration and build the rack instance and UUT instance dict
        """
        uuts = {}
        path = os.path.join(path, '')               # Add the appendix / if not
        if os.path.exists(path) is False:
            return uuts

        dir_list = os.listdir(path)
        logging.info("Config Scaning {}".format(path))
        for f in dir_list:
            ext = os.path.splitext(f)[-1].lower()
            if ext == ".txt":
                # logging.debug("Processing file {}".format(f))
                uut = Uut.parse_file(path + f)
                if uut is not None:
                    key=uut.mlbsn
                    uuts[key]=uut
        return uuts

    def scanPrjConfig(self, prj=None):
        if prj == None:
            prjs = TestMonitor.getSupportedPrj()
            for p in prjs:
                self.scanPrjConfig(p)
            return 

        model = self.getModel(prj)
        cksum = model.getDirSum()
        if cksum != model.cksum:
            logging.debug("Integration Dirty: previous {}, current {}, prj {}, host {} ,Building UUT instance".format(model.cksum, cksum, prj, self.getHost()))
            path = os.path.join(TestStation.data_path, self.getHost(), TestMonitor.getConfigPath(prj))
            uuts = self.__scanConfigDir(path)
            logging.info("Prj {} host {} was processed, total {} config files.".format(prj, self.getHost(), len(uuts)))
            self.uuts.update(uuts)
            model.cksum = cksum
        return 
        
    def __initModel(self):
        prjs = TestMonitor.getSupportedPrj()
        return list(map(lambda x: self.Model(self, x), prjs))

    def getModel(self, prj):
        for m in self.models:
            if prj == str(m):
                return m
        return None

        
    def __init__(self, host):
        # use hostname root@192.168.0.83 as the host identifier
        logging.basicConfig(level=logging.INFO)
        self.hostn = host
        self.passw = None
        self.last_sync = None
        self.racks = None
        # all uuts dict based on keysn
        self.uuts = {}
        self.models = self.__initModel()



    class Model:
        """" Every TS include multiple Models
        """
        def getDirSum(self):
            """ Get a directory Checksum by using 'ls -l | cksum'
            """
            path = os.path.join(TestStation.data_path, self.ts.getHost(), TestMonitor.getConfigPath(self.name))
            cmd = "ls -l {} | cksum ".format(path)
            result = subprocess.check_output(cmd, shell=True)
            cksum= result.split()[0]
            return str(cksum)

        def __init__(self, ts, model):
            self.name = model
            self.ts = ts
            self.cksum = None

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.mode


if __name__ == '__main__':
    x = TestStation('log@192.168.0.210')
    pass
    
