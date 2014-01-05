import unittest
import logging
from taskmator.task import core, util

class CoreTest(unittest.TestCase):

    def setUp(self):
        self.ROOT_PATH = "/Users/ysahn/workspace/tool/taskmator/"

        logger = logging.getLogger("taskmator")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)

    def testCommandLineTask(self):
        task = util.CommandLineTask("cmd", None)
        params = {"message":"Hello World", "command": "echo \"${message}\""}
        task.setParams(params)
        paramVal = task.getParam("command")
        self.assertEqual(paramVal, "echo \"Hello World\"", "Param does not match")
        task.execute()
        code, result = task.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")
        self.assertEqual(result, "Hello World", "Outcome result does not match")
        print("Result: \""+result + "\"")

    #@unittest.skip("Skipping testOutputReportTask")
    def testOutputReportTask(self):
        rootTask = core.CompositeTask("root", None)
        task1 = util.CommandLineTask("t1", rootTask)
        params = {"message":"T1", "command": "echo \"${message} output\""}
        task1.setParams(params)

        task2 = util.CommandLineTask("t2", rootTask)
        params = {"message":"T2", "command": "echo \"${message} output\""}
        task2.setParams(params)

        taskOutRep = util.OutputReportTask("output", rootTask)
        params = {"stream":"console", "format":"[${type}] ${name} (${outcome_code}) ${outcome_result}"}
        taskOutRep.setParams(params)

        rootTask.execute()
        code, result = rootTask.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
