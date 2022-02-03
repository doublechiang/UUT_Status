#!/usr/bin/env python3
import os
import configparser
import logging

class Uut:
    """
        Unit under test class
    """
    @staticmethod
    def parse_file(fname):
        """ return an UUT instance
        """
        uut_dict = {}
        cfg_parser = configparser.RawConfigParser()
        with open(fname) as stream:
            stream = "[dummy]\n" + stream.read()


        try:
            cfg_parser.read_string(stream)
            # below line get single attribute    
            # mac = cfg_parser.get('dummy', 'BMCMAC')
        except:
            logging.error("Processsing file {} with exception!".format(fname))
            return None

        # if the txt file do not contain the [END] section, it's not a valid config file
        if 'END' not in cfg_parser.sections():
            logging.error("There is no [END] section in the config file.")
            return None

        uut_dict = {k:v for k, v in cfg_parser['dummy'].items()}

        # create instance based on the dictionary so that we can access it under attribute.
        return Uut(uut_dict)
   

    @staticmethod
    def parse_dir(path):
        """ Scan whole directory and return the list of UUT instance.
        """
        path = os.path.join(path, '')
        dir_list = os.listdir(path)
        uuts = []
        for f in dir_list:
            ext = os.path.splitext(f)[-1].lower()
            if ext == ".txt":
                uut = Uut.parse_file(path + f)
                uuts.append(uut)
        return uuts

    def __init__(self, d):
        logging.basicConfig(level=logging.DEBUG)
        self.__dict__ = d    
        self.ts = None

    @staticmethod
    def to_macstr(mac):
        if ',' in mac:
            mac = mac.split(',')[0]
            return Uut.to_macstr(mac)
        elif mac.find(':') == -1:
            result = []
            for i in range(0, len(mac), 2):
                result.append(mac[i:i+2])
            return ':'.join(result).lower()
        else:
            return mac



if __name__ == '__main__':
    # print(vars(Uut.parse_file('./samples/WIN/Response/P81251401000101E.txt')))
    uuts = Uut.parse_dir('samples/WIN/Response')
    for u in uuts:
        print(u.str_to_mac(u.bmcmac))

