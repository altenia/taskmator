import unittest
from testbase import TaskmatorTestBase
from taskmator.task import core, util
from taskmator import context

class CoreTest(TaskmatorTestBase):

    #@unittest.skip("Skipping Namespace")
    def testNamespace(self):
        fac = context.TaskFactory()
        taskTypeName = "core.Composite"
        root = fac.instantiate(taskTypeName, "root", None)
        l1 = fac.instantiate(taskTypeName, "l1", root)
        l2a = fac.instantiate(taskTypeName, "l2a", l1)
        l2b = fac.instantiate(taskTypeName, "l2b", l1)
        
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
        task_container = context.TaskContainer(None)
        exec_context = context.ExecutionContext(task_container)

        rootTask = core.CompositeTask("root", None)
        task_container.task_root = rootTask
        rootTask._exec = ['echo_hello', 'echo_append']
        task1 = util.CommandLineTask("echo_hello", rootTask)
        params = {"message":"Hello", "command": "echo \"${message}\""}
        task1.setParams(params)

        task2 = util.CommandLineTask("echo_append", rootTask)
        params = {"command": "echo \"${root.echo_hello.outcome_result} Task\""}
        task2.setParams(params)

        rootTask.execute(exec_context)

        traces = exec_context.traces()
        #for trace in traces:
        #    print (trace)

        self.assertEqual(len(traces), 3, "Three execution trace entries")
        self.assertEqual(traces[0]['output'], "Hello", "Outcome result does not match")
        self.assertEqual(traces[1]['output'], "Hello Task", "Outcome result does not match")

    #@unittest.skip("Skipping OutputPassing")
    def testPrecond(self):
        """
        Tests that tasks are correctly executed or skipped based
        on the evaluation of the preconditions
        """
        task_container = context.TaskContainer(None)
        exec_context = context.ExecutionContext(task_container)

        task1 = core.EchoTask("echo_hello", None)
        params = {"message": "This is test"}
        task1.setParams(params)
        code, output = task1.execute(exec_context)
        self.assertEqual(code, core.Task.CODE_OK, "Outcome Code is not " + str(core.Task.CODE_OK))

        task1.precond = "'${message}' == 'This is test'"
        task1.execute(exec_context)
        code, output = task1.execute(exec_context)
        self.assertEqual(code, core.Task.CODE_OK, "Outcome Code is not " + str(core.Task.CODE_OK))

        task1.precond = "'${message}' == 'This is another test'"
        task1.execute(exec_context)
        code, output = task1.execute(exec_context)
        self.assertEqual(code, core.Task.CODE_SKIPPED, "Outcome Code is not " + str(core.Task.CODE_SKIPPED))


    def main():
        unittest.main()


if __name__ == '__main__':
    unittest.main()
