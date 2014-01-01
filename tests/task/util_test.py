import unittest
import logging
from taskmator.task.util import CommandLineTask

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
        task = CommandLineTask("cmd", None)
        params = {"message":"Hello World", "command": "echo \"${message}\""}
        task.setParams(params)
        paramVal = task.getParam("command")
        self.assertEqual(paramVal, "echo \"Hello World\"", "Param does not match")
        task.execute()
        code, result = task.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")
        self.assertEqual(result, "Hello World", "Outcome result does not match")
        print("Result: \""+result + "\"")

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
