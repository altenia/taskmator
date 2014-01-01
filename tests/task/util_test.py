import unittest
import logging
from taskmator.task import core, factory;
from taskmator import factory;
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

    def testNamespace(self):
        fac = factory.TaskFactory()
        taskTypeName = "taskmator.task.core.CompositeTask"
        root = fac.createTask(None, taskTypeName, "root")
        l1 = fac.createTask(root, taskTypeName, "l1")
        l2a = fac.createTask(l1, taskTypeName, "l2a")
        l2b = fac.createTask(l1, taskTypeName, "l2b")
        
        self.assertEqual(root.getNamespace(), "")
        self.assertEqual(root.getFqn(), "root")
        self.assertEqual(l2a.getNamespace(), "root.l1")

        self.assertEqual(l2a.getFqn(), "root.l1.l2a")

    @unittest.skip("testing testCommandLineTask")
    def testCommandLineTask(self):
        # make sure the shuffled sequence does not lose any elements
        task = core.CommandLineTask("CommandLIne", "ls", "List", {"command": "ls -la"})

        #task.execute();
        task.execute();
        
        #self.failUnless(IsOdd(1))
        self.assertEqual(0, task.execute());

    def testTaskFactory(self):
        # make sure the shuffled sequence does not lose any elements
        fac = factory.TaskFactory()
        rootTask = fac.loadRoot(self.ROOT_PATH + "tests/data/sample1.task.json")
        #rootTask.traverse()
        rootTask.execute()


    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
