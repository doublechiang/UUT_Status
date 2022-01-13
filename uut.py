#!/usr/bin/env python3
import os
import configparser

class Uut:
    """
        Unit under test class
    """
    @staticmethod
    def parse_file(fname):
        """ return dictionary of the config file.
        """
        uut_dict = {}
        cfg_parser = configparser.RawConfigParser()
        with open(fname) as stream:
            stream = "[dummy]\n" + stream.read()

        cfg_parser.read_string(stream)
        # below line get single attribute    
        # mac = cfg_parser.get('dummy', 'BMCMAC')

        uut_dict = {k:v for k, v in cfg_parser['dummy'].items()}

        # create instance based on the dictionary so that we can access it under attribute.
        # return Uut(uut_dict)
        return uut_dict
   

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
                uuts.append(Uut(uut))
        return uuts

    @staticmethod
    def str_to_mac(str):
        """ Add the semi column into string and return the mac format
        """
        result = []
        for i in range(0, len(str), 2):
            result.append(str[i:i+2])
        return ':'.join(result).lower()


    def __init__(self, d):
        self.__dict__ = d    

if __name__ == '__main__':
    # print(vars(Uut.parse_file('./samples/WIN/Response/P81251401000101E.txt')))
    uuts = Uut.parse_dir('samples/WIN/Response')
    for u in uuts:
        print(u.str_to_mac(u.bmcmac))

