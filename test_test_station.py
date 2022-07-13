import unittest
from app import test_station

import settings
from test_station import TestStation

class TestStationTest(unittest.TestCase):
    def setUp(self) -> None:
        settings.tss = [
            { 'ts' : 'log:log@192.168.66.66', 'prjs' : [ 'T6UB'] },
            { 'ts' : 'log:log@192.168.0.83', 'prjs' : [ 'T6UB', 'RMK_I'] }
        ]
        return super().setUp()
    def tearDown(self) -> None:
        return super().tearDown()

    def testSync(self):
        # rsync test station files and create locally under data folder.
        # TestStation('root@192.168.0.83').sync()
        pass

    def testInit(self):
        """ When initialize the with the preconfigured setting, it should parse the member
        """
        ts = TestStation('log@192.168.0.83')
        self.assertEqual(ts.getHost(), '192.168.0.83')
        self.assertEqual(ts.getHostLogin(), 'log')
        self.assertEqual(ts.passw, 'log')

    def test_models(self):
        # we have settings file, and
        ts = TestStation('192.168.0.83')
        models = ts.models
        self.assertEqual(len(models), 2)
        for m in models:
            self.assertTrue(m, TestStation.Model)

        # use count() to check the model exist in the models
        all_models = list(map(str, models))
        self.assertGreater(all_models.count('RMK_I'), 0)
        self.assertGreater(all_models.count('T6UB'), 0)

if __name__ == '__main__':
    unittest.main()