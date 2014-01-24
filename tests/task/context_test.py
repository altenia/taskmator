import os
import unittest
import logging
from taskmator.manager import TaskManager
from taskmator.context import TaskContainer
from taskmator.task.core import CompositeTask

class CoreTest(unittest.TestCase):

    ROOT_PATH = "/Users/ysahn/workspace/tool/taskmator/"

    @classmethod
    def setUpClass(cls):

        logger = logging.getLogger("taskmator")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)


    # @unittest.skip("Skipping Namespace")
    def testContainer(self):
        test_spec_uri = os.path.join(os.path.dirname(__file__), '../data/sample1.task.json')
        tm = TaskManager()
        spec = tm.load_spec(test_spec_uri)
        task_container = TaskContainer(spec)
        task = task_container.get_task('root.prepare.create_user')
        self.assertIsNotNone(task)
        task = task_container.get_task('root.prepare.create_folders')
        self.assertIsNotNone(task)



    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
