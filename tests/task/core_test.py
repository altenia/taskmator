import unittest
import logging
from taskmator.task import core, factory, util;
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

    def testCommandLineTask(self):
        rootTask = core.CompositeTask("root", None)
        pgreptask = util.CommandLineTask("echo_hello", rootTask)
        params = {"message":"Hello", "command": "echo \"${message}\""}
        pgreptask.setParams(params)

        pgreptask = util.CommandLineTask("echo_append", rootTask)
        params = {"prevmessage":"$root.echo_hello.outcome_result", "command": "echo \"${prevmessage} Task\""}
        pgreptask.setParams(params)

        rootTask.execute()
        code, result = rootTask.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")
        self.assertEqual(result, "Hello World\n", "Outcome result does not match")
        print("Result: \""+result + "\"")

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
