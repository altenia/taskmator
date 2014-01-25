__author__ = 'ysahn'
import os
import unittest
import logging


class TaskmatorTestBase(unittest.TestCase):

    TEST_SPEC_PATH = "../data/sample1.task.json"

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger("taskmator")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)

    def setUp(self):
        self.test_spec_uri = os.path.join(os.path.dirname(__file__), self.TEST_SPEC_PATH)
