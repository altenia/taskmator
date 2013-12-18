import unittest
from taskmator.task import core, factory;
#import pudb; pu.db

class CoreTest(unittest.TestCase):

    def setUp(self):
        self.ROOT_PATH = "/Users/ysahn/workspace/tool/taskmator/"

    @unittest.skip("testing testCommandLineTask")
    def testCommandLineTask(self):
        # make sure the shuffled sequence does not lose any elements
        task = core.CommandLineTask("CommandLIne", "ls", "List", {"command": "ls -la"})
        
        #self.failUnless(IsOdd(1))
        self.assertEqual(0, task.execute());

    def testTaskFactory(self):
        # make sure the shuffled sequence does not lose any elements
        fac = factory.TaskFactory()
        task = fac.loadRoot(self.ROOT_PATH + "tests/data/sample1.task.json")

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
