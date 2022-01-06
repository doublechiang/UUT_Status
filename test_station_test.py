import unittest

from test_station import TestStation

class TestStationTest(unittest.TestCase):
    def testSync(self):
        # rsync test station files and create locally under data folder.
        TestStation('root@192.168.0.83').sync()


if __name__ == '__main__':
    unittest.main()