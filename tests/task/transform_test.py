import unittest
from testbase import TaskmatorTestBase
from taskmator.task import core, text
from taskmator import manager

class TransformTest(TaskmatorTestBase):

    #@unittest.skip("Skipping testTransform")
    def testTransform(self):
        """
        Tests that echo command is executed and results no error code
        """
        tmanager = manager.TaskManager()
        context = tmanager.start_task(self.get_data_path('codegen.task.json'))
        traces = context.traces()

        for trace in traces:
            print (str(trace))


if __name__ == '__main__':
    unittest.main()
