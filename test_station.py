#!/usr/bin/env python3

from distutils.log import error
import os
import logging
import datetime
import base64
import subprocess
import time

from uut import Uut
from iscdhcpleases import Lease, IscDhcpLeases
import tm
import settings
from rack import Rack

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
    def getBase64(str):
        return base64.b64encode(str.encode()).decode('utf-8')


    def __sync_prj(self, prj):
        # create local test station data folder
        local_folder = os.path.join(TestStation.data_path, self.getHost(), tm.TestMonitor.getConfigPath(prj))
        logging.info("sync local folder :{}".format(local_folder))
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)

        # Get config files
        fn = os.path.join('/', tm.TestMonitor.getConfigPath(prj), '*.txt')
        cmd = "rsync --timeout=2 -a --delete {}:{} {}".format(self.hostn, fn, local_folder)
        if settings.hop_station is not None:
            cmd = "rsync --timeout=2 -ae --delete 'ssh -A -J {}' {}:{} {}".format(settings.hop_station, self.hostn, fn, local_folder)
        logging.info(cmd)
        os.system(cmd)

    def sync(self):
        """ 
            rsync the teststation response files and dhcp lease file
            Since client can call sync frequently, if called within 300 seconds, it will not execute.
            return True if sync performed, False is not sync
        """

        # Do not sync when in development mode, but we need to rebulid the directory
        if 'development' == os.getenv('FLASK_ENV'):
            logging.debug("Development mode, do not sync the Test station data")
            return True

        for m in self.models:
            logging.info(f'Syncing {m} in {self}')
            self.__sync_prj(str(m))

        now = datetime.datetime.now()
        if self.last_sync is not None:
            time_diff = now - self.last_sync
            if time_diff.seconds < TestStation.SYNC_INTERVAL_SECS:
                logging.debug("Sync call within SYNC_INTERVAL_SECS, ignored")
                return False
            
        self.last_sync = now

        # get dhcpd leases
        local_folder = os.path.join(TestStation.data_path, self.getHost(), './var/lib/dhcpd/')
        if os.path.exists(local_folder) is False:
            os.makedirs(local_folder)
        cmd = "rsync --timeout=2 {}:{} {}".format(self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        if settings.hop_station is not None:
            cmd = "rsync --timeout=2 -e 'ssh -A -J {}' {}:{} {}".format(settings.hop_station, self.hostn, "/var/lib/dhcpd/dhcpd.leases", local_folder)
        logging.info(cmd)
        os.system(cmd)
        return True
      

    def sync_scan(self, prjs):
        # Sync this station based on configuration.
        if self.sync():
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
            return the uut based on mbsn or product sn
        """
        uut = self.uuts.get(sn)
        # if can't find in mbsn, then search in chassis sn
        if uut == None:
            uut = self.uuts_keypsn.get(sn)
        if uut == None:
            uut = self.uuts_keysn.get(sn)

        # logging.debug("Return SN {}, UUT {}".format(sn, uut))
        return uut



    def getRackFactory(self):
        """
            A Test station handle multiple Racks.
        """        
        return self.racks

    def getHost(self):
        return self.hostn.split('@')[1]

    def getHostLogin(self):
        return self.hostn.split('@')[0]

    def getHostPassBase64(self):
        coded = self.getBase64(self.passw)
        # logging.debug("passwd {}, base64 coded {}".format(self.passw, coded))
        return coded


    def scanPrjConfig(self, prj=None):
        # if prj input is None, then we will scan all project defined.
        if prj == None:
            for p in self.models:
                self.scanPrjConfig(p)
            return 

        # For each project (model), build 
        cksum = prj.getDirSum()
        if cksum != prj.cksum:
            logging.debug("Integration Dirty: previous {}, current {}, prj {}, host {} ,Building UUT instance".format(prj.cksum, cksum, prj, self.getHost()))
            path = os.path.join(TestStation.data_path, self.getHost(), tm.TestMonitor.getConfigPath(prj))
            path = os.path.join(path, '')               # Add the appendix / if not

            uuts = {}
            with os.scandir(path) as it:
                # filter the file older than 4 weeks ( 60 sec * 60 min * 24 hour * 7 days * 4 weeks)
                filter_time = int(round(time.time())) - (60*60*24*7*4)
                scanned_mtime = None
                for entry in it:
                    mtime = int(round(entry.stat().st_mtime))
                    if scanned_mtime is None:
                        scanned_mtime = mtime
                    else:
                        if scanned_mtime < mtime:
                            scanned_mtime = mtime

                    # If the file already older than 4 weeks, ignore it.
                    if mtime < filter_time:
                        continue

                    # if the scanned file less the last scanned mtime, also skip that.
                    if mtime < prj.mtime:
                        continue

                    ext = os.path.splitext(entry.name)[-1].lower()
                    if ext == ".txt":
                        # logging.debug("Processing file {}".format(f))
                        uut = Uut.parse_file(path + entry.name)
                        if uut is not None:
                            uut.ts = self
                            key=uut.mlbsn
                            uuts[key]=uut

            # Update the most scanned file time.
            prj.mtime = scanned_mtime
            logging.info("Prj {} host {} was processed, total {} config files.".format(prj, self.getHost(), len(uuts)))
            self.uuts.update(uuts)
            self.uuts_keysn.update(self.__genUutKeyChassisSn(uuts))
            self.uuts_keypsn.update(self.__genUutKeyProductSn(uuts))
            self.racks = self.__genRackDict(uuts)
            prj.cksum = cksum
        else:
            logging.info(f'directory checksum matching, skip scan for {prj} on {self.getHost()}')

        return
    
    @property
    def ip(self):
        return self.hostn.split('@')[1]

    @property
    def user(self):
        return self.hostn.split('@')[0]

    def __genUutKeyChassisSn(self, uuts):
        uuts_keySn = {}
        for u in uuts.values():
            uuts_keySn[u.chassissn] = u
        return uuts_keySn

    def __genUutKeyProductSn(self, uuts):
        uuts_keySn = {}
        for u in uuts.values():
            uuts_keySn[u.csn] = u
        return uuts_keySn


    def __genRackDict(self, uuts):
        rack_uut_dict = {}
        for u in uuts.values():
            rsn = u.racksn
            rack = rack_uut_dict.get(rsn)
            if rack is None:
                rack = Rack(rsn)
                rack.rmac = u.rack_mount_mac1
                rack.ts = self
                rack_uut_dict[rsn] = rack
            if rack.rmac != u.rack_mount_mac1 or rack.rsn != u.racksn:
                logging.error("Rack SN MAC doesn't match, configuration file error!")
            rack.appendUut(u)
        return rack_uut_dict
       

    def __repr__(self):
        return self.hostn
        
    def __init__(self, **kwargs):
        # use hostname root@192.168.0.83 as the host identifier
        logging.basicConfig(level=logging.INFO)
        self.models = []
        for k, v in kwargs.items():
            if k == 'ts':
                s = v.split('@')[1]
                cred = v.split('@')[0]
                user= cred.split(':')[0]
                self.passw = cred.split(':')[1] 
                self.hostn = f'{user}@{s}'
            if k == 'prjs':
                for m in v:
                    model = self.Model(self, m)
                    self.models.append(model)
                
        self.last_sync = None
        # index of racks
        self.racks = None
        # all uuts dict based on mbsn
        self.uuts = {}
        # all uuts dict based on sn
        self.uuts_keysn = {}                # key chassissn
        self.uuts_keypsn = {}               # key product SN



    class Model:
        """" Every TS include can has multiple Models
        """
        def getDirSum(self):
            """ Get a directory Checksum by using 'ls -l | cksum'
            """
            path = os.path.join(TestStation.data_path, self.ts.getHost(), tm.TestMonitor.getConfigPath(self.name))
            cmd = "ls -l {} | cksum ".format(path)
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            cksum= result.split()[0]
            return str(cksum)

        def __init__(self, ts, model):
            self.name = model
            self.ts = ts
            self.cksum = None
            # When application start, it set the filter date, and update the most updated mtime everyscan.
            # filter the file older than 4 weeks ( 60 sec * 60 min * 24 hour * 7 days * 4 weeks)
            self.mtime = int(round(time.time())) - (60*60*24*7*4)

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name


if __name__ == '__main__':
    x = TestStation('log@192.168.0.210')
    pass
    
