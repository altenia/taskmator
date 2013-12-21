import unittest
import logging
from taskmator.task import core, factory;
#import pudb; pu.db

class CoreTest(unittest.TestCase):

    def setUp(self):
        self.ROOT_PATH = "/Users/ysahn/workspace/tool/taskmator/"

        logger = logging.getLogger("taskmator")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)

    @unittest.skip("testing testCommandLineTask")
    def testCommandLineTask(self):
        # make sure the shuffled sequence does not lose any elements
        task = core.CommandLineTask("CommandLIne", "ls", "List", {"command": "ls -la"})

        task.execute();
        
        #self.failUnless(IsOdd(1))
        self.assertEqual(0, task.execute());

    def testTaskFactory(self):
        # make sure the shuffled sequence does not lose any elements
        fac = factory.TaskFactory()
        task = fac.loadRoot(self.ROOT_PATH + "tests/data/sample1.task.json")
        task.traverse()

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
