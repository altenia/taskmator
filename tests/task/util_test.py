import unittest
from testbase import TaskmatorTestBase
from taskmator.task import core, util
from taskmator import context

class UtilTest(TaskmatorTestBase):

    @unittest.skip("Skipping testCommandLineTask")
    def testCommandLineTask(self):
        """
        Tests that echo command is executed and results no error code
        """
        task_container = context.TaskContainer(None)
        exec_context = context.ExecutionContext(task_container)

        task = util.CommandLineTask("cmd", None)
        params = {"message":"Hello World", "command": "echo \"${message}\""}
        task.setParams(params)
        paramVal = task.getParam("command")
        self.assertEqual(paramVal, "echo \"Hello World\"", "Param does not match")
        task.execute(exec_context)
        code, output = task.getOutcome()
        self.assertEqual(code, 0, "Outcome Code is not 0")
        self.assertEqual(output, "Hello World", "Outcome result does not match")
        print("Result: \""+output + "\"")

    #@unittest.skip("Skipping testOutputReportTask")
    def testOutputReportTask(self):
        """
        Tests that a composite task containing two command line tasks and an
        output report tasks displays the output report accordingly.
        """
        task_container = context.TaskContainer(None)
        exec_context = context.ExecutionContext(task_container)

        rootTask = core.CompositeTask("root", None)
        task_container.task_root = rootTask
        rootTask._exec = ['t1', 't2', 'output']
        task1 = util.CommandLineTask("t1", rootTask)
        params = {"message":"T1", "command": "echo \"${message} output\""}
        task1.setParams(params)

        task2 = util.CommandLineTask("t2", rootTask)
        params = {"message":"T2", "command": "echo \"${message} output\""}
        task2.setParams(params)

        taskOutRep = util.OutputReportTask("output", rootTask)
        params = {"stream":"console", "format":"[${type}] ${name} (${outcome_code}) ${outcome_result}"}
        taskOutRep.setParams(params)

        rootTask.execute(exec_context)
        code, output = rootTask.getOutcome()
        print (code)
        #self.assertEqual(code, 0, "Outcome Code is not 0")

    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
