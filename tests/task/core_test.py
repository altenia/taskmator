import unittest
import logging
from taskmator.task import core, util
from taskmator import factory

class CoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        logger = logging.getLogger("taskmator")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)

    @unittest.skip("Skipping Namespace")
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

    #@unittest.skip("Skipping OutputPassing")
    def testOutputPassing(self):
        """
        Tests that in a composite task first task's output is used as input
        for the second task
        """
        rootTask = core.CompositeTask("root", None)
        task1 = util.CommandLineTask("echo_hello", rootTask)
        params = {"message":"Hello", "command": "echo \"${message}\""}
        task1.setParams(params)

        task2 = util.CommandLineTask("echo_append", rootTask)
        params = {"command": "echo \"${root.echo_hello.outcome_result} Task\""}
        task2.setParams(params)

        rootTask.execute()
        code, result = rootTask.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")
        self.assertEqual(result, "Hello Task", "Outcome result does not match")

    #@unittest.skip("Skipping OutputPassing")
    def testPrecond(self):
        """
        Tests that tasks are correctly executed or skipped based
        on the evaluation of the preconditions

        """
        task1 = core.EchoTask("echo_hello", None)
        params = {"message": "This is test"}
        task1.setParams(params)
        code = task1.execute()
        self.assertEqual(code, core.Task.CODE_OK, "Outcome Code is not " + str(core.Task.CODE_OK))

        task1.precond = "'${message}' == 'This is test'"
        task1.execute()
        code = task1.execute()
        self.assertEqual(code, core.Task.CODE_OK, "Outcome Code is not " + str(core.Task.CODE_OK))

        task1.precond = "'${message}' == 'This is another test'"
        task1.execute()
        code = task1.execute()
        self.assertEqual(code, core.Task.CODE_SKIPPED, "Outcome Code is not " + str(core.Task.CODE_SKIPPED))


    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
