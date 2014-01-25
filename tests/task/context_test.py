__author__ = 'ysahn'
import unittest

from testbase import TaskmatorTestBase
from taskmator.manager import TaskManager
from taskmator.context import TaskContainer

class ContextTest(TaskmatorTestBase):

    # @unittest.skip("Skipping Namespace")
    def testContainer(self):

        tm = TaskManager()
        spec = tm.load_spec(self.get_data_path(self.TEST_SPEC_NAME))
        task_container = TaskContainer(spec)
        task = task_container.get_task('root.prepare.create_user')
        self.assertIsNotNone(task)
        task = task_container.get_task('root.prepare.create_folders')
        self.assertIsNotNone(task)


    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
