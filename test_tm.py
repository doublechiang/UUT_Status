import unittest

import tm
import settings
import test_station

class TestTm(unittest.TestCase):

    def setUp(self) -> None:
        settings.tss = [
            { 'ts' : 'log:log@192.168.0.130', 'prjs' : [ 'T6UB'] }
        ]
        return super().setUp()
    def test_init(self):
        tss = tm.TestMonitor().pxes
        # from the test config file should include one ts and it's TestStation instance 
        self.assertEqual(len(tss), 1)
        ts = tss[0]
        self.assertTrue(isinstance(ts, test_station.TestStation))





